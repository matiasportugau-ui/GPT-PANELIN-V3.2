# BOOT Integration Guide

## Overview

The BOOT (Bootstrap, Operations, Orchestration, and Testing) process provides an idempotent, secure system initialization for GPT-PANELIN. This document describes the architecture, usage, and security considerations.

## Architecture

### Components

1. **boot.sh** - Main orchestrator script
   - Manages logging with automatic rotation
   - Implements lock mechanism to prevent concurrent runs
   - Validates Python environment
   - Installs dependencies
   - Executes preload script
   - Creates readiness flag

2. **boot_preload.py** - Knowledge base preloader
   - Copies files from `knowledge_src/` to `knowledge/`
   - Performs idempotent operations (skips unchanged files)
   - Generates `knowledge_index.json` with SHA256 hashes
   - Supports optional embeddings generation
   - Validates environment configuration

3. **index_validator.py** - Index validation tool
   - Validates `knowledge_index.json` structure
   - Verifies all referenced files exist
   - Validates SHA256 hashes match
   - Reports warnings and errors

### Directory Structure

```
.
├── boot.sh                      # Main orchestrator
├── boot_preload.py              # Preloader script
├── index_validator.py           # Validator script
├── knowledge_src/               # Source knowledge files (committed to repo)
├── knowledge/                   # Runtime knowledge files (generated)
├── knowledge_index.json         # Generated index (runtime)
├── .boot-log                    # Boot process log (runtime)
├── .boot-lock                   # Lock file (runtime)
└── .boot-ready                  # Readiness flag (runtime)
```

## Environment Variables

### Required Variables

None - the system runs with defaults.

### Optional Variables

- **GENERATE_EMBEDDINGS** (default: `0`)
  - Set to `1` to enable embeddings generation
  - Requires valid `OPENAI_API_KEY`
  - Should be `0` in CI/CD environments
  
- **OPENAI_API_KEY** (default: empty)
  - OpenAI API key for embeddings generation
  - Only used when `GENERATE_EMBEDDINGS=1`
  - Never log or commit this value
  - Use secure secret management in production

- **PYTHON_CMD** (default: `python3`)
  - Python interpreter to use
  - Automatically uses virtual environment if found

## Security Considerations

### Secrets Management

1. **Never commit secrets** to the repository
   - Use environment variables for API keys
   - Use `.gitignore` to exclude sensitive files
   - Use secret management systems in production

2. **Log sanitization**
   - `boot.sh` and `boot_preload.py` redact sensitive values from logs
   - Patterns like `key=`, `token=`, `secret=`, `password=` are sanitized
   - Review logs before sharing

3. **File permissions**
   - Log files created with `600` (owner read/write only)
   - Use principle of least privilege

### Network Security

1. **Embeddings generation**
   - Only enabled when explicitly configured
   - Disabled by default in CI
   - Requires valid API key
   - Network calls should be rate-limited

2. **CI/CD environments**
   - Always set `GENERATE_EMBEDDINGS=0`
   - Do not provide API keys in CI
   - Use smoke tests without network calls

## Usage

### Basic Usage

```bash
# Run the boot process
./boot.sh
```

The script will:
1. Create secure log file (`.boot-log`)
2. Acquire lock to prevent concurrent runs
3. Check Python environment
4. Install dependencies from `requirements.txt`
5. Run preload script
6. Create readiness flag (`.boot-ready`)

### With Embeddings Generation

```bash
# Set environment variables
export GENERATE_EMBEDDINGS=1
export OPENAI_API_KEY="sk-..."

# Run boot process
./boot.sh
```

**Warning:** Only use in development/production, never in CI.

### Validation

```bash
# Validate the generated index
python3 index_validator.py
```

Exit codes:
- `0` - All validations passed
- `1` - Warnings or mismatches found
- `2` - Critical error (missing index)

### Local Smoke Testing

```bash
# Run local smoke test
./scripts/smoke_boot.sh
```

This runs the boot process in a safe mode and validates the results.

## Manual Testing Steps

### Test 1: Fresh Boot

```bash
# Clean previous artifacts
rm -f .boot-log .boot-lock .boot-ready knowledge_index.json
rm -rf knowledge/

# Run boot
./boot.sh

# Verify artifacts created
ls -la .boot-log .boot-ready knowledge_index.json

# Validate index
python3 index_validator.py
```

Expected: All artifacts created, validator returns 0.

### Test 2: Idempotency

```bash
# Run boot twice
./boot.sh
./boot.sh

# Check log for "skipped" messages
tail -20 .boot-log
```

