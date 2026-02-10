# BOOT Architecture Documentation

## Overview

The BOOT (Bootstrap, Operations, Orchestration, and Testing) architecture provides a standardized, secure, and idempotent initialization process for the Panelin GPT system. This document describes the BOOT flow, artifacts, error handling, and integration patterns.

**Version:** 1.0  
**Last Updated:** 2026-02-10

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [BOOT Flow Diagram](#boot-flow-diagram)
3. [Components](#components)
4. [Environment Variables](#environment-variables)
5. [Artifacts](#artifacts)
6. [Error States & Remediation](#error-states--remediation)
7. [Security Considerations](#security-considerations)
8. [Integration Patterns](#integration-patterns)
9. [Testing](#testing)

---

## Architecture Overview

The BOOT architecture follows these principles:

- **Idempotent**: Safe to run multiple times; subsequent runs detect completion and skip
- **Secure**: No secrets written to logs or committed files
- **Observable**: Comprehensive logging with timestamps; clear readiness signaling
- **Fail-Fast**: Explicit validation of environment and dependencies before operations
- **Configurable**: Supports multiple runtimes (local Python, Docker, CI/CD)

### Design Goals

1. Standardize initialization across development, staging, and production
2. Enable safe automated deployments without manual intervention
3. Provide clear observability into system readiness
4. Support knowledge base indexing and optional embedding generation
5. Maintain security by design (no secret leakage)

---

## BOOT Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     BOOT Process Start                       │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
          ┌──────────────────────────────┐
          │  Check .boot-ready exists?   │
          └──────────┬───────────────────┘
                     │
         ┌───────────┴───────────┐
         │ Yes                   │ No
         ▼                       ▼
  ┌─────────────┐      ┌──────────────────┐
  │ Exit (skip) │      │ Rotate log if    │
  │ unless      │      │ size > limit     │
  │ --force     │      └────────┬─────────┘
  └─────────────┘               │
                                ▼
                       ┌────────────────────┐
                       │ Environment        │
                       │ Validation         │
                       │  - Check writable  │
                       │  - Check Python    │
                       │  - Check files     │
                       │  - Warn if no key  │
                       └────────┬───────────┘
                                │
                     ┌──────────┴──────────┐
                     │ Success             │ Failure
                     ▼                     ▼
            ┌──────────────────┐  ┌────────────────┐
            │ Install          │  │ Exit with      │
            │ Dependencies     │  │ error code 1-4 │
            │  - Create venv   │  └────────────────┘
            │  - Install reqs  │
            └────────┬─────────┘
                     │
                     ▼
            ┌──────────────────┐
            │ Validate Files   │
            │  - Run validate_ │
            │    gpt_files.py  │
            └────────┬─────────┘
                     │
                     ▼
            ┌──────────────────┐
            │ Knowledge        │
            │ Ingestion        │
            │  - Run boot_     │
            │    preload.py    │
            │  - Index files   │
            │  - Optional:     │
            │    embeddings    │
            └────────┬─────────┘
                     │
                     ▼
            ┌──────────────────┐
            │ Signal Ready     │
            │  - Create        │
            │    .boot-ready   │
            │  - Log success   │
            └────────┬─────────┘
                     │
                     ▼
          ┌──────────────────────┐
          │  BOOT Complete       │
          │  System Ready        │
          └──────────────────────┘
```

---

## Components

### 1. boot.sh

**Purpose:** Main orchestrator script written in Bash

**Responsibilities:**
- Idempotency checking
- Log rotation
- Environment validation
- Dependency installation
- Orchestrate knowledge ingestion
- File validation
- Readiness signaling

**Exit Codes:**
- `0` - Success
- `1` - Environment validation failed
- `2` - Dependency check failed
- `3` - Knowledge ingestion failed
- `4` - Permission/write error

**Key Features:**
- Command-line flags: `--force`, `--no-embeddings`, `--verbose`
- Timestamp-based logging
- Automatic log rotation (default: 10MB limit)
- Safe re-run detection

### 2. boot_preload.py

**Purpose:** Knowledge base ingestion pipeline written in Python

**Responsibilities:**
- Scan knowledge directories (docs, panelin_reports, .evolucionador/knowledge)
- Extract file metadata (path, size, hash, timestamps)
- Validate JSON files
- Create knowledge_index.json
- Optional: Generate vector embeddings (placeholder for future)

**Key Features:**
- SHA256 file hashing for integrity
- Recursive directory scanning
- File type filtering (.json, .md, .txt, .csv, .rtf)
- Exclude patterns (node_modules, .git, __pycache__)
- Statistics tracking (files indexed, total size, errors)

### 3. scripts/boot_test.sh

**Purpose:** Smoke test suite for BOOT process

**Tests:**
- Script syntax validation
- Environment validation
- Idempotency behavior
- Force flag functionality
- Knowledge indexer without network
- Artifact creation and format
- Security: No secrets in logs
- Index structure validation

**Safe for CI:** No network calls, no real API keys required

### 4. scripts/validate_boot_artifacts.py

**Purpose:** Post-BOOT validation of artifacts

**Validations:**
- `.boot-ready` exists with proper format
- `.boot-log` has timestamps, no secrets
- `knowledge_index.json` has valid structure and hashes

**Modes:**
- Normal: Basic validation
- Strict (`--strict`): Includes file hash verification

---

## Environment Variables

### Core Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `PANELIN_ROOT` | No | Current directory | Repository root path |
| `GENERATE_EMBEDDINGS` | No | `0` | Generate vector embeddings (0=no, 1=yes) |
| `PANELIN_API_KEY` | Conditional | None | API key for embeddings (required if GENERATE_EMBEDDINGS=1) |
| `PYTHON_BIN` | No | `python3` | Python interpreter path |
| `BOOT_LOG_MAX_SIZE_MB` | No | `10` | Max log size before rotation (MB) |

### Optional Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `KNOWLEDGE_DIRS` | Auto-detect | Colon-separated list of directories to index |
| `ALLOWED_EXTENSIONS` | `.json,.md,.txt,.csv,.rtf` | Comma-separated file extensions |

### Usage Examples

```bash
# Local development (no embeddings)
export GENERATE_EMBEDDINGS=0
./boot.sh

# Production with embeddings
export GENERATE_EMBEDDINGS=1
export PANELIN_API_KEY="your-api-key-here"
./boot.sh

# CI/CD (force fresh boot)
GENERATE_EMBEDDINGS=0 ./boot.sh --force --no-embeddings

# Docker container
docker run -e GENERATE_EMBEDDINGS=0 -e PANELIN_ROOT=/app panelin-gpt:boot
```

---

## Artifacts

### 1. .boot-ready

**Purpose:** Readiness flag indicating successful BOOT completion

**Location:** `{PANELIN_ROOT}/.boot-ready`

**Format:**
```
BOOT completed successfully
Timestamp: 2026-02-10T23:36:28Z
Python: Python 3.11.7
Embeddings: 0
Root: /app
```

**Usage:** Check existence before starting application
```bash
if [ -f .boot-ready ]; then
  echo "System ready"
  start-application
else
  echo "BOOT incomplete, run ./boot.sh"
  exit 1
fi
```

### 2. .boot-log

**Purpose:** Comprehensive log of BOOT process with timestamps

**Location:** `{PANELIN_ROOT}/.boot-log`

**Format:**
```
[2026-02-10T23:36:28Z] INFO: ==========================================
[2026-02-10T23:36:28Z] INFO: Panelin GPT BOOT Process Starting
[2026-02-10T23:36:28Z] INFO: ==========================================
[2026-02-10T23:36:28Z] INFO: Root: /app
[2026-02-10T23:36:28Z] INFO: Python: python3
[2026-02-10T23:36:28Z] INFO: Embeddings: 0
[2026-02-10T23:36:29Z] INFO: ==> Validating environment
[2026-02-10T23:36:29Z] INFO: Python version: 3.11
...
```

**Rotation:** Automatically rotates when size exceeds `BOOT_LOG_MAX_SIZE_MB`
- Rotated files: `.boot-log.YYYYMMDD-HHMMSS`
- Retention: Last 5 rotated logs kept

**Security:** Never contains API keys, passwords, or tokens

### 3. knowledge_index.json

**Purpose:** Metadata index of all knowledge base files

**Location:** `{PANELIN_ROOT}/knowledge_index.json`

**Structure:**
```json
{
  "version": "1.0",
  "generated_at": "2026-02-10T23:36:30Z",
  "root_directory": "/app",
  "embeddings_enabled": false,
  "files": [
    {
      "path": "docs/README.md",
      "absolute_path": "/app/docs/README.md",
      "name": "README.md",
      "extension": ".md",
      "size_bytes": 12345,
      "modified_at": "2026-02-10T20:00:00Z",
      "sha256": "abc123...",
      "valid": true
    }
  ],
  "statistics": {
    "total_files_scanned": 150,
    "files_indexed": 142,
    "total_size_bytes": 5242880,
    "total_size_mb": 5.0,
    "errors": 0
  }
}
```

**Usage:** Query indexed files, verify integrity, track changes

---

## Error States & Remediation

### Error Code 1: Environment Validation Failed

**Symptoms:**
- Exit code 1
- Log message: "Environment validation failed"

**Common Causes:**
- Required files missing (requirements.txt, validate_gpt_files.py)
- Python version incompatible
- Missing repository structure

**Remediation:**
```bash
# Check Python version (need 3.8+)
python3 --version

# Verify you're in repository root
ls -la boot.sh requirements.txt

# Check file permissions
ls -l boot.sh boot_preload.py

# Re-clone repository if files missing
git pull origin main
```

### Error Code 2: Dependency Check Failed

**Symptoms:**
- Exit code 2
- Log message: "Python not found" or "Dependency check failed"

**Common Causes:**
- Python not installed or not in PATH
- Unable to create virtualenv
- Network issues during pip install

**Remediation:**
```bash
# Install Python 3.8+
sudo apt-get install python3 python3-venv python3-pip

# Set PYTHON_BIN if non-standard location
export PYTHON_BIN=/usr/local/bin/python3.11
./boot.sh

# Check network connectivity
ping pypi.org

# Use offline mode (if pip packages cached)
pip install --no-index --find-links=/path/to/cache -r requirements.txt
```

### Error Code 3: Knowledge Ingestion Failed

**Symptoms:**
- Exit code 3
- Log message: "Knowledge ingestion failed" or "File validation failed"

**Common Causes:**
- Invalid JSON in knowledge base files
- Permission errors reading files
- boot_preload.py errors

**Remediation:**
```bash
# Validate JSON files manually
python3 -m json.tool BMC_Base_Conocimiento_GPT-2.json

# Check file permissions
chmod -R u+r docs/ panelin_reports/

# Run knowledge ingestion separately
python3 boot_preload.py

# Check specific files mentioned in error
cat .boot-log | grep ERROR
```

### Error Code 4: Permission/Write Error

**Symptoms:**
- Exit code 4
- Log message: "not writable" or "Permission denied"

**Common Causes:**
- Insufficient permissions to create files
- Read-only filesystem
- Disk full

**Remediation:**
```bash
# Check disk space
df -h

# Check write permissions
touch .boot-test && rm .boot-test || echo "No write permission"

# Fix permissions
chmod u+w . 
sudo chown -R $USER:$USER .

# Check if filesystem read-only
mount | grep "$(pwd -P)"
```

### General Troubleshooting

```bash
# View recent errors in log
tail -50 .boot-log | grep ERROR

# Run with verbose mode
./boot.sh --verbose

# Force clean boot
rm -f .boot-ready .boot-log knowledge_index.json
./boot.sh --force

# Test in isolated environment
mkdir /tmp/boot-test
cp -r . /tmp/boot-test
cd /tmp/boot-test
./boot.sh
```

---

## Security Considerations

### 1. Secrets Management

**Rules:**
- **NEVER** log API keys, passwords, or tokens
- **NEVER** commit `.boot-ready` or `.boot-log` to git
- **ALWAYS** use environment variables for secrets
- **ALWAYS** validate patterns don't match secrets in logs

**Implementation:**
```bash
# boot.sh never echoes API key values
if [[ -n "${PANELIN_API_KEY:-}" ]]; then
  log_info "API key is set (length: ${#PANELIN_API_KEY})"
  # NOT: log_info "API key: $PANELIN_API_KEY"
fi
```

**CI/CD:**
```yaml
# GitHub Actions - use secrets
env:
  PANELIN_API_KEY: ${{ secrets.PANELIN_API_KEY }}

# Never run with secrets in public CI
- name: Run BOOT (no secrets)
  run: ./boot.sh --no-embeddings
  env:
    GENERATE_EMBEDDINGS: 0
```

### 2. Input Validation

**Path Traversal Prevention:**
- Use absolute paths only
- Validate `PANELIN_ROOT` is within expected directory
- Exclude patterns prevent accessing sensitive areas

**File Type Validation:**
- Only allowed extensions indexed
- JSON files validated before indexing
- Binary files excluded from text processing

### 3. Log Security

**Sensitive Pattern Detection:**
```python
# validate_boot_artifacts.py checks for:
SENSITIVE_PATTERNS = [
    r'api[_-]?key["\']?\s*[:=]\s*["\']?[a-zA-Z0-9_-]{20,}',
    r'password["\']?\s*[:=]\s*["\']?[^\s"\']{8,}',
    r'secret["\']?\s*[:=]\s*["\']?[a-zA-Z0-9_-]{20,}',
    r'token["\']?\s*[:=]\s*["\']?[a-zA-Z0-9_-]{20,}',
]
```

**Audit:** Run validation after every BOOT
```bash
python3 scripts/validate_boot_artifacts.py --strict
```

### 4. Least Privilege

- BOOT scripts run as application user, not root
- Virtual environment isolates dependencies
- No sudo required for normal operation

---

## Integration Patterns

### Pattern 1: Local Development

```bash
# First time setup
git clone https://github.com/matiasportugau-ui/GPT-PANELIN-V3.2.git
cd GPT-PANELIN-V3.2
./boot.sh

# Daily development (skip BOOT if already done)
if [ ! -f .boot-ready ]; then
  ./boot.sh
fi
python3 quotation_calculator_v3.py
```

### Pattern 2: CI/CD Pipeline

```yaml
# .github/workflows/deploy.yml
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Run BOOT
        run: ./boot.sh --force --no-embeddings
        env:
          GENERATE_EMBEDDINGS: 0
      
      - name: Validate BOOT
        run: python3 scripts/validate_boot_artifacts.py
      
      - name: Deploy
        run: ./deploy.sh
```

### Pattern 3: Docker Container

**Option A: BOOT during image build**
```dockerfile
FROM python:3.11-slim
COPY . /app
WORKDIR /app
RUN ./boot.sh --no-embeddings
CMD ["python3", "app.py"]
```

**Option B: BOOT at container start** (recommended)
```dockerfile
FROM python:3.11-slim
COPY . /app
WORKDIR /app
ENTRYPOINT ["/app/docker-entrypoint.sh"]
CMD ["python3", "app.py"]
```

```bash
# docker-entrypoint.sh
#!/bin/bash
if [ ! -f .boot-ready ]; then
  ./boot.sh --no-embeddings
fi
exec "$@"
```

### Pattern 4: Kubernetes Init Container

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: panelin-gpt
spec:
  initContainers:
  - name: boot
    image: panelin-gpt:latest
    command: ["/bin/sh", "-c"]
    args:
      - ./boot.sh --no-embeddings
    env:
    - name: GENERATE_EMBEDDINGS
      value: "0"
    volumeMounts:
    - name: boot-data
      mountPath: /app
  
  containers:
  - name: app
    image: panelin-gpt:latest
    volumeMounts:
    - name: boot-data
      mountPath: /app
  
  volumes:
  - name: boot-data
    emptyDir: {}
```

### Pattern 5: Systemd Service

```ini
# /etc/systemd/system/panelin-gpt.service
[Unit]
Description=Panelin GPT Service
After=network.target

[Service]
Type=simple
User=panelin
WorkingDirectory=/opt/panelin-gpt
Environment="GENERATE_EMBEDDINGS=0"
ExecStartPre=/opt/panelin-gpt/boot.sh
ExecStart=/opt/panelin-gpt/venv/bin/python3 app.py
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

---

## Testing

### Smoke Tests (No Network)

```bash
# Run full smoke test suite
./scripts/boot_test.sh

# Expected: All tests pass
# Output: PASS/FAIL for each test
```

**Tests included:**
1. Script syntax validation
2. Python syntax validation
3. Environment validation
4. Idempotency behavior
5. Force flag functionality
6. Knowledge indexer (offline)
7. Artifact creation
8. No secrets in logs
9. Index structure validation
10. Help and usage messages

### Integration Tests (With Network)

```bash
# Full BOOT with actual dependencies
./boot.sh --force --no-embeddings

# Validate artifacts
python3 scripts/validate_boot_artifacts.py --strict

# Check readiness
test -f .boot-ready && echo "Ready" || echo "Not ready"
```

### Performance Benchmarks

```bash
# Measure BOOT time
time ./boot.sh --force --no-embeddings

# Expected: < 60 seconds on standard hardware
# Actual: ~10-30 seconds depending on file count

# Measure index size
ls -lh knowledge_index.json

# Expected: < 1MB for typical repository
```

### Security Tests

```bash
# Test secret detection
export PANELIN_API_KEY="test-secret-12345"
./boot.sh --no-embeddings
python3 scripts/validate_boot_artifacts.py

# Should fail if secret found in logs
grep -q "test-secret" .boot-log && echo "FAIL: Secret leaked" || echo "PASS: No leak"
```

---

## Maintenance

### Log Rotation

Automatic rotation occurs when log size exceeds `BOOT_LOG_MAX_SIZE_MB`:

```bash
# Manual rotation
if [ -f .boot-log ]; then
  mv .boot-log .boot-log.$(date +%Y%m%d-%H%M%S)
fi

# Clean old logs (keep last 5)
ls -t .boot-log.* | tail -n +6 | xargs rm -f
```

### Monitoring

```bash
# Check BOOT health
./scripts/validate_boot_artifacts.py

# Monitor for repeated BOOT failures
tail -f .boot-log | grep ERROR

# Alert if BOOT incomplete after 5 minutes
timeout 300 bash -c 'while [ ! -f .boot-ready ]; do sleep 5; done' || alert "BOOT timeout"
```

### Upgrades

When upgrading BOOT scripts:

```bash
# Backup current state
cp boot.sh boot.sh.backup
cp boot_preload.py boot_preload.py.backup

# Pull updates
git pull origin main

# Force fresh BOOT with new scripts
rm -f .boot-ready
./boot.sh --force --no-embeddings

# Validate
python3 scripts/validate_boot_artifacts.py --strict
```

---

## FAQ

**Q: Can I run BOOT multiple times?**  
A: Yes, BOOT is idempotent. Subsequent runs detect `.boot-ready` and skip. Use `--force` to override.

**Q: Do I need API keys for development?**  
A: No. Set `GENERATE_EMBEDDINGS=0` to skip embedding generation. All other features work without keys.

**Q: What happens if BOOT fails mid-process?**  
A: BOOT fails fast and exits with specific error code. No partial state. Simply fix the issue and re-run.

**Q: Can I run BOOT in parallel?**  
A: Not recommended. BOOT is designed for sequential execution. Use container orchestration for parallel deployments.

**Q: How do I debug BOOT issues?**  
A: Check `.boot-log` for detailed messages. Run with `--verbose` for more output. Use smoke tests to isolate issues.

**Q: Is BOOT required for production?**  
A: Yes. BOOT ensures consistent environment, validates files, and creates necessary indexes. Skip at your own risk.

**Q: Can I customize BOOT for my environment?**  
A: Yes. Use environment variables for configuration. For deeper changes, fork and modify scripts while maintaining contracts.

---

## Support

For issues, questions, or contributions:
- **Repository:** https://github.com/matiasportugau-ui/GPT-PANELIN-V3.2
- **Issues:** https://github.com/matiasportugau-ui/GPT-PANELIN-V3.2/issues
- **Documentation:** See README.md and inline code comments

---

**Document Version:** 1.0  
**Last Updated:** 2026-02-10  
**Author:** BOOT Architecture Team
