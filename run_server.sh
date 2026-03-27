#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SCRIPT_DIR/.venv"
PYTHON_BIN=""
REQ_FILE="$SCRIPT_DIR/requirements.txt"
REQ_HASH_FILE="$VENV_DIR/.requirements.sha256"

# Detect platform: "mac", "win" (Git Bash / MSYS / Cygwin), or "linux"
detect_platform() {
  case "$(uname -s)" in
    Darwin*)  echo "mac" ;;
    MINGW*|MSYS*|CYGWIN*) echo "win" ;;
    Linux*)
      if grep -qi microsoft /proc/version 2>/dev/null; then
        echo "win"
      else
        echo "linux"
      fi
      ;;
    *) echo "unknown" ;;
  esac
}

PLATFORM="$(detect_platform)"

log() {
  echo "[illustrator-mcp] $1"
}

to_windows_path() {
  local input_path="$1"

  if command -v cygpath >/dev/null 2>&1; then
    cygpath -w "$input_path"
    return 0
  fi

  if command -v wslpath >/dev/null 2>&1; then
    wslpath -w "$input_path"
    return 0
  fi

  echo "$input_path"
}

# Return the path to the Python binary inside the venv
venv_python() {
  if [ "$PLATFORM" = "win" ]; then
    echo "$VENV_DIR/Scripts/python.exe"
  else
    echo "$VENV_DIR/bin/python3"
  fi
}

find_python() {
  local venv_py
  venv_py="$(venv_python)"

  if [ -x "$venv_py" ]; then
    PYTHON_BIN="$venv_py"
    return 0
  fi

  if command -v python3 >/dev/null 2>&1; then
    PYTHON_BIN="$(command -v python3)"
    return 0
  fi

  if command -v python >/dev/null 2>&1; then
    PYTHON_BIN="$(command -v python)"
    return 0
  fi

  if [ "$PLATFORM" = "win" ] && command -v py >/dev/null 2>&1; then
    PYTHON_BIN="py -3"
    return 0
  fi

  return 1
}

ensure_venv() {
  local venv_py
  venv_py="$(venv_python)"

  if [ ! -x "$venv_py" ]; then
    log "Creating virtual environment in .venv"
    if command -v python3 >/dev/null 2>&1; then
      python3 -m venv "$VENV_DIR"
    elif command -v python >/dev/null 2>&1; then
      python -m venv "$VENV_DIR"
    elif [ "$PLATFORM" = "win" ] && command -v py >/dev/null 2>&1; then
      py -3 -m venv "$VENV_DIR"
    else
      log "Python was not found. Install Python 3.12+ and retry."
      exit 1
    fi
  fi

  PYTHON_BIN="$venv_py"
}

requirements_hash() {
  if command -v sha256sum >/dev/null 2>&1; then
    sha256sum "$REQ_FILE" | awk '{print $1}'
  elif command -v shasum >/dev/null 2>&1; then
    shasum -a 256 "$REQ_FILE" | awk '{print $1}'
  else
    $PYTHON_BIN -c "import hashlib,sys; print(hashlib.sha256(open(sys.argv[1],'rb').read()).hexdigest())" "$REQ_FILE"
  fi
}

has_pip() {
  $PYTHON_BIN -m pip --version >/dev/null 2>&1
}

ensure_pip() {
  if has_pip; then
    return 0
  fi

  log "pip not found in .venv. Bootstrapping with ensurepip..."
  if ! $PYTHON_BIN -m ensurepip --upgrade >/dev/null 2>&1; then
    log "Failed to bootstrap pip. Please install pip for this Python and retry."
    exit 1
  fi

  if ! has_pip; then
    log "pip is still unavailable after ensurepip."
    exit 1
  fi
}

requirements_ok() {
  local expected_hash current_hash

  if [ ! -f "$REQ_HASH_FILE" ]; then
    return 1
  fi

  expected_hash="$(cat "$REQ_HASH_FILE" 2>/dev/null || true)"
  current_hash="$(requirements_hash)"

  if [ "$expected_hash" != "$current_hash" ]; then
    return 1
  fi

  if ! has_pip; then
    return 1
  fi

  if ! $PYTHON_BIN -m pip check >/dev/null 2>&1; then
    return 1
  fi

  # Validate key runtime imports (platform-appropriate)
  if [ "$PLATFORM" = "win" ]; then
    if ! $PYTHON_BIN -c "import mcp, PIL, win32com.client" >/dev/null 2>&1; then
      return 1
    fi
  else
    if ! $PYTHON_BIN -c "import mcp, PIL" >/dev/null 2>&1; then
      return 1
    fi
  fi

  return 0
}

install_requirements() {
  local req_file_path="$REQ_FILE"

  if [ "$PLATFORM" = "win" ]; then
    req_file_path="$(to_windows_path "$REQ_FILE")"
  fi

  ensure_pip
  log "Installing dependencies from requirements.txt"
  $PYTHON_BIN -m pip install --upgrade pip
  $PYTHON_BIN -m pip install -r "$req_file_path"
  requirements_hash > "$REQ_HASH_FILE"
}

main() {
  log "Detected platform: $PLATFORM"

  ensure_venv
  ensure_pip

  if requirements_ok; then
    log "Dependencies are already satisfied. Skipping install."
  else
    install_requirements
  fi

  local server_path="$SCRIPT_DIR/illustrator/server.py"
  if [ "$PLATFORM" = "win" ]; then
    server_path="$(to_windows_path "$server_path")"
  fi

  log "Starting Illustrator MCP server..."
  log "To stop the server, press Ctrl+C in this terminal."
  exec $PYTHON_BIN "$server_path"
}

main "$@"
