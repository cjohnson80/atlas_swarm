#!/bin/bash
set -euo pipefail
umask 077

if [ -z "${AGENT_ROOT:-}" ]; then
    echo "ERROR: AGENT_ROOT is not set." >&2
    exit 1
fi

while [[ "$AGENT_ROOT" == */ ]] && [[ "$AGENT_ROOT" != "/" ]]; do
    AGENT_ROOT="${AGENT_ROOT%/}"
done

if [[ "$AGENT_ROOT" != /* ]]; then
    echo "ERROR: AGENT_ROOT must be an absolute path." >&2
    exit 1
fi

get_stat() {
    local target="$1"
    if stat -c "%u %a" "$target" >/dev/null 2>&1; then
        stat -c "%u %a" "$target"
    else
        stat -f "%u %Lp" "$target"
    fi
}

if [ -L "$AGENT_ROOT" ]; then
    echo "ERROR: AGENT_ROOT ($AGENT_ROOT) cannot be a symlink." >&2
    exit 1
fi

if [ ! -d "$AGENT_ROOT" ]; then
    echo "ERROR: AGENT_ROOT ($AGENT_ROOT) does not exist or is not a directory." >&2
    exit 1
fi

CURRENT_UID=$(id -u)

ROOT_STAT=$(get_stat "$AGENT_ROOT")
ROOT_OWNER="${ROOT_STAT% *}"
ROOT_PERM="${ROOT_STAT#* }"

if [ "$ROOT_OWNER" != "$CURRENT_UID" ]; then
    echo "ERROR: AGENT_ROOT ($AGENT_ROOT) is not owned by current user ($CURRENT_UID)." >&2
    exit 1
fi

if [ "$ROOT_PERM" != "700" ] && [ "$ROOT_PERM" != "0700" ]; then
    echo "ERROR: AGENT_ROOT ($AGENT_ROOT) must have 700 permissions." >&2
    exit 1
fi

CRITICAL_DIRS=("bin" "core" "logs" "workspace" "mailbox")
NON_CRITICAL_DIRS=("memory" "data" "tmp")

process_dir() {
    local dir_name="$1"
    local is_critical="$2"
    local dir_path="$AGENT_ROOT/$dir_name"
    local CURRENT_UID
    CURRENT_UID=$(id -u)

    if [ -e "$dir_path" ] || [ -L "$dir_path" ]; then
        if [ -L "$dir_path" ]; then
            echo "ERROR: Directory $dir_path is a symlink. Symlinks are strictly forbidden." >&2
            exit 1
        fi
        if [ ! -d "$dir_path" ]; then
            echo "ERROR: $dir_path exists but is not a directory." >&2
            exit 1
        fi

        local D_STAT
        D_STAT=$(get_stat "$dir_path")
        local D_OWNER="${D_STAT% *}"
        local D_PERM="${D_STAT#* }"

        if [ "$D_OWNER" != "$CURRENT_UID" ]; then
            echo "ERROR: $dir_path is not owned by current user ($CURRENT_UID)." >&2
            exit 1
        fi

        if [ "$D_PERM" != "700" ] && [ "$D_PERM" != "0700" ]; then
            chmod 700 "$dir_path"
        fi
    else
        if [[ "$is_critical" == "true" ]]; then
            echo "ERROR: Critical directory $dir_path is missing." >&2
            exit 1
        else
            mkdir -m 700 "$dir_path"
        fi
    fi
}

for d in "${CRITICAL_DIRS[@]}"; do
    process_dir "$d" "true"
done

for d in "${NON_CRITICAL_DIRS[@]}"; do
    process_dir "$d" "false"
done

echo "Environment validation passed successfully."