Expected: Second run should skip unchanged files, complete successfully.

### Test 3: Lock Mechanism

```bash
# Create stale lock
echo "9999" > .boot-lock

# Try to run boot
./boot.sh

# Should fail with lock error
# Clean up
rm .boot-lock
```

Expected: Boot should fail with clear error about lock file.

### Test 4: Log Rotation

```bash
# Create large log file (>5MB)
dd if=/dev/zero of=.boot-log bs=1M count=6

# Run boot
./boot.sh

# Check for rotated log
ls -la .boot-log .boot-log.old
```

Expected: Old log rotated to `.boot-log.old`, new log created.

### Test 5: Validation Failures

```bash
# Run boot normally
./boot.sh

# Corrupt a file
echo "corrupted" >> knowledge/some_file.txt

# Validate
python3 index_validator.py
```

Expected: Validator should detect hash mismatch and exit with code 1.

## CI Integration

### Smoke Test Workflow

The `.github/workflows/boot-smoke.yml` workflow:
- Triggers on PRs affecting boot or knowledge files
- Sets `GENERATE_EMBEDDINGS=0` (no network calls)
- Verifies presence of scripts
- Runs `index_validator.py` if index exists
- Does not make external API calls

### CI Best Practices

1. **Never provide API keys** in CI environment
2. **Always set GENERATE_EMBEDDINGS=0** in CI
3. **Use smoke tests** without network dependencies
4. **Validate artifacts** but don't commit them
5. **Check exit codes** and fail CI on errors

## Container Integration

### Dockerfile Example

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Copy application files
COPY requirements.txt .
COPY boot.sh .
COPY boot_preload.py .
COPY index_validator.py .
COPY knowledge_src/ ./knowledge_src/

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Set safe defaults
ENV GENERATE_EMBEDDINGS=0
ENV PYTHONUNBUFFERED=1

# Run boot on container start
ENTRYPOINT ["./boot.sh"]
```

Build and run:

```bash
# Build image
docker build -t gpt-panelin:latest .

# Run container
docker run --rm gpt-panelin:latest

# With embeddings (development only)
docker run --rm \
  -e GENERATE_EMBEDDINGS=1 \
  -e OPENAI_API_KEY="sk-..." \
  gpt-panelin:latest
```

## Troubleshooting

### Issue: Lock file exists

```bash
# Check if process is running
ps aux | grep boot.sh

# If not running, remove stale lock
rm .boot-lock
```

### Issue: Python module not found

```bash
# Install dependencies manually
python3 -m pip install -r requirements.txt
```

### Issue: Permission denied

```bash
# Make scripts executable
chmod +x boot.sh boot_preload.py index_validator.py
```

### Issue: Validation failures

```bash
# Re-run boot to regenerate index
./boot.sh

# Check log for errors
tail -50 .boot-log
```

### Issue: Large log files

The log automatically rotates at 5MB. To manually rotate:

```bash
mv .boot-log .boot-log.old
touch .boot-log
chmod 600 .boot-log
```

## Advanced Configuration

### Custom Python Environment

```bash
# Use specific Python version
PYTHON_CMD=python3.11 ./boot.sh
```

### Custom Directories

Edit the scripts to change directory paths:
- `KNOWLEDGE_SRC_DIR` in `boot_preload.py`
- `KNOWLEDGE_DIR` in `boot_preload.py`
- `INDEX_FILE` in both `boot_preload.py` and `index_validator.py`

### Extending Preload

To add custom preload logic:

1. Edit `boot_preload.py`
2. Add new functions before `main()`
3. Call functions from `main()`
4. Update index schema if needed

## Maintenance

### Regular Tasks

1. **Monitor log size** - Automatic rotation at 5MB
2. **Validate index** - Run validator periodically
3. **Update dependencies** - Keep `requirements.txt` current
4. **Review security** - Audit logs for sensitive data

### Updating Knowledge Files

1. Add/modify files in `knowledge_src/`
2. Run `./boot.sh`
3. Validate with `python3 index_validator.py`
4. Commit changes to `knowledge_src/` only

**Note:** Do not commit `knowledge/`, `knowledge_index.json`, or `.boot-*` files.

## Support

For issues or questions:
1. Check logs in `.boot-log`
2. Review this documentation
3. Run validator for diagnostics
4. Open GitHub issue with log excerpts (redact secrets!)

## Version History

- **1.0.0** (2024) - Initial BOOT implementation
  - Idempotent file copying
  - SHA256-based validation
  - Optional embeddings hook
  - Secure logging and lock mechanism
