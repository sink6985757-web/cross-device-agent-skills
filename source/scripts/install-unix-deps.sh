#!/usr/bin/env sh
set -eu

if [ "${1:-}" != "--yes" ]; then
  echo "BLOCKED: dependency installation changes the OS; pass --yes." >&2
  exit 1
fi

run_admin() {
  if [ "$(id -u)" -eq 0 ]; then "$@"; else sudo "$@"; fi
}

case "$(uname -s)" in
  Linux)
    if command -v apt-get >/dev/null 2>&1; then
      run_admin apt-get update
      run_admin apt-get install -y python3 git curl
      run_admin apt-get install -y gh chezmoi || true
    elif command -v dnf >/dev/null 2>&1; then
      run_admin dnf install -y python3 git curl gh chezmoi || run_admin dnf install -y python3 git curl
    elif command -v pacman >/dev/null 2>&1; then
      run_admin pacman -Sy --needed --noconfirm python git curl github-cli chezmoi
    elif command -v zypper >/dev/null 2>&1; then
      run_admin zypper --non-interactive install python3 git curl gh chezmoi || run_admin zypper --non-interactive install python3 git curl
    elif command -v apk >/dev/null 2>&1; then
      run_admin apk add python3 git curl github-cli chezmoi || run_admin apk add python3 git curl
    else
      echo "BLOCKED: unsupported Linux package manager; install Python 3 and Git, then resume." >&2
      exit 1
    fi
    ;;
  Darwin)
    if ! command -v brew >/dev/null 2>&1; then
      NONINTERACTIVE=1 bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
      for candidate in /opt/homebrew/bin/brew /usr/local/bin/brew; do
        if [ -x "$candidate" ]; then BREW="$candidate"; break; fi
      done
    else
      BREW=$(command -v brew)
    fi
    if [ -z "${BREW:-}" ]; then
      echo "BLOCKED: Homebrew installed but is not discoverable; add brew to PATH and resume." >&2
      exit 1
    fi
    "$BREW" install python git gh chezmoi
    ;;
  *)
    echo "BLOCKED: supported systems are Linux and macOS." >&2
    exit 1
    ;;
esac

echo "DEPENDENCIES READY: Python 3 and Git are installed; gh and chezmoi are verified later by Source doctor."
