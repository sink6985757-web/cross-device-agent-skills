#!/usr/bin/env python3
"""Disposable cross-platform Source lifecycle test."""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


REPO = Path(__file__).resolve().parent.parent
ENGINE = REPO / "source" / "scripts" / "source.py"


def run(*args: str | Path, cwd: Path | None = None, expect: int = 0) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        [str(item) for item in args], cwd=str(cwd) if cwd else None,
        text=True, encoding="utf-8", errors="replace", capture_output=True,
    )
    if result.returncode != expect:
        raise AssertionError(
            f"exit={result.returncode}, expected={expect}\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}"
        )
    return result


def source(root: Path, action: str, *extra: str, expect: int = 0) -> subprocess.CompletedProcess[str]:
    return run(
        sys.executable, ENGINE, "--action", action, "--project-root", root,
        "--agent", "CrossPlatformTest", *extra, expect=expect,
    )


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def save(path: Path, value: dict) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


def main() -> None:
    root = Path(tempfile.mkdtemp(prefix="source-cross-platform-"))
    try:
        (root / "SOURCE.md").write_text("SENTINEL\n", encoding="utf-8", newline="\n")
        source(root, "init", "--project-name", "Source Cross Platform")
        assert (root / "SOURCE.md").read_text(encoding="utf-8").strip() == "SENTINEL"
        assert (root / "source.ps1").is_file() and (root / "source.sh").is_file()
        assert (root / ".source" / "authority.json").is_file()
        assert (root / ".source" / "authority.sha256").is_file()
        assert source(root, "authority-check").returncode == 0

        initial = load(root / ".source" / "state.json")
        assert initial["phase"] == "READY"
        assert "device" not in initial["actor"]
        source(root, "start")
        working = load(root / ".source" / "state.json")
        session = working["session_id"]
        revision = working["revision"]
        source(root, "auto")
        resumed = load(root / ".source" / "state.json")
        assert resumed["revision"] == revision and resumed["session_id"] == session

        resumed["connectors"]["notion"]["status"] = "PENDING_AGENT"
        save(root / ".source" / "state.json", resumed)
        run("git", "-C", root, "config", "user.name", "Source Test")
        run("git", "-C", root, "config", "user.email", "source-test@example.invalid")
        includes = [
            ".source", "SOURCE.md", "AGENTS.md", "handoff.md", "source.ps1",
            "source.sh", ".gitignore", ".gitattributes",
        ]
        finish_args: list[str] = ["--skip-connectors", "--commit-message", "cross-platform lifecycle"]
        for item in includes:
            finish_args.extend(("--include", item))
        result = source(root, "finish", *finish_args)
        assert "完成 notion connector" in result.stdout, result.stdout
        awaiting = load(root / ".source" / "state.json")
        assert awaiting["phase"] == "AWAITING_EXTERNAL"

        source(
            root, "complete", "--connector", "notion", "--connector-status", "VERIFIED",
            "--note", r"runtime C:\Users\Example\secret and /home/example/secret",
        )
        finished = load(root / ".source" / "state.json")
        assert finished["phase"] == "READY"
        serialized = json.dumps(finished, ensure_ascii=False)
        assert not re.search(r"(?i)[A-Z]:[\\/]", serialized)
        assert "/home/example" not in serialized
        assert not run("git", "-C", root, "status", "--porcelain").stdout.strip()
        assert int(run("git", "-C", root, "rev-list", "--count", "HEAD").stdout) == 3
        assert source(root, "doctor").returncode == 0

        source(root, "authority-unlock", "--yes")
        with (root / "SOURCE.md").open("a", encoding="utf-8", newline="\n") as handle:
            handle.write("FORMAL CHANGE\n")
        source(root, "authority-check", expect=1)
        source(root, "authority-seal", "--yes")
        source(root, "authority-check")

        for canonical in ("config.json", "state.json", "authority.json"):
            text = (root / ".source" / canonical).read_text(encoding="utf-8")
            assert not re.search(r"(?i)[A-Z]:[\\/]", text)
            assert not re.search(r"/(?:home|Users)/[^\s\"]+", text)

        print("PASS: init -> lock -> start -> interrupted resume -> finish -> connector -> path scrub -> unlock/seal")
    finally:
        def remove_error(function, path, _exc):
            os.chmod(path, 0o700)
            function(path)

        shutil.rmtree(root, onerror=remove_error)


if __name__ == "__main__":
    main()
