#!/usr/bin/env sh
set -eu

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
LOCAL_ENGINE="$SCRIPT_DIR/source/scripts/source.py"
GLOBAL_ENGINE="${HOME}/.agents/skills/source/scripts/source.py"

if [ -f "$LOCAL_ENGINE" ]; then
  ENGINE="$LOCAL_ENGINE"
elif [ -f "$GLOBAL_ENGINE" ]; then
  ENGINE="$GLOBAL_ENGINE"
else
  echo "BLOCKED: Source engine is not installed. Clone the private distribution repo, then run its source.sh bootstrap." >&2
  exit 1
fi

if ! command -v python3 >/dev/null 2>&1; then
  case " $* " in
    *" --yes "*) sh "$(dirname "$ENGINE")/install-unix-deps.sh" --yes ;;
    *) echo "BLOCKED: Python 3 is required. Re-run with --yes for the supported package-manager installer." >&2; exit 1 ;;
  esac
fi

exec python3 "$ENGINE" "$@"
