#!/usr/bin/env python3
"""Cross-platform Source project lifecycle engine (stdlib only)."""

from __future__ import annotations

import argparse
from contextlib import contextmanager
import datetime as dt
import hashlib
import json
import os
import platform
import re
import shutil
import stat
import subprocess
import sys
import tempfile
import uuid
from pathlib import Path
from typing import Any, Iterable


ACTIONS = (
    "auto", "bootstrap", "init", "status", "next", "start", "finish",
    "doctor", "deploy-skills", "sync-dotfiles", "complete",
    "hub-init", "child-create", "hub-status", "hub-sync",
    "skills-check", "skills-update", "connector-bootstrap",
    "authority-check", "authority-lock", "authority-unlock", "authority-seal",
)
MANAGED_SKILLS = (
    "source", "project-init", "startup", "shutdown", "notion-conversation-log",
)
SENSITIVE = re.compile(
    r"(?i)(^|[\\/])(\.env(?:\..*)?|credentials[^\\/]*|id_rsa|id_ed25519|[^\\/]+\.(key|pem|pfx|p12))$"
)
WINDOWS_ABS = re.compile(r"(?i)(?<![A-Za-z0-9+.-])[A-Z]:[\\/]")
UNC_ABS = re.compile(r"(?<![\\])\\\\[^\\\s]+[\\/]")
POSIX_ABS = re.compile(r"(?<![:\w])/(?:Users|home|opt|private|var|tmp|etc|usr|Volumes)(?:/|\b)")

SCRIPT = Path(__file__).resolve()
SKILL_ROOT = SCRIPT.parent.parent
ASSET_ROOT = SKILL_ROOT / "assets"
DISTRIBUTION_ROOT = SKILL_ROOT.parent
DEFAULT_SKILL_REMOTE = "https://github.com/sink6985757-web/cross-device-agent-skills.git"

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


def now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def system_name() -> str:
    value = platform.system().lower()
    return {"darwin": "macos"}.get(value, value or "unknown")


def run(
    args: Iterable[str | Path], *, cwd: Path | None = None, check: bool = True,
    capture: bool = True,
) -> subprocess.CompletedProcess[str]:
    command = [str(item) for item in args]
    result = subprocess.run(
        command, cwd=str(cwd) if cwd else None, text=True, encoding="utf-8",
        errors="replace", capture_output=capture,
    )
    if check and result.returncode:
        detail = (result.stderr or result.stdout).strip()
        raise RuntimeError(f"Command failed ({command[0]}): {detail}")
    return result


def command_exists(name: str) -> bool:
    return shutil.which(name) is not None


def find_chezmoi() -> str | None:
    command = shutil.which("chezmoi")
    if command:
        return command
    if os.name == "nt":
        package_root = Path(os.environ.get("LOCALAPPDATA", "")) / "Microsoft" / "WinGet" / "Packages"
        if package_root.is_dir():
            for package in sorted(package_root.glob("twpayne.chezmoi*")):
                candidate = package / "chezmoi.exe"
                if candidate.is_file():
                    return str(candidate)
    return None


def resolve_root(start: str, for_init: bool = False) -> Path:
    root = Path(start).expanduser().resolve()
    if for_init:
        return root
    cursor = root if root.is_dir() else root.parent
    for candidate in (cursor, *cursor.parents):
        if (candidate / ".source" / "state.json").is_file():
            return candidate
    return root


def read_json(path: Path) -> Any:
    if not path.is_file():
        return None
    return json.loads(path.read_text(encoding="utf-8-sig"))


def sanitize_text(value: str, root: Path | None = None) -> str:
    result = value
    home = str(Path.home().resolve())
    if home:
        result = re.sub(re.escape(home), "~", result, flags=re.IGNORECASE if os.name == "nt" else 0)
        result = result.replace("~\\", "~/")
    if root:
        root_text = str(root.resolve())
        result = re.sub(re.escape(root_text), ".", result, flags=re.IGNORECASE if os.name == "nt" else 0)
    result = re.sub(r"(?i)(?<![A-Za-z0-9+.-])[A-Z]:[\\/][^;\r\n\"]*", "<runtime-path>", result)
    result = re.sub(r"(?<![\\])\\\\[^;\r\n\"]+", "<runtime-path>", result)
    result = re.sub(
        r"(?<![:\w])/(?:Users|home|opt|private|var|tmp|etc|usr|Volumes)/[^\s;,\"]+",
        "<runtime-path>", result,
    )
    return result


def portable(value: Any, root: Path | None = None) -> Any:
    if isinstance(value, dict):
        return {key: portable(item, root) for key, item in value.items()}
    if isinstance(value, list):
        return [portable(item, root) for item in value]
    if isinstance(value, str):
        return sanitize_text(value, root)
    return value


