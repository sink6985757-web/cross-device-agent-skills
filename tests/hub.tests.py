#!/usr/bin/env python3
"""Disposable hub/child, cloud-concurrency, and append-only event test."""

from __future__ import annotations

import datetime as dt
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
    env = dict(os.environ)
    env["SOURCE_DISABLE_NETWORK"] = "1"
    result = subprocess.run(
        [str(item) for item in args], cwd=str(cwd) if cwd else None,
        text=True, encoding="utf-8", errors="replace", capture_output=True, env=env,
    )
    if result.returncode != expect:
        raise AssertionError(
            f"exit={result.returncode}, expected={expect}\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}"
        )
    return result


def source(root: Path, action: str, *extra: str, expect: int = 0) -> subprocess.CompletedProcess[str]:
    return run(
        sys.executable, ENGINE, "--action", action, "--project-root", root,
        "--agent", "HubTest", *extra, expect=expect,
    )


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def assert_portable(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    assert not re.search(r"(?i)(?<![A-Za-z0-9+.-])[A-Z]:[\\/]", text), path
    assert not re.search(r"/(?:home|Users)/[^\s\"]+", text), path


def main() -> None:
    hub = Path(tempfile.mkdtemp(prefix="source-hub-"))
    try:
        source(hub, "hub-init", "--project-name", "Portable Hub")
        hub_config = load(hub / ".source" / "config.json")
        assert hub_config["workspace"]["role"] == "hub"
        assert "projects/*/" in (hub / ".gitignore").read_text(encoding="utf-8")
        assert int(run("git", "-C", hub, "rev-list", "--count", "HEAD").stdout) == 1

        source(hub, "child-create", "--child-name", "Alpha Project")
        source(hub, "child-create", "--child-name", "Beta Project")
        alpha = hub / "projects" / "alpha-project"
        beta = hub / "projects" / "beta-project"
        descriptors = sorted((hub / ".source" / "hub" / "projects").glob("*.json"))
        assert len(descriptors) == 2
        alpha_config = load(alpha / ".source" / "config.json")
        beta_config = load(beta / ".source" / "config.json")
        assert alpha_config["workspace"]["role"] == "child"
        assert alpha_config["workspace"]["hub_root"] == "../.."
        assert beta_config["workspace"]["hub_root"] == "../.."
        assert (alpha / "knowledge" / "obsidian" / "Project Log.md").is_file()
        assert load(alpha / ".source" / "connectors" / "notion.json")["status"] == "NEEDS_SETUP"
        assert int(run("git", "-C", alpha, "rev-list", "--count", "HEAD").stdout) == 1

        source(alpha, "start")
        alpha_working = load(alpha / ".source" / "state.json")
        alpha_session = alpha_working["session_id"]
        assert alpha_working["phase"] == "WORKING"
        assert (alpha / ".source" / "coordination" / "active.lock" / "lease.json").is_file()
        assert (alpha / "logs" / "sessions" / f"{alpha_session}.json").is_file()

        mutation = alpha / ".source" / "coordination" / "mutation.lock"
        mutation.mkdir(parents=True)
        expires = (dt.datetime.now(dt.timezone.utc) + dt.timedelta(minutes=10)).replace(microsecond=0).isoformat().replace("+00:00", "Z")
        (mutation / "lease.json").write_text(
            json.dumps({"action": "other-writer", "expires_at": expires}), encoding="utf-8",
        )
        blocked = source(alpha, "finish", "--skip-connectors", "--skip-git", expect=1)
        assert "Concurrent Source mutation" in blocked.stderr
        shutil.rmtree(mutation)

        skill = alpha / "skills" / "alpha-helper"
        skill.mkdir(parents=True)
        (skill / "SKILL.md").write_text(
            "---\nname: alpha-helper\ndescription: Test proposal only.\n---\n\n# Alpha Helper\n",
            encoding="utf-8", newline="\n",
        )
        source(alpha, "finish", "--skip-connectors", "--include", "skills")
        alpha_done = load(alpha / ".source" / "state.json")
        assert alpha_done["phase"] == "READY" and alpha_done["session_id"] is None
        assert not (alpha / ".source" / "coordination" / "active.lock").exists()
        proposals = list((hub / ".source" / "hub" / "skill-proposals").rglob("proposal.json"))
        assert len(proposals) == 1 and load(proposals[0])["status"] == "REVIEW_REQUIRED"

        source(beta, "start")
        beta_session = load(beta / ".source" / "state.json")["session_id"]
        assert beta_session != alpha_session
        source(beta, "finish", "--skip-connectors")
        assert (beta / "logs" / "sessions" / f"{beta_session}.json").is_file()

        status = source(hub, "hub-status")
        assert "projects=2" in status.stdout and "Alpha Project" in status.stdout and "Beta Project" in status.stdout
        event_files = list((hub / ".source" / "hub" / "events").rglob("*.json"))
        event_ids = [load(item)["event_id"] for item in event_files]
        assert len(event_files) >= 6 and len(event_ids) == len(set(event_ids))
        source(hub, "hub-sync", "--commit-message", "sync disposable child events")
        assert not run("git", "-C", hub, "status", "--porcelain").stdout.strip()
        assert int(run("git", "-C", hub, "rev-list", "--count", "HEAD").stdout) == 2
        source(hub, "doctor")
        source(alpha, "doctor")
        source(beta, "doctor")

        for path in (
            hub / ".source" / "config.json", hub / ".source" / "state.json",
            alpha / ".source" / "config.json", alpha / ".source" / "state.json",
            beta / ".source" / "config.json", beta / ".source" / "state.json",
            *event_files,
        ):
            assert_portable(path)

        print("PASS: hub init -> isolated children -> lease block -> logs -> proposals -> append-only hub sync")
    finally:
        shutil.rmtree(hub, ignore_errors=True)


if __name__ == "__main__":
    main()
