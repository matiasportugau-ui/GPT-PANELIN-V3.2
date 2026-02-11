#!/usr/bin/env bash
#
# boot.sh - BOOT (Bootstrap, Operations, Orchestration, and Testing) orchestrator
#
# This script initializes the GPT-PANELIN system with idempotent, secure execution.
# Features:
# - Secure logfile with rotation
# - Lock mechanism to prevent concurrent runs
# - Environment activation with validation
# - Error handling with clear exit codes
# - No secrets logged
#
# Exit codes:
#   0 - Success
#   1 - General error
#   2 - Lock acquisition failure
#   3 - Python environment error
#   4 - Preload script error

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOGFILE="${SCRIPT_DIR}/.boot-log"
LOCKFILE="${SCRIPT_DIR}/.boot-lock"
READY_FLAG="${SCRIPT_DIR}/.boot-ready"
MAX_LOGFILE_SIZE=$((5 * 1024 * 1024))  # 5MB
PYTHON_CMD="${PYTHON_CMD:-python3}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Logging function - sanitizes sensitive data
log() {
    local level="$1"
    shift
    local message="$*"
    # Remove potential secrets from log messages
    message=$(echo "$message" | sed -E 's/(key|token|secret|password)=[^ ]*/\1=***REDACTED***/gi')
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] [$level] $message" >> "$LOGFILE"
    if [[ "$level" == "ERROR" ]]; then
        echo -e "${RED}[$level]${NC} $message" >&2
    elif [[ "$level" == "WARN" ]]; then
        echo -e "${YELLOW}[$level]${NC} $message" >&2
    else
        echo -e "${GREEN}[$level]${NC} $message"
    fi
}

# Initialize secure logfile
init_logfile() {
    if [[ ! -f "$LOGFILE" ]]; then
        touch "$LOGFILE"
        chmod 600 "$LOGFILE"
        log "INFO" "Created secure logfile: $LOGFILE"
    else
        # Check if rotation is needed
        local logsize=$(stat -f%z "$LOGFILE" 2>/dev/null || stat -c%s "$LOGFILE" 2>/dev/null || echo 0)
        if [[ $logsize -gt $MAX_LOGFILE_SIZE ]]; then
            local backup="${LOGFILE}.old"
            mv "$LOGFILE" "$backup"
            touch "$LOGFILE"
            chmod 600 "$LOGFILE"
            log "INFO" "Rotated logfile (old size: $logsize bytes)"
        fi
    fi
}

# Acquire lock to prevent concurrent execution
acquire_lock() {
    local max_wait=30
    local waited=0
    
    while [[ -f "$LOCKFILE" ]]; do
        if [[ $waited -ge $max_wait ]]; then
            log "ERROR" "Lock file exists after ${max_wait}s. Another boot.sh may be running."
            log "ERROR" "If this is a stale lock, remove: $LOCKFILE"
            exit 2
        fi
        log "WARN" "Waiting for lock... ($waited/$max_wait seconds)"
        sleep 1
        waited=$((waited + 1))
    done
    
    # Create lock file with PID
    echo $$ > "$LOCKFILE"
    log "INFO" "Lock acquired (PID: $$)"
}

# Release lock
release_lock() {
    if [[ -f "$LOCKFILE" ]]; then
        rm -f "$LOCKFILE"
        log "INFO" "Lock released"
    fi
}

# Cleanup on exit
cleanup() {
    local exit_code=$?
    release_lock
    if [[ $exit_code -ne 0 ]]; then
        log "ERROR" "Boot process failed with exit code: $exit_code"
    fi
    exit $exit_code
}

trap cleanup EXIT INT TERM

# Check Python environment
check_python() {
    log "INFO" "Checking Python environment..."
    
    if ! command -v "$PYTHON_CMD" &> /dev/null; then
        log "ERROR" "Python command not found: $PYTHON_CMD"
        exit 3
    fi
    
    local py_version=$($PYTHON_CMD --version 2>&1)
    log "INFO" "Using Python: $py_version"
    
    # Check if we should activate a virtual environment
    local venv_dirs=("venv" ".venv" "env")
    for venv in "${venv_dirs[@]}"; do
        if [[ -f "${SCRIPT_DIR}/${venv}/bin/activate" ]]; then
            log "INFO" "Found virtual environment: $venv"
            # shellcheck disable=SC1090
            source "${SCRIPT_DIR}/${venv}/bin/activate"
            log "INFO" "Activated virtual environment"
            PYTHON_CMD="python"  # Use venv python
            break
        fi
    done
}

# Install/upgrade pip dependencies
install_dependencies() {
    log "INFO" "Checking Python dependencies..."
    
    if [[ -f "${SCRIPT_DIR}/requirements.txt" ]]; then
        log "INFO" "Installing dependencies from requirements.txt..."
        if $PYTHON_CMD -m pip install --quiet --upgrade pip; then
            log "INFO" "Upgraded pip successfully"
        else
            log "WARN" "Could not upgrade pip (may not be critical)"
        fi
        
        if $PYTHON_CMD -m pip install --quiet -r "${SCRIPT_DIR}/requirements.txt"; then
            log "INFO" "Dependencies installed successfully"
        else
            log "ERROR" "Failed to install dependencies"
            exit 3
        fi
    else
        log "WARN" "No requirements.txt found, skipping dependency installation"
    fi
}

# Run boot_preload.py
run_preload() {
    log "INFO" "Running boot_preload.py..."
    
    local preload_script="${SCRIPT_DIR}/boot_preload.py"
    if [[ ! -f "$preload_script" ]]; then
        log "ERROR" "Preload script not found: $preload_script"
        exit 4
    fi
    
    # Pass environment variables but sanitize logs
    if $PYTHON_CMD "$preload_script"; then
        log "INFO" "Preload completed successfully"
    else
        local exit_code=$?
        log "ERROR" "Preload failed with exit code: $exit_code"
        exit 4
    fi
}

# Create ready flag
create_ready_flag() {
    local timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    cat > "$READY_FLAG" <<EOF
{
  "status": "ready",
  "timestamp": "$timestamp",
  "boot_version": "1.0.0",
  "python_version": "$($PYTHON_CMD --version 2>&1)"
}
EOF
    log "INFO" "Boot ready flag created: $READY_FLAG"
}

# Main execution
main() {
    echo "========================================="
    echo "  BOOT - Bootstrap, Operations, Orchestration, Testing"
    echo "========================================="
    echo ""
    
    init_logfile
    acquire_lock
    
    log "INFO" "Starting BOOT process..."
    log "INFO" "Working directory: $SCRIPT_DIR"
    
    check_python
    install_dependencies
    run_preload
    create_ready_flag
    
    log "INFO" "BOOT process completed successfully!"
    echo ""
    echo -e "${GREEN}✓${NC} BOOT completed successfully"
    echo "  Log: $LOGFILE"
    echo "  Ready flag: $READY_FLAG"
    echo ""
    
    exit 0
}

main "$@"