def write_text_atomic(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix=".tmp-", dir=str(path.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(text.rstrip() + "\n")
        os.replace(temp_name, path)
    finally:
        if os.path.exists(temp_name):
            os.unlink(temp_name)


def write_json_atomic(path: Path, value: Any, root: Path | None = None) -> None:
    write_text_atomic(path, json.dumps(portable(value, root), ensure_ascii=False, indent=2))


def parse_iso(value: str | None) -> dt.datetime | None:
    if not value:
        return None
    try:
        return dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def safe_relative(value: str, *, label: str = "path") -> str:
    candidate = Path(value.replace("\\", "/"))
    if candidate.is_absolute() or not candidate.parts or ".." in candidate.parts:
        raise RuntimeError(f"{label} must be a root-relative path without '..'")
    return candidate.as_posix()


def workspace_settings(config: dict[str, Any]) -> dict[str, Any]:
    defaults = {
        "role": "standalone", "hub_root": None, "child_root": "projects",
        "logs_root": "logs/sessions", "event_root": ".source/hub/events",
        "coordination_root": ".source/coordination",
    }
    defaults.update(config.get("workspace") or {})
    return defaults


def resolve_hub(root: Path, config: dict[str, Any]) -> Path | None:
    workspace = workspace_settings(config)
    if workspace["role"] == "hub":
        return root
    relative = workspace.get("hub_root")
    if not relative:
        return None
    candidate = (root / relative).resolve()
    if not state_path(candidate).is_file():
        raise RuntimeError("Configured hub_root is not an initialized Source workspace")
    return candidate


@contextmanager
def mutation_guard(root: Path, action: str, ttl_minutes: int = 15):
    """Best-effort cross-process guard; canonical data still uses append-only files."""
    parent = root / ".source" / "coordination"
    lock = parent / "mutation.lock"
    token = uuid.uuid4().hex
    parent.mkdir(parents=True, exist_ok=True)
    for _ in range(2):
        try:
            lock.mkdir()
            break
        except FileExistsError:
            lease = read_json(lock / "lease.json") or {}
            expires = parse_iso(lease.get("expires_at"))
            if expires and expires > dt.datetime.now(dt.timezone.utc):
                raise RuntimeError(f"Concurrent Source mutation is active: {lease.get('action', 'unknown')}")
            stale = parent / ("stale-" + uuid.uuid4().hex)
            try:
                os.replace(lock, stale)
                make_tree_writable(stale)
                shutil.rmtree(stale)
            except OSError as exc:
                raise RuntimeError("Stale cloud lock could not be reclaimed; wait for sync and retry") from exc
    else:
        raise RuntimeError("Could not acquire Source mutation lock")
    write_json_atomic(lock / "lease.json", {
        "schema_version": 1, "token": token, "action": action,
        "acquired_at": now_iso(),
        "expires_at": (dt.datetime.now(dt.timezone.utc) + dt.timedelta(minutes=ttl_minutes)).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
    }, root)
    try:
        yield
    finally:
        lease = read_json(lock / "lease.json") or {}
        if lease.get("token") == token and lock.exists():
            make_tree_writable(lock)
            shutil.rmtree(lock)


def active_lease_path(root: Path) -> Path:
    return root / ".source" / "coordination" / "active.lock"


def set_active_lease(root: Path, state: dict[str, Any], lease_hours: int) -> None:
    lock = active_lease_path(root)
    lock.parent.mkdir(parents=True, exist_ok=True)
    if lock.exists():
        current = read_json(lock / "lease.json") or {}
        expires = parse_iso(current.get("expires_at"))
        if expires and expires > dt.datetime.now(dt.timezone.utc):
            raise RuntimeError("This child project already has an active work session")
        make_tree_writable(lock)
        shutil.rmtree(lock)
    lock.mkdir()
    write_json_atomic(lock / "lease.json", {
        "schema_version": 1, "project_id": state["project_id"],
        "session_id": state["session_id"], "platform": system_name(),
        "acquired_at": now_iso(),
        "expires_at": (dt.datetime.now(dt.timezone.utc) + dt.timedelta(hours=lease_hours)).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
    }, root)


def release_active_lease(root: Path, session_id: str | None) -> None:
    lock = active_lease_path(root)
    lease = read_json(lock / "lease.json") or {}
    if lock.exists() and (not session_id or lease.get("session_id") == session_id):
        make_tree_writable(lock)
        shutil.rmtree(lock)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def tree_files(path: Path) -> list[Path]:
    return sorted(
        (
            item for item in path.rglob("*")
            if item.is_file() and "__pycache__" not in item.parts and item.suffix != ".pyc"
        ),
        key=lambda item: item.as_posix(),
    )


def sha256_tree(path: Path) -> str:
    digest = hashlib.sha256()
    for item in tree_files(path):
        digest.update(item.relative_to(path).as_posix().encode("utf-8"))
        digest.update(b"\0")
        digest.update(sha256_file(item).encode("ascii"))
        digest.update(b"\n")
    return digest.hexdigest()


def config_path(root: Path) -> Path:
    return root / ".source" / "config.json"


def state_path(root: Path) -> Path:
    return root / ".source" / "state.json"


def authority_path(root: Path) -> Path:
    return root / ".source" / "authority.json"


def authority_signature_path(root: Path) -> Path:
    return root / ".source" / "authority.sha256"


def authority_marker_path(root: Path) -> Path:
    return root / ".source" / "runtime" / "authority-change.json"


def expand_authority_entry(root: Path, entry: dict[str, Any]) -> list[Path]:
    target = root / entry["path"]
    if entry.get("kind", "file") == "tree":
        return tree_files(target) if target.is_dir() else []
    return [target]


def entry_hash(root: Path, entry: dict[str, Any]) -> str:
    target = root / entry["path"]
    return sha256_tree(target) if entry.get("kind", "file") == "tree" else sha256_file(target)


def set_writable(path: Path, writable: bool) -> None:
    if not path.exists():
        return
    if os.name == "nt":
        import ctypes

        kernel32 = ctypes.windll.kernel32
        attributes = kernel32.GetFileAttributesW(str(path))
        if attributes == 0xFFFFFFFF:
            raise OSError(f"Cannot read Windows attributes: {path.name}")
        read_only = 0x1
        updated = (attributes & ~read_only) if writable else (attributes | read_only)
        if not kernel32.SetFileAttributesW(str(path), updated):
            raise OSError(f"Cannot update Windows attributes: {path.name}")
        return
    mode = path.stat().st_mode
    if writable:
        path.chmod(mode | stat.S_IWUSR)
    else:
        path.chmod(mode & ~(stat.S_IWUSR | stat.S_IWGRP | stat.S_IWOTH))


def protected_files(root: Path, manifest: dict[str, Any]) -> list[Path]:
    files: list[Path] = []
    for entry in manifest.get("protected", []):
        files.extend(expand_authority_entry(root, entry))
    files.extend([authority_path(root), authority_signature_path(root)])
    return sorted(set(files), key=lambda item: item.as_posix())


def is_read_only(path: Path) -> bool:
    if os.name == "nt":
        import ctypes

        attributes = ctypes.windll.kernel32.GetFileAttributesW(str(path))
        return attributes != 0xFFFFFFFF and bool(attributes & 0x1)
    return not bool(path.stat().st_mode & (stat.S_IWUSR | stat.S_IWGRP | stat.S_IWOTH))


def filesystem_supports_read_only(root: Path) -> bool:
    runtime = root / ".source" / "runtime"
    runtime.mkdir(parents=True, exist_ok=True)
    probe = runtime / ("readonly-probe-" + uuid.uuid4().hex)
    try:
        probe.write_text("probe", encoding="utf-8")
        set_writable(probe, False)
        return is_read_only(probe)
    finally:
        if probe.exists():
            set_writable(probe, True)
            probe.unlink()


def authority_check(root: Path, require_locked: bool = True) -> list[tuple[str, str]]:
    manifest_file = authority_path(root)
    signature_file = authority_signature_path(root)
    if not manifest_file.is_file():
        return [("NOT_CONFIGURED", ".source/authority.json is absent")]
    if not signature_file.is_file():
        return [("BLOCKED", ".source/authority.sha256 is absent")]
    expected_signature = signature_file.read_text(encoding="ascii").strip().lower()
    actual_signature = sha256_file(manifest_file)
    issues: list[tuple[str, str]] = []
    if expected_signature != actual_signature:
        issues.append(("BLOCKED", "authority manifest signature mismatch"))
        return issues
    manifest = read_json(manifest_file)
    for entry in manifest.get("protected", []):
        target = root / entry["path"]
        if not target.exists():
            issues.append(("BLOCKED", f"protected path missing: {entry['path']}"))
            continue
        if entry.get("sha256") != entry_hash(root, entry):
            issues.append(("BLOCKED", f"protected hash mismatch: {entry['path']}"))
    if authority_marker_path(root).exists():
        issues.append(("BLOCKED", "formal authority change is open; run authority-seal"))
    if require_locked and not issues:
        unlocked = [item.relative_to(root).as_posix() for item in protected_files(root, manifest) if not is_read_only(item)]
        if unlocked:
            if filesystem_supports_read_only(root):
                issues.append(("LOCK_DRIFT", f"read-only lock missing: {', '.join(unlocked[:5])}"))
            else:
                issues.append(("HASH_ENFORCED", "filesystem has no persistent read-only attribute; signature and hashes remain mandatory"))
    return issues or [("PASS", "authority signature, hashes, and lock are valid")]


def authority_lock(root: Path) -> None:
    issues = authority_check(root, require_locked=False)
    blocked = [detail for status, detail in issues if status == "BLOCKED"]
    if blocked:
        raise RuntimeError("; ".join(blocked))
    manifest = read_json(authority_path(root))
    for item in protected_files(root, manifest):
        set_writable(item, False)


def authority_unlock(root: Path, *, yes: bool, agent: str) -> None:
    if not yes:
        raise RuntimeError("authority-unlock requires --yes")
    issues = authority_check(root, require_locked=False)
    blocked = [detail for status, detail in issues if status == "BLOCKED"]
    if blocked:
        raise RuntimeError("; ".join(blocked))
    manifest = read_json(authority_path(root))
    for item in protected_files(root, manifest):
        set_writable(item, True)
    marker = authority_marker_path(root)
    marker.parent.mkdir(parents=True, exist_ok=True)
    write_json_atomic(marker, {"opened_at": now_iso(), "agent": agent, "purpose": "formal-authority-change"}, root)
    print("AUTHORITY UNLOCKED: modify only the approved canonical files, then run authority-seal --yes")


def authority_seal(root: Path, *, yes: bool, agent: str) -> None:
    if not yes:
        raise RuntimeError("authority-seal requires --yes")
    manifest_file = authority_path(root)
    if not manifest_file.is_file():
        raise RuntimeError(".source/authority.json is absent")
    set_writable(manifest_file, True)
    signature_file = authority_signature_path(root)
    set_writable(signature_file, True)
    manifest = read_json(manifest_file)
    for entry in manifest.get("protected", []):
        target = root / entry["path"]
        if not target.exists():
            raise RuntimeError(f"protected path missing: {entry['path']}")
        entry["sha256"] = entry_hash(root, entry)
    manifest["sealed_at"] = now_iso()
    manifest["sealed_by"] = agent
    write_json_atomic(manifest_file, manifest, root)
    write_text_atomic(signature_file, sha256_file(manifest_file))
    current_state = read_json(state_path(root))
    if current_state:
        migrate_state(current_state)
        write_json_atomic(state_path(root), current_state, root)
        write_handoff(root, portable(current_state, root))
    marker = authority_marker_path(root)
    if marker.exists():
        marker.unlink()
    authority_lock(root)
    print("AUTHORITY SEALED: signature, protected hashes, and read-only permissions applied")


def ensure_authority(root: Path) -> None:
    issues = authority_check(root, require_locked=True)
    if issues[0][0] == "NOT_CONFIGURED":
        return
    blocked = [detail for status, detail in issues if status == "BLOCKED"]
    if blocked:
        raise RuntimeError("Authority gate blocked: " + "; ".join(blocked))
    if any(status == "LOCK_DRIFT" for status, _ in issues):
        authority_lock(root)


def has_absolute_path(value: Any) -> list[str]:
    findings: list[str] = []

    def walk(item: Any, where: str) -> None:
        if isinstance(item, dict):
            for key, child in item.items():
                walk(child, f"{where}.{key}")
        elif isinstance(item, list):
            for index, child in enumerate(item):
                walk(child, f"{where}[{index}]")
        elif isinstance(item, str) and (WINDOWS_ABS.search(item) or UNC_ABS.search(item) or POSIX_ABS.search(item)):
            findings.append(where)

    walk(value, "$")
    return findings


def copy_if_missing(template: str, destination: Path, dry_run: bool) -> bool:
    if destination.exists():
        return False
    source = ASSET_ROOT / template
    if not source.is_file():
        raise RuntimeError(f"Template missing: {template}")
    if not dry_run:
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
    return True


def merge_gitignore(root: Path, dry_run: bool, role: str = "standalone") -> None:
    path = root / ".gitignore"
    required = (
        "desktop.ini", "*.tmp", "~$*", ".env", ".env.*", "*.key", "*.pem",
        "credentials.*", ".source/backups/", ".source/runtime/",
        ".source/coordination/", "__pycache__/", "*.pyc",
    )
    if role == "hub":
        required = (*required, "projects/*/")
    existing = path.read_text(encoding="utf-8-sig").splitlines() if path.exists() else []
    updated = existing + [item for item in required if item not in existing]
    if updated != existing and not dry_run:
        write_text_atomic(path, "\n".join(updated))


def git_snapshot(root: Path, fetch: bool = False) -> dict[str, Any]:
    if not command_exists("git"):
        return {"enabled": False, "status": "BLOCKED", "branch": None, "remote": None, "ahead": 0, "behind": 0}
    if not (root / ".git").exists():
        return {"enabled": False, "status": "NOT_CONFIGURED", "branch": None, "remote": None, "ahead": 0, "behind": 0}
    if run(["git", "rev-parse", "--is-inside-work-tree"], cwd=root, check=False).returncode:
        return {"enabled": False, "status": "NOT_CONFIGURED", "branch": None, "remote": None, "ahead": 0, "behind": 0}
    branch = run(["git", "branch", "--show-current"], cwd=root).stdout.strip()
    remotes = run(["git", "remote"], cwd=root).stdout.split()
    remote = run(["git", "remote", "get-url", "origin"], cwd=root).stdout.strip() if "origin" in remotes else None
    if fetch and remote:
        fetch_head = root / ".git" / "FETCH_HEAD"
        fresh = fetch_head.exists() and (dt.datetime.now().timestamp() - fetch_head.stat().st_mtime) < 1800
        if not fresh:
            run(["git", "fetch", "origin"], cwd=root, check=False)
    ahead = behind = 0
    upstream = run(
        ["git", "for-each-ref", "--format=%(upstream:short)", f"refs/heads/{branch}"],
        cwd=root, check=False,
    ).stdout.strip()
    if upstream:
        counts = run(["git", "rev-list", "--left-right", "--count", f"HEAD...{upstream}"], cwd=root).stdout.split()
        if len(counts) >= 2:
            ahead, behind = int(counts[0]), int(counts[1])
    dirty = bool(run(["git", "status", "--porcelain"], cwd=root).stdout.strip())
    status_value = "DIRTY" if dirty else ("BEHIND" if behind else "CLEAN")
    return {"enabled": True, "status": status_value, "branch": branch, "remote": remote, "ahead": ahead, "behind": behind}


def update_git_state(root: Path, state: dict[str, Any], fetch: bool = False) -> None:
    snapshot = git_snapshot(root, fetch)
    state["git"].update(snapshot)


def assert_child(parent: Path, child: Path) -> None:
    try:
        child.resolve().relative_to(parent.resolve())
    except ValueError as exc:
        raise RuntimeError("Unsafe target outside managed root") from exc


def make_tree_writable(path: Path) -> None:
    if not path.exists():
        return
    for item in [path, *path.rglob("*")]:
        try:
            set_writable(item, True)
        except OSError:
            pass


def directory_hash(path: Path) -> str:
    return sha256_tree(path)


def install_agent_adapters(results: list[str]) -> None:
    home = Path.home()
    if os.name == "nt":
        script = home / ".agents" / "scripts" / "install-agent-adapters.ps1"
        if script.is_file() and command_exists("powershell.exe"):
            completed = run(["powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", script], check=False)
            results.append("adapters=VERIFIED" if completed.returncode == 0 else "adapters=PARTIAL")
        return
    claude_root = home / ".claude" / "skills"
    claude_root.mkdir(parents=True, exist_ok=True)
    for name in MANAGED_SKILLS:
        target = home / ".agents" / "skills" / name
        link = claude_root / name
        if link.is_symlink() and link.resolve() == target.resolve():
            continue
        if link.exists() or link.is_symlink():
            results.append(f"claude-{name}=SKIPPED_CONFLICT")
            continue
        link.symlink_to(target, target_is_directory=True)
    results.append("adapters=VERIFIED")


def install_managed_skills(source_root: Path, *, yes: bool, dry_run: bool) -> list[str]:
    destination_root = Path.home() / ".agents" / "skills"
    backup_root = Path.home() / ".agents" / "skill-backups" / ("source-" + dt.datetime.now().strftime("%Y%m%d-%H%M%S"))
    results: list[str] = []
    if not dry_run:
        destination_root.mkdir(parents=True, exist_ok=True)
    for name in MANAGED_SKILLS:
        source = source_root / name
        destination = destination_root / name
        if not (source / "SKILL.md").is_file():
            raise RuntimeError(f"Skill source missing: {name}")
        if source.resolve() == destination.resolve():
            results.append(f"{name}=CANONICAL")
            continue
        if destination.exists():
            if directory_hash(source) == directory_hash(destination):
                results.append(f"{name}=MATCH")
                continue
            if not yes:
                raise RuntimeError(f"Skill conflict: {name} differs; re-run with --yes")
            assert_child(destination_root, destination)
            if not dry_run:
                backup_root.mkdir(parents=True, exist_ok=True)
                shutil.copytree(destination, backup_root / name, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
                make_tree_writable(destination)
                shutil.rmtree(destination)
        if not dry_run:
            shutil.copytree(source, destination, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
            make_tree_writable(destination)
        results.append(f"{name}={'WOULD_INSTALL' if dry_run else 'INSTALLED'}")
    if not dry_run:
        install_agent_adapters(results)
    return results


def sync_dotfiles(*, yes: bool, dry_run: bool, message: str) -> dict[str, str]:
    chezmoi = find_chezmoi()
    if not chezmoi:
        return {"status": "BLOCKED", "detail": "chezmoi missing; install it and resume"}
    home = Path.home()
    source_path = Path(run([chezmoi, "source-path"]).stdout.strip())
    if not dry_run:
        for name in MANAGED_SKILLS:
            live = home / ".agents" / "skills" / name
            if live.exists():
                run([chezmoi, "add", "--force", "--no-tty", live])
            managed = run(
                [chezmoi, "managed", "--include", "files", "--path-style", "absolute", live],
                check=False,
            ).stdout.splitlines()
            for item in managed:
                candidate = Path(item.strip())
                if item.strip() and not candidate.exists():
                    run([chezmoi, "forget", "--force", "--no-tty", candidate])
        targets = [
            home / ".agents", home / ".codex" / "AGENTS.md",
            home / ".claude" / "CLAUDE.md", home / ".gemini" / "GEMINI.md",
        ]
        existing = [item for item in targets if item.exists()]
        if existing:
            run([chezmoi, "re-add", "--force", "--no-tty", *existing])
    dirty = run(["git", "status", "--porcelain"], cwd=source_path).stdout.strip()
    if not dirty:
        return {"status": "VERIFIED", "detail": "dotfiles already current"}
    if not yes:
        return {"status": "PARTIAL", "detail": "dotfiles changed; re-run with --yes"}
    if not dry_run:
        run(["git", "add", "--all"], cwd=source_path)
        run(["git", "commit", "-m", message], cwd=source_path)
        run(["git", "push", "origin", "HEAD"], cwd=source_path)
    return {"status": "VERIFIED", "detail": "dotfiles committed and pushed"}


def assert_no_sensitive_changes(root: Path) -> None:
    for line in run(["git", "status", "--porcelain"], cwd=root).stdout.splitlines():
        item = line[3:].strip().strip('"') if len(line) > 3 else ""
        if SENSITIVE.search(item):
            raise RuntimeError(f"Sensitive path must not be committed: {item}")


def git_finish(root: Path, message: str, includes: list[str], dry_run: bool) -> dict[str, Any]:
    snapshot = git_snapshot(root)
    if not snapshot["enabled"]:
        return {"status": "NOT_CONFIGURED", "commit": None, "pushed": False}
    assert_no_sensitive_changes(root)
    if not run(["git", "status", "--porcelain"], cwd=root).stdout.strip():
        return {"status": "NO_CHANGES", "commit": None, "pushed": True}
    if dry_run:
        return {"status": "DRY_RUN", "commit": None, "pushed": False}
    run(["git", "add", "-u"], cwd=root)
    for item in includes:
        full = (root / item).resolve()
        assert_child(root, full)
        run(["git", "add", "--", item], cwd=root)
    untracked = run(["git", "ls-files", "--others", "--exclude-standard"], cwd=root).stdout.splitlines()
    if untracked:
        raise RuntimeError("Untracked files remain; approve with --include: " + ", ".join(untracked))
    cached = run(["git", "diff", "--cached", "--name-only"], cwd=root).stdout.splitlines()
    if not cached:
        return {"status": "NO_STAGED_CHANGES", "commit": None, "pushed": False}
    run(["git", "diff", "--cached", "--check"], cwd=root)
    run(["git", "commit", "-m", message], cwd=root)
    commit = run(["git", "rev-parse", "HEAD"], cwd=root).stdout.strip()
    if "origin" not in run(["git", "remote"], cwd=root).stdout.split():
        return {"status": "COMMITTED_NOT_PUSHED", "commit": commit, "pushed": False}
    pushed = run(["git", "push", "origin", "HEAD"], cwd=root, check=False)
    return {"status": "VERIFIED" if pushed.returncode == 0 else "PUSH_FAILED", "commit": commit, "pushed": pushed.returncode == 0}


def ensure_git_identity(root: Path) -> None:
    if not git_snapshot(root)["enabled"]:
        return
    if not run(["git", "config", "user.name"], cwd=root, check=False).stdout.strip():
        run(["git", "config", "user.name", "Source Bootstrap"], cwd=root)
    if not run(["git", "config", "user.email"], cwd=root, check=False).stdout.strip():
        run(["git", "config", "user.email", "source-bootstrap@example.invalid"], cwd=root)


def new_config(
    name: str, root: Path, *, role: str = "standalone", hub_root: str | None = None,
) -> dict[str, Any]:
    snapshot = git_snapshot(root)
    return {
        "schema_version": 3,
        "project_name": name,
        "project_kind": "standard",
        "default_branch": snapshot.get("branch") or "main",
        "workspace": {
            "role": role,
            "hub_root": hub_root,
            "child_root": "projects",
            "logs_root": "logs/sessions",
            "event_root": ".source/hub/events",
            "coordination_root": ".source/coordination",
        },
        "git": {
            "private_by_default": True,
            "remote": snapshot.get("remote"),
            "include_paths": [
                ".source", "SOURCE.md", "AGENTS.md", "handoff.md", "source.ps1",
                "source.sh", ".gitattributes", ".gitignore", "knowledge",
            ],
        },
        "skills": {
            "managed": list(MANAGED_SKILLS), "sync_dotfiles": True,
            "remote": DEFAULT_SKILL_REMOTE, "branch": "main",
            "update_policy": "auto-approved",
        },
        "connectors": {
            "gdrive": {"enabled": True, "mode": "RUNTIME_DETECT"},
            "obsidian": {
                "enabled": True, "mode": "LOCAL_VAULT",
                "relative_note": "knowledge/obsidian/Project Log.md",
            },
            "notion": {
                "enabled": True, "mode": "AGENT", "knowledge_master": None,
                "topic": None, "prompt": None, "period_page": None,
            },
            "cdn": {"enabled": False, "mode": "AGENT", "provider": None, "target": None},
        },
    }


def new_state(name: str, agent: str) -> dict[str, Any]:
    return {
        "schema_version": 3,
        "project_id": str(uuid.uuid4()),
        "project_name": name,
        "phase": "INITIALIZING",
        "revision": 0,
        "session_id": None,
        "summary": "正在建立 Source pipeline。",
        "last_action": "init",
        "updated_at": now_iso(),
        "actor": {"agent": agent, "platform": system_name()},
        "next_steps": ["完成初始化檢查。"],
        "git": {
            "enabled": False, "status": "NOT_CONFIGURED", "branch": None,
            "remote": None, "ahead": 0, "behind": 0, "last_push": None,
        },
        "connectors": {
            "github": {"status": "NOT_CONFIGURED", "external_id": None, "note": None},
            "hub": {"status": "NOT_CONFIGURED", "external_id": None, "note": None},
            "skills": {"status": "READY", "external_id": None, "note": None},
            "gdrive": {"status": "RUNTIME", "external_id": None, "note": None},
            "obsidian": {"status": "NOT_CONFIGURED", "external_id": None, "note": None},
            "notion": {"status": "NOT_CONFIGURED", "external_id": None, "note": None},
            "cdn": {"status": "NOT_CONFIGURED", "external_id": None, "note": None},
        },
    }


def migrate_state(state: dict[str, Any]) -> dict[str, Any]:
    actor = state.setdefault("actor", {})
    actor.pop("device", None)
    actor["platform"] = system_name()
    state.setdefault("connectors", {}).setdefault(
        "hub", {"status": "NOT_CONFIGURED", "external_id": None, "note": None},
    )
    state["schema_version"] = 3
    return state


def prepare_connector_files(root: Path, config: dict[str, Any], dry_run: bool) -> list[str]:
    results: list[str] = []
    obsidian = config.get("connectors", {}).get("obsidian", {})
    if obsidian.get("enabled") and obsidian.get("relative_note"):
        relative = safe_relative(obsidian["relative_note"], label="Obsidian relative_note")
        destination = root / relative
        if copy_if_missing("obsidian-project-log.template.md", destination, dry_run):
            results.append(f"obsidian={relative}")
    checkpoint = root / ".source" / "connectors" / "notion.json"
    if config.get("connectors", {}).get("notion", {}).get("enabled") and not checkpoint.exists() and not dry_run:
        write_json_atomic(checkpoint, {
            "schema_version": 1, "status": "NEEDS_SETUP",
            "instruction": "Authorize the Notion connector, create or select the project page, then run Source complete.",
            "page_id": None, "prompt_policy": "READ_ONLY",
        }, root)
        results.append("notion=NEEDS_SETUP")
    return results


def session_log_path(root: Path, config: dict[str, Any], session_id: str) -> Path:
    relative = safe_relative(workspace_settings(config)["logs_root"], label="logs_root")
    return root / relative / f"{session_id}.json"


def update_session_log(
    root: Path, config: dict[str, Any], state: dict[str, Any], session_id: str,
    event: str, *, summary: str | None = None,
) -> Path:
    path = session_log_path(root, config, session_id)
    log = read_json(path) or {
        "schema_version": 1, "project_id": state["project_id"],
        "project_name": state["project_name"], "session_id": session_id,
        "started_at": state.get("updated_at") or now_iso(), "events": [],
    }
    log["events"].append({"event": event, "at": now_iso(), "agent": state.get("actor", {}).get("agent")})
    log["status"] = "WORKING" if event == "start" else "FINISHED"
    if event == "finish":
        log["finished_at"] = now_iso()
    if summary:
        log["summary"] = summary
    write_json_atomic(path, log, root)
    return path


def publish_hub_event(
    root: Path, config: dict[str, Any], state: dict[str, Any], event: str,
    session_id: str | None, *, proposals: list[dict[str, str]] | None = None,
) -> Path | None:
    hub = resolve_hub(root, config)
    if not hub or hub == root:
        return None
    assert_child(hub, root)
    hub_config = read_json(config_path(hub)) or {}
    if workspace_settings(hub_config)["role"] != "hub":
        raise RuntimeError("Configured parent is not a Source hub")
    event_root = safe_relative(workspace_settings(hub_config)["event_root"], label="event_root")
    event_id = uuid.uuid4().hex
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    target = hub / event_root / state["project_id"] / f"{stamp}-{event_id}.json"
    if target.exists():
        raise RuntimeError("Append-only hub event collision")
    write_json_atomic(target, {
        "schema_version": 1, "event_id": event_id, "event": event,
        "project_id": state["project_id"], "project_name": state["project_name"],
        "project_path": root.relative_to(hub).as_posix(), "session_id": session_id,
        "phase": state["phase"], "revision": state["revision"],
        "summary": state["summary"], "created_at": now_iso(),
        "git_commit": state.get("git", {}).get("last_push"),
        "skill_proposals": proposals or [],
    }, hub)
    set_writable(target, False)
    return target


def publish_skill_proposals(
    root: Path, config: dict[str, Any], state: dict[str, Any], session_id: str,
) -> list[dict[str, str]]:
    skills_root = root / "skills"
    hub = resolve_hub(root, config)
    if not hub or hub == root or not skills_root.is_dir():
        return []
    proposals: list[dict[str, str]] = []
    for source in sorted(skills_root.iterdir(), key=lambda item: item.name.lower()):
        if not source.is_dir() or not (source / "SKILL.md").is_file():
            continue
        name = re.sub(r"[^a-z0-9-]+", "-", source.name.lower()).strip("-")
        if not name or name != source.name.lower():
            raise RuntimeError(f"Invalid proposed skill directory: {source.name}")
        for item in tree_files(source):
            if item.is_symlink() or SENSITIVE.search(item.relative_to(source).as_posix()):
                raise RuntimeError(f"Unsafe skill proposal content: {source.name}")
        digest = directory_hash(source)
        destination = hub / ".source" / "hub" / "skill-proposals" / state["project_id"] / session_id / name
        if destination.exists():
            raise RuntimeError(f"Skill proposal already exists: {name}")
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(source, destination, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        write_json_atomic(destination / "proposal.json", {
            "schema_version": 1, "name": name, "sha256": digest,
            "project_id": state["project_id"], "session_id": session_id,
            "created_at": now_iso(), "status": "REVIEW_REQUIRED",
        }, hub)
        proposals.append({"name": name, "sha256": digest, "status": "REVIEW_REQUIRED"})
    return proposals


def approved_skill_status(
    root: Path, config: dict[str, Any], state: dict[str, Any], *, apply: bool,
) -> dict[str, str]:
    skills = config.get("skills") or {}
    remote = skills.get("remote")
    branch = skills.get("branch") or "main"
    if not remote:
        return {"status": "NOT_CONFIGURED", "detail": "No approved skill remote configured"}
    if os.environ.get("SOURCE_DISABLE_NETWORK") == "1":
        return {"status": "SKIPPED", "detail": "Network skill check disabled by runtime"}
    result = run(["git", "ls-remote", remote, f"refs/heads/{branch}"], check=False)
    if result.returncode or not result.stdout.strip():
        return {"status": "PARTIAL", "detail": "Approved skill remote is temporarily unavailable"}
    commit = result.stdout.split()[0]
    if config.get("project_kind") == "skill-distribution" and root.resolve() == DISTRIBUTION_ROOT.resolve():
        snapshot = git_snapshot(root)
        local_head = run(["git", "rev-parse", "HEAD"], cwd=root, check=False).stdout.strip() if snapshot["enabled"] else None
        if snapshot.get("status") == "DIRTY" or (local_head and local_head != commit):
            return {
                "status": "LOCAL_WORKING_COPY",
                "detail": "Canonical distribution checkout is newer or modified; remote downgrade is disabled",
            }
        if local_head == commit:
            if apply:
                state["connectors"]["skills"].update(
                    status="VERIFIED", external_id=commit, note="Canonical distribution matches approved remote",
                )
            return {"status": "CURRENT", "detail": commit}
    current = state.get("connectors", {}).get("skills", {}).get("external_id")
    if current == commit:
        return {"status": "CURRENT", "detail": commit}
    if not apply:
        return {"status": "UPDATE_AVAILABLE", "detail": commit}
    temp_root = Path(tempfile.mkdtemp(prefix="source-approved-skills-"))
    try:
        clone = run(["git", "clone", "--depth", "1", "--branch", branch, remote, temp_root], check=False)
        if clone.returncode:
            return {"status": "PARTIAL", "detail": "Approved skill source could not be cloned"}
        blocked = [detail for status, detail in authority_check(temp_root, require_locked=False) if status == "BLOCKED"]
        if blocked:
            return {"status": "BLOCKED", "detail": "Remote authority validation failed: " + "; ".join(blocked)}
        installed = install_managed_skills(temp_root, yes=True, dry_run=False)
        state["connectors"]["skills"].update(status="VERIFIED", external_id=commit, note="; ".join(installed))
        return {"status": "UPDATED", "detail": commit}
    finally:
        make_tree_writable(temp_root)
        shutil.rmtree(temp_root, ignore_errors=True)


def connector_bootstrap(root: Path, args: argparse.Namespace) -> None:
    ensure_authority(root)
    config = read_json(config_path(root))
    state = read_json(state_path(root))
    with mutation_guard(root, "connector-bootstrap"):
        results = prepare_connector_files(root, config, args.dry_run)
        obsidian = config["connectors"]["obsidian"]
        if obsidian.get("enabled"):
            state["connectors"]["obsidian"].update(
                status="LOCAL_READY", external_id=obsidian.get("relative_note"),
                note="Project-local Obsidian-compatible vault",
            )
        notion = config["connectors"]["notion"]
        if notion.get("enabled") and not notion.get("period_page"):
            state["connectors"]["notion"].update(
                status="NEEDS_SETUP", note="Authorize connector and create/select a project page",
            )
        save_checkpoint(root, state, action="connector-bootstrap", next_steps=[
            "如需 Notion，授權 connector 並建立或選擇專案頁後執行 Source complete。",
        ], agent=args.agent)
    print("CONNECTORS: " + (", ".join(results) if results else "already prepared"))
    show_status(root)


def slugify(value: str) -> str:
    slug = re.sub(r"[^\w-]+", "-", value.lower(), flags=re.UNICODE).replace("_", "-").strip("-")
    if not slug:
        slug = "project-" + uuid.uuid4().hex[:8]
    reserved = {"con", "prn", "aux", "nul", *(f"com{i}" for i in range(1, 10)), *(f"lpt{i}" for i in range(1, 10))}
    if slug.lower() in reserved:
        slug = "project-" + slug
    if len(slug) > 64:
        slug = slug[:48].rstrip("-") + "-" + hashlib.sha256(value.encode("utf-8")).hexdigest()[:8]
    return slug


def child_create(root: Path, args: argparse.Namespace) -> None:
    ensure_authority(root)
    config = read_json(config_path(root))
    if workspace_settings(config)["role"] != "hub":
        raise RuntimeError("child-create must run from a Source hub")
    if not args.child_name:
        raise RuntimeError("--child-name is required")
    slug = slugify(args.child_name)
    relative = args.child_path or f"{workspace_settings(config)['child_root']}/{slug}"
    relative = safe_relative(relative, label="child_path")
    child = (root / relative).resolve()
    assert_child(root, child)
    if child.exists() and any(child.iterdir()):
        raise RuntimeError(f"Child target is not empty: {relative}")
    child_args = argparse.Namespace(**vars(args))
    child_args.project_root = str(child)
    child_args.project_name = args.child_name
    child_args.workspace_role = "child"
    child_args.hub_root = Path(os.path.relpath(root, child)).as_posix()
    initialize(child, child_args)
    child_state = read_json(state_path(child))
    child_state["connectors"]["hub"].update(
        status="READY", external_id="hub", note="Parent hub is configured by relative path",
    )
    save_checkpoint(
        child, child_state, action="child-register",
        next_steps=["執行 Source 自動開工。"], agent=args.agent,
    )
    ensure_git_identity(child)
    git_finish(child, f"初始化 Source 子專案：{args.child_name}", [
        ".source", "SOURCE.md", "AGENTS.md", "handoff.md", "source.ps1",
        "source.sh", ".gitattributes", ".gitignore", "knowledge",
    ], args.dry_run)
    child_state = read_json(state_path(child))
    descriptor = root / ".source" / "hub" / "projects" / f"{child_state['project_id']}.json"
    write_json_atomic(descriptor, {
        "schema_version": 1, "project_id": child_state["project_id"],
        "project_name": args.child_name, "project_path": relative,
        "created_at": now_iso(), "status": "ACTIVE",
    }, root)
    set_writable(descriptor, False)
    publish_hub_event(child, read_json(config_path(child)), child_state, "initialized", None)
    print(f"CHILD CREATED: {relative}")
    print(f"NEXT: run Source in {relative}")


def hub_status(root: Path) -> None:
    config = read_json(config_path(root)) or {}
    if workspace_settings(config)["role"] != "hub":
        raise RuntimeError("hub-status must run from a Source hub")
    descriptors = sorted((root / ".source" / "hub" / "projects").glob("*.json"))
    event_root = root / workspace_settings(config)["event_root"]
    print(f"HUB: projects={len(descriptors)}")
    for descriptor_path in descriptors:
        descriptor = read_json(descriptor_path)
        child = root / descriptor["project_path"]
        child_state = read_json(state_path(child)) or {}
        events = list((event_root / descriptor["project_id"]).glob("*.json"))
        active = read_json(active_lease_path(child) / "lease.json") or {}
        lease_state = "ACTIVE" if parse_iso(active.get("expires_at")) and parse_iso(active.get("expires_at")) > dt.datetime.now(dt.timezone.utc) else "IDLE"
        print(
            f"- {descriptor['project_name']} | {descriptor['project_path']} | "
            f"phase={child_state.get('phase', 'MISSING')} | lease={lease_state} | events={len(events)}"
        )


def hub_sync(root: Path, args: argparse.Namespace) -> None:
    ensure_authority(root)
    config = read_json(config_path(root)) or {}
    if workspace_settings(config)["role"] != "hub":
        raise RuntimeError("hub-sync must run from a Source hub")
    with mutation_guard(root, "hub-sync"):
        result = git_finish(
            root, args.commit_message or "同步 Source 子專案事件", [".source/hub"], args.dry_run,
        )
    print(f"HUB SYNC: {result['status']} commit={result.get('commit')}")


def write_handoff(root: Path, state: dict[str, Any]) -> None:
    steps = state.get("next_steps") or ["執行 Source 的 next 動作。"]
    step_text = "\n".join(f"{index}. {item}" for index, item in enumerate(steps, 1))
    connectors = "\n".join(f"- {name}：{value['status']}" for name, value in state["connectors"].items())
    git = state["git"]
    git_line = f"{git['status']}；branch={git['branch']}；last_push={git.get('last_push')}" if git["enabled"] else "NOT_CONFIGURED"
    actor = state.get("actor", {})
    text = f"""# Handoff

> GENERATED／DO NOT EDIT：本檔只能由 Source engine 產生；canonical checkpoint 是 `.source/state.json`。

## 目前做到哪

{state['summary']}

## 狀態

- Phase：{state['phase']}
- Revision：{state['revision']}
- Last action：{state['last_action']}
- Git：{git_line}

## 下一步

{step_text}

## Connectors

{connectors}

## 最後更新

- {state['updated_at']}
- {actor.get('agent')} @ {actor.get('platform')}
"""
    write_text_atomic(root / "handoff.md", text)


def save_checkpoint(root: Path, state: dict[str, Any], *, action: str, next_steps: list[str] | None, agent: str) -> None:
    migrate_state(state)
    state["revision"] = int(state.get("revision", 0)) + 1
    state["last_action"] = action
    state["updated_at"] = now_iso()
    state["actor"] = {"agent": agent, "platform": system_name()}
    if next_steps is not None:
        state["next_steps"] = next_steps
    write_json_atomic(state_path(root), state, root)
    write_handoff(root, portable(state, root))


def show_status(root: Path) -> None:
    state = read_json(state_path(root))
    if not state:
        print(f"NOT_INITIALIZED: {root}")
        print("NEXT: run Source init")
        return
    migrate_state(state)
    git = state["git"]
    print(f"SOURCE {state['project_name']} | phase={state['phase']} | revision={state['revision']}")
    print(f"STATUS: {state['summary']}")
    print(f"GIT: {git['status']} | branch={git['branch']} | ahead={git['ahead']} | behind={git['behind']}")
    for name, connector in state["connectors"].items():
        print(f"{name.upper()}: {connector['status']}")
    if state.get("next_steps"):
        print("NEXT:")
        for index, step in enumerate(state["next_steps"], 1):
            print(f"  {index}. {step}")


def initialize(root: Path, args: argparse.Namespace) -> None:
    if state_path(root).is_file():
        print("Source pipeline 已初始化；不覆寫。")
        show_status(root)
        return
    if not args.dry_run:
        root.mkdir(parents=True, exist_ok=True)
    name = args.project_name or root.name
    role = getattr(args, "workspace_role", None) or "standalone"
    hub_root = getattr(args, "hub_root", None)
    config = new_config(name, root, role=role, hub_root=hub_root)
    state = new_state(name, args.agent)
    if not args.dry_run:
        (root / ".source").mkdir(parents=True, exist_ok=True)
        write_json_atomic(config_path(root), config, root)
        write_json_atomic(state_path(root), state, root)
    for template, destination in (
        ("SOURCE.template.md", root / "SOURCE.md"),
        ("AGENTS.template.md", root / "AGENTS.md"),
        ("handoff.template.md", root / "handoff.md"),
        ("source.launcher.ps1", root / "source.ps1"),
        ("source.launcher.sh", root / "source.sh"),
        ("gitattributes.template", root / ".gitattributes"),
        ("authority.template.json", authority_path(root)),
    ):
        copy_if_missing(template, destination, args.dry_run)
    if not args.dry_run and os.name != "nt":
        launcher = root / "source.sh"
        launcher.chmod(launcher.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    merge_gitignore(root, args.dry_run, role)
    prepare_connector_files(root, config, args.dry_run)
    if not command_exists("git"):
        state["connectors"]["github"].update(status="BLOCKED", note="git missing")
    elif not (root / ".git").exists() and not args.dry_run:
        result = run(["git", "init", "-b", "main"], cwd=root, check=False)
        if result.returncode:
            run(["git", "init"], cwd=root)
            run(["git", "branch", "-M", "main"], cwd=root)
    update_git_state(root, state)
    if state["git"]["enabled"]:
        state["connectors"]["github"]["status"] = "READY" if state["git"]["remote"] else "LOCAL_ONLY"
    if args.create_remote and not state["git"]["remote"]:
        if not args.yes:
            raise RuntimeError("Creating a private GitHub repo requires --yes")
        if not command_exists("gh") or run(["gh", "auth", "status"], check=False).returncode:
            raise RuntimeError("GitHub CLI unavailable or unauthenticated; run gh auth login")
        owner = run(["gh", "api", "user", "--jq", ".login"]).stdout.strip()
        slug = re.sub(r"[^a-z0-9-]+", "-", name.lower()).strip("-")
        if not args.dry_run:
            run(["gh", "repo", "create", f"{owner}/{slug}", "--private", "--source", root, "--remote", "origin"])
        update_git_state(root, state)
        state["connectors"]["github"]["status"] = "READY"
    state["phase"] = "READY"
    state["summary"] = f"Source {role} pipeline 初始化完成；可開始工作。"
    if config["connectors"]["obsidian"]["enabled"]:
        state["connectors"]["obsidian"].update(
            status="LOCAL_READY", external_id=config["connectors"]["obsidian"]["relative_note"],
            note="Project-local Obsidian-compatible vault",
        )
    if config["connectors"]["notion"]["enabled"] and not config["connectors"]["notion"].get("period_page"):
        state["connectors"]["notion"].update(
            status="NEEDS_SETUP", note="Authorize connector and create/select a project page",
        )
    if role == "hub":
        state["connectors"]["hub"].update(status="HUB_READY", note="Append-only hub event receiver")
    elif role == "child":
        state["connectors"]["hub"].update(status="READY", external_id="hub", note="Relative parent hub")
    if not args.dry_run:
        authority_seal(root, yes=True, agent=args.agent)
        save_checkpoint(root, state, action="init", next_steps=["執行 Source 自動開工。"], agent=args.agent)
    show_status(root)


def start_project(root: Path, args: argparse.Namespace) -> None:
    state = read_json(state_path(root))
    if not state:
        initialize(root, args)
        return
    ensure_authority(root)
    if state["phase"] == "WORKING":
        print("既有工作 session 尚未收工；沿用原 checkpoint。")
        show_status(root)
        return
    config = read_json(config_path(root))
    with mutation_guard(root, "start"):
        role = workspace_settings(config)["role"]
        if role == "hub":
            state["connectors"]["hub"].update(status="HUB_READY", note="Append-only hub event receiver")
        elif role == "child":
            state["connectors"]["hub"].update(status="READY", external_id="hub", note="Relative parent hub")
        update_git_state(root, state, fetch=True)
        for name in ("obsidian", "notion"):
            if config["connectors"][name]["enabled"] and state["connectors"][name]["status"] == "NOT_CONFIGURED":
                state["connectors"][name]["status"] = "READY_AGENT"
        cloud_tokens = ("google drive", "my drive", "雲端硬碟")
        state["connectors"]["gdrive"]["status"] = "DETECTED" if any(token in str(root).lower() for token in cloud_tokens) else "RUNTIME"
        skill_result = approved_skill_status(
            root, config, state,
            apply=(config.get("skills", {}).get("update_policy") == "auto-approved"),
        )
        if skill_result["status"] in ("PARTIAL", "BLOCKED"):
            state["connectors"]["skills"].update(status=skill_result["status"], note=skill_result["detail"])
        state["phase"] = "WORKING"
        state["session_id"] = str(uuid.uuid4())
        set_active_lease(root, state, args.lease_hours)
        state["summary"] = "已開工，可依下一步繼續。"
        steps = state.get("next_steps") or []
        if not steps or "Source" in steps[0] or "source" in steps[0]:
            steps = ["在本次任務中完成一個可驗證成果。"]
        if state["git"]["behind"]:
            steps.insert(0, f"遠端領先 {state['git']['behind']} commits；檢查本地變更後再決定是否 pull。")
        save_checkpoint(root, state, action="start", next_steps=steps, agent=args.agent)
        update_session_log(root, config, state, state["session_id"], "start")
        event = publish_hub_event(root, config, state, "start", state["session_id"])
        if event:
            state["connectors"]["hub"].update(
                status="PUBLISHED", external_id=event.name, note="Append-only start event",
            )
            save_checkpoint(root, state, action="start-published", next_steps=steps, agent=args.agent)
    show_status(root)


def pending_connectors(state: dict[str, Any]) -> list[str]:
    return [name for name, value in state["connectors"].items() if value["status"] == "PENDING_AGENT"]


def finish_project(root: Path, args: argparse.Namespace) -> None:
    ensure_authority(root)
    config = read_json(config_path(root))
    state = read_json(state_path(root))
    if not state:
        raise RuntimeError("Project is not initialized")
    with mutation_guard(root, "finish"):
        session_id = state.get("session_id") or str(uuid.uuid4())
        role = workspace_settings(config)["role"]
        if role == "hub":
            state["connectors"]["hub"].update(status="HUB_READY", note="Append-only hub event receiver")
        elif role == "child":
            state["connectors"]["hub"].update(status="READY", external_id="hub", note="Relative parent hub")
        state["session_id"] = session_id
        state["phase"] = "FINISHING"
        state["summary"] = "正在保存 checkpoint 與同步可用層級。"
        steps: list[str] = []
        if config.get("project_kind") == "skill-distribution":
            try:
                installed = install_managed_skills(DISTRIBUTION_ROOT, yes=args.yes, dry_run=args.dry_run)
                state["connectors"]["skills"].update(status="VERIFIED", note="; ".join(installed))
                dotfiles = sync_dotfiles(yes=args.yes, dry_run=args.dry_run, message="同步 Source pipeline 與相容技能")
                if dotfiles["status"] != "VERIFIED":
                    steps.append(dotfiles["detail"])
            except Exception as exc:  # keep checkpoint even when an optional layer fails
                state["connectors"]["skills"].update(status="BLOCKED", note=str(exc))
                steps.append(str(exc))
        if not args.skip_connectors:
            for name in ("obsidian", "notion", "cdn"):
                if config["connectors"][name]["enabled"]:
                    state["connectors"][name]["status"] = "PENDING_AGENT"
                    steps.append(f"完成 {name} connector，再執行 Source complete。")
                elif name == "cdn":
                    state["connectors"]["cdn"]["status"] = "NOT_CONFIGURED"
        pending = pending_connectors(state)
        final_phase = "AWAITING_EXTERNAL" if pending else "READY"
        state["phase"] = final_phase
        state["summary"] = f"本地收工完成；等待 connector：{', '.join(pending)}。" if pending else "收工完成，可安全換電腦、OS 或 Agent。"
        if not steps:
            steps = [f"完成 {name} connector。" for name in pending] if pending else ["下一台電腦執行 Source 即可自動開工。"]
        update_git_state(root, state)
        log_path = update_session_log(root, config, state, session_id, "finish", summary=state["summary"])
        proposals = publish_skill_proposals(root, config, state, session_id)
        save_checkpoint(root, state, action="finish-preflight", next_steps=steps, agent=args.agent)
        git_includes = list(dict.fromkeys([*(config.get("git", {}).get("include_paths") or []), *args.include]))
        relative_log = log_path.relative_to(root).as_posix()
        if relative_log not in git_includes:
            git_includes.append(relative_log)
        if not args.skip_git:
            first = git_finish(root, args.commit_message or f"收工：{state['project_name']}", git_includes, args.dry_run)
            if first["commit"]:
                state["git"]["last_push"] = first["commit"][:7]
                state["git"]["status"] = first["status"]
        state["session_id"] = None
        save_checkpoint(root, state, action="finish", next_steps=steps, agent=args.agent)
        event = publish_hub_event(root, config, state, "finish", session_id, proposals=proposals)
        if event:
            state["connectors"]["hub"].update(
                status="PUBLISHED", external_id=event.name, note="Append-only finish event",
            )
            save_checkpoint(root, state, action="finish-published", next_steps=steps, agent=args.agent)
        release_active_lease(root, session_id)
        if not args.skip_git:
            git_finish(root, "回填 Source 收工狀態", [], args.dry_run)
    show_status(root)


def complete_connector(root: Path, args: argparse.Namespace) -> None:
    ensure_authority(root)
    if not args.connector:
        raise RuntimeError("--connector is required")
    state = read_json(state_path(root))
    if not state:
        raise RuntimeError("Project is not initialized")
    state["connectors"][args.connector].update(
        status=args.connector_status, external_id=args.external_id, note=args.note,
    )
    pending = pending_connectors(state)
    state["phase"] = "AWAITING_EXTERNAL" if pending else "READY"
    state["summary"] = f"尚待 connector：{', '.join(pending)}。" if pending else "全部收工 connector 已完成。"
    steps = [f"完成 {name} connector。" for name in pending] if pending else ["下一台電腦執行 Source 即可自動開工。"]
    save_checkpoint(root, state, action=f"complete-{args.connector}", next_steps=steps, agent=args.agent)
    if not args.skip_git:
        git_finish(root, f"回填 {args.connector} connector 狀態", [], args.dry_run)
    show_status(root)


def doctor(root: Path) -> int:
    checks: list[tuple[str, str, str]] = [("platform", "PASS", f"{system_name()} (runtime-only)")]
    checks.append(("python", "PASS", f"{platform.python_version()} (runtime-only)"))
    for name in ("git", "gh", "chezmoi"):
        command = find_chezmoi() if name == "chezmoi" else shutil.which(name)
        status_value = "PASS" if command else ("BLOCKED" if name == "git" else "OPTIONAL_MISSING")
        checks.append((name, status_value, "runtime detected" if command else "not found"))
    for name, path in (
        ("config", config_path(root)), ("state", state_path(root)),
        ("authority", authority_path(root)), ("authority-signature", authority_signature_path(root)),
    ):
        checks.append((name, "PASS" if path.is_file() else "BLOCKED", path.relative_to(root).as_posix()))
    source_dir = root / ".source"
    if source_dir.exists():
        try:
            probe = source_dir / (".write-probe-" + uuid.uuid4().hex)
            probe.write_text("probe", encoding="utf-8")
            probe.unlink()
            checks.append(("state-write", "PASS", ".source generated layer is writable"))
        except OSError as exc:
            checks.append(("state-write", "BLOCKED", str(exc)))
    for filename, asset in (("source.ps1", "source.launcher.ps1"), ("source.sh", "source.launcher.sh")):
        launcher = root / filename
        template = ASSET_ROOT / asset
        if launcher.is_file() and template.is_file():
            checks.append((f"launcher:{filename}", "PASS" if sha256_file(launcher) == sha256_file(template) else "STALE", "matches canonical adapter"))
    for name, path in (("config", config_path(root)), ("state", state_path(root)), ("authority", authority_path(root))):
        if path.is_file():
            findings = has_absolute_path(read_json(path))
            checks.append((f"portable:{name}", "BLOCKED" if findings else "PASS", "persisted_absolute_path=0" if not findings else ", ".join(findings)))
    for status_value, detail in authority_check(root, require_locked=True):
        checks.append(("authority-gate", status_value, detail))
    current_config = read_json(config_path(root)) or {}
    workspace = workspace_settings(current_config)
    role = workspace.get("role")
    checks.append(("workspace-role", "PASS" if role in ("standalone", "hub", "child") else "BLOCKED", str(role)))
    for key in ("child_root", "logs_root", "event_root", "coordination_root"):
        try:
            safe_relative(str(workspace[key]), label=key)
            checks.append((f"portable:{key}", "PASS", str(workspace[key])))
        except RuntimeError as exc:
            checks.append((f"portable:{key}", "BLOCKED", str(exc)))
    if role == "child":
        hub_relative = workspace.get("hub_root")
        invalid_hub = not hub_relative or Path(str(hub_relative)).is_absolute()
        checks.append(("child-hub-root", "BLOCKED" if invalid_hub else "PASS", str(hub_relative)))
    if role == "hub":
        ignored = (root / ".gitignore").read_text(encoding="utf-8-sig") if (root / ".gitignore").is_file() else ""
        for pattern in (".source/coordination/", "projects/*/"):
            checks.append((f"gitignore:{pattern}", "PASS" if pattern in ignored else "BLOCKED", "cloud/Git isolation rule"))
        event_ids: list[str] = []
        malformed = 0
        event_root = root / workspace["event_root"]
        for path in event_root.rglob("*.json") if event_root.is_dir() else []:
            event = read_json(path) or {}
            if not event.get("event_id") or path.stem.split("-")[-1] != event.get("event_id"):
                malformed += 1
            event_ids.append(event.get("event_id"))
        unique = len(event_ids) == len(set(event_ids)) and malformed == 0
        checks.append(("hub-events", "PASS" if unique else "BLOCKED", f"append_only_unique={len(event_ids)}"))
    requires_github_auth = bool((current_config.get("git") or {}).get("remote"))
    if command_exists("gh") and requires_github_auth:
        auth = run(["gh", "auth", "status"], check=False)
        checks.append(("github-auth", "PASS" if auth.returncode == 0 else "BLOCKED", "runtime credential check"))
    width = max(len(item[0]) for item in checks)
    for name, status_value, detail in checks:
        print(f"{name:<{width}}  {status_value:<16} {detail}")
    if state_path(root).is_file():
        print()
        show_status(root)
    return 1 if any(status_value == "BLOCKED" for _, status_value, _ in checks) else 0


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Cross-platform Source project lifecycle")
    parser.add_argument("positional_action", nargs="?", choices=ACTIONS)
    parser.add_argument("--action", choices=ACTIONS, default=None)
    parser.add_argument("--project-root", default=os.getcwd())
    parser.add_argument("--project-name")
    parser.add_argument("--workspace-role", choices=("standalone", "hub", "child"), default="standalone")
    parser.add_argument("--hub-root")
    parser.add_argument("--child-name")
    parser.add_argument("--child-path")
    parser.add_argument("--lease-hours", type=int, default=12)
    parser.add_argument("--agent", default="Agent")
    parser.add_argument("--commit-message")
    parser.add_argument("--include", action="append", default=[])
    parser.add_argument("--connector", choices=("notion", "obsidian", "cdn"))
    parser.add_argument("--connector-status", choices=("VERIFIED", "PARTIAL", "BLOCKED", "SKIPPED"), default="VERIFIED")
    parser.add_argument("--external-id")
    parser.add_argument("--note")
    parser.add_argument("--yes", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--skip-git", action="store_true")
    parser.add_argument("--skip-connectors", action="store_true")
    parser.add_argument("--create-remote", action="store_true")
    args = parser.parse_args(argv)
    args.action = args.action or args.positional_action or "auto"
    return args


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    if args.lease_hours < 1 or args.lease_hours > 168:
        print("BLOCKED: --lease-hours must be between 1 and 168", file=sys.stderr)
        return 1
    root = resolve_root(args.project_root, args.action in ("init", "bootstrap", "hub-init"))
    try:
        if args.action == "auto":
            state = read_json(state_path(root))
            args.action = "init" if not state else ("start" if state.get("phase") == "READY" else "next")
        if args.action == "bootstrap":
            for result in install_managed_skills(DISTRIBUTION_ROOT, yes=args.yes, dry_run=args.dry_run):
                print(result)
            initialize(root, args)
        elif args.action == "init":
            initialize(root, args)
        elif args.action == "hub-init":
            args.workspace_role = "hub"
            initialize(root, args)
            if state_path(root).is_file() and not args.dry_run:
                ensure_git_identity(root)
                config = read_json(config_path(root))
                git_finish(
                    root, f"初始化 Source 主幹：{config['project_name']}",
                    config.get("git", {}).get("include_paths") or [], args.dry_run,
                )
        elif args.action == "child-create":
            with mutation_guard(root, "child-create"):
                child_create(root, args)
        elif args.action == "hub-status":
            hub_status(root)
        elif args.action == "hub-sync":
            hub_sync(root, args)
        elif args.action in ("status", "next"):
            show_status(root)
        elif args.action == "start":
            start_project(root, args)
        elif args.action == "finish":
            finish_project(root, args)
        elif args.action == "doctor":
            return doctor(root)
        elif args.action == "deploy-skills":
            for result in install_managed_skills(DISTRIBUTION_ROOT, yes=args.yes, dry_run=args.dry_run):
                print(result)
        elif args.action == "sync-dotfiles":
            result = sync_dotfiles(yes=args.yes, dry_run=args.dry_run, message="同步 Source pipeline 與共用 Agent 核心")
            print(f"{result['status']}: {result['detail']}")
        elif args.action in ("skills-check", "skills-update"):
            ensure_authority(root)
            config = read_json(config_path(root))
            state = read_json(state_path(root))
            if args.action == "skills-update":
                with mutation_guard(root, "skills-update"):
                    result = approved_skill_status(root, config, state, apply=True)
                    save_checkpoint(
                        root, state, action="skills-update",
                        next_steps=state.get("next_steps"), agent=args.agent,
                    )
            else:
                result = approved_skill_status(root, config, state, apply=False)
            print(f"SKILLS: {result['status']} {result['detail']}")
            return 1 if result["status"] == "BLOCKED" else 0
        elif args.action == "connector-bootstrap":
            connector_bootstrap(root, args)
        elif args.action == "complete":
            complete_connector(root, args)
        elif args.action == "authority-check":
            issues = authority_check(root, require_locked=True)
            for status_value, detail in issues:
                print(f"{status_value}: {detail}")
            return 1 if any(status_value in ("BLOCKED", "LOCK_DRIFT") for status_value, _ in issues) else 0
        elif args.action == "authority-lock":
            authority_lock(root)
            print("AUTHORITY LOCKED")
        elif args.action == "authority-unlock":
            authority_unlock(root, yes=args.yes, agent=args.agent)
        elif args.action == "authority-seal":
            authority_seal(root, yes=args.yes, agent=args.agent)
        return 0
    except Exception as exc:
        print(f"BLOCKED: {sanitize_text(str(exc), root)}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
