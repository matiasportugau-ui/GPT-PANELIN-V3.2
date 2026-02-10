#!/usr/bin/env bash
################################################################################
# boot_test.sh - BOOT Process Smoke Test
# 
# Purpose: Validates BOOT process without network calls or API keys
# - Tests script execution and environment validation
# - Validates artifact creation (.boot-ready, .boot-log, knowledge_index.json)
# - Checks idempotency and log rotation
# - Safe to run in CI without secrets
#
# Usage:
#   ./scripts/boot_test.sh
#
# Exit Codes:
#   0 - All tests passed
#   1 - One or more tests failed
################################################################################

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test tracking
TESTS_PASSED=0
TESTS_FAILED=0
TEST_DIR="/tmp/boot_test_$$"

# Logging functions
log_test() {
  echo -e "${YELLOW}[TEST]${NC} $*"
}

log_pass() {
  echo -e "${GREEN}[PASS]${NC} $*"
  TESTS_PASSED=$((TESTS_PASSED + 1))
}

log_fail() {
  echo -e "${RED}[FAIL]${NC} $*"
  TESTS_FAILED=$((TESTS_FAILED + 1))
}

log_info() {
  echo -e "[INFO] $*"
}

# Setup test environment
setup_test_env() {
  log_info "Setting up test environment in $TEST_DIR"
  mkdir -p "$TEST_DIR"
  
  # Copy necessary files
  cp boot.sh "$TEST_DIR/"
  cp boot_preload.py "$TEST_DIR/"
  cp requirements.txt "$TEST_DIR/"
  cp validate_gpt_files.py "$TEST_DIR/" 2>/dev/null || true
  
  # Create minimal file structure
  mkdir -p "$TEST_DIR/docs"
  echo '{"test": "data"}' > "$TEST_DIR/docs/test.json"
  echo "# Test Document" > "$TEST_DIR/docs/test.md"
  
  cd "$TEST_DIR"
}

# Cleanup test environment
cleanup_test_env() {
  log_info "Cleaning up test environment"
  cd /
  rm -rf "$TEST_DIR"
}

# Test 1: Boot script syntax
test_boot_script_syntax() {
  log_test "Test 1: Boot script syntax check"
  
  if bash -n boot.sh; then
    log_pass "boot.sh has valid syntax"
  else
    log_fail "boot.sh has syntax errors"
  fi
}

# Test 2: Python script syntax
test_python_script_syntax() {
  log_test "Test 2: Python script syntax check"
  
  if python3 -m py_compile boot_preload.py 2>/dev/null; then
    log_pass "boot_preload.py has valid syntax"
  else
    log_fail "boot_preload.py has syntax errors"
  fi
}

# Test 3: Environment validation
test_environment_validation() {
  log_test "Test 3: Environment validation (dry run)"
  
  # Test with invalid Python binary (should fail gracefully)
  if PYTHON_BIN="/nonexistent/python" bash boot.sh 2>&1 | grep -q "Python not found"; then
    log_pass "Correctly detects missing Python"
  else
    log_fail "Did not detect missing Python"
  fi
}

# Test 4: Idempotency check
test_idempotency() {
  log_test "Test 4: Idempotency check"
  
  # Create fake .boot-ready
  echo "Previous boot" > .boot-ready
  
  # Should detect existing boot and exit 0
  if bash boot.sh 2>&1 | grep -q "already booted"; then
    log_pass "Correctly detects existing boot"
  else
    log_fail "Did not detect existing boot"
  fi
  
  rm .boot-ready
}

# Test 5: Force flag
test_force_flag() {
  log_test "Test 5: Force flag functionality"
  
  # Create fake .boot-ready
  echo "Previous boot" > .boot-ready
  
  # Should override with --force
  if bash boot.sh --force 2>&1 | grep -q "forced reboot"; then
    log_pass "Force flag works correctly"
  else
    log_fail "Force flag did not work"
  fi
  
  rm -f .boot-ready .boot-log
}

# Test 6: Knowledge indexer without network
test_knowledge_indexer() {
  log_test "Test 6: Knowledge indexer (no network)"
  
  export PANELIN_ROOT="$TEST_DIR"
  export GENERATE_EMBEDDINGS=0
  
  if python3 boot_preload.py; then
    if [[ -f "knowledge_index.json" ]]; then
      log_pass "Knowledge index created successfully"
      
      # Validate JSON
      if python3 -c "import json; json.load(open('knowledge_index.json'))" 2>/dev/null; then
        log_pass "Knowledge index is valid JSON"
      else
        log_fail "Knowledge index is invalid JSON"
      fi
    else
      log_fail "Knowledge index not created"
    fi
  else
    log_fail "Knowledge indexer failed"
  fi
}

# Test 7: Artifact validation
test_artifacts() {
  log_test "Test 7: Boot artifacts validation"
  
  # Remove old artifacts
  rm -f .boot-ready .boot-log knowledge_index.json
  
  # Run boot (will fail on dependency install but should create logs)
  bash boot.sh --no-embeddings 2>&1 | head -20 || true
  
  # Check if log was created
  if [[ -f ".boot-log" ]]; then
    log_pass ".boot-log created"
    
    # Check log format (should have timestamps)
    if grep -qE '\[[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z\]' .boot-log; then
      log_pass "Log has proper timestamp format"
    else
      log_fail "Log missing timestamps"
    fi
  else
    log_fail ".boot-log not created"
  fi
}

# Test 8: No secrets in output
test_no_secrets_logged() {
  log_test "Test 8: Secrets not logged"
  
  export PANELIN_API_KEY="secret_test_key_12345"
  
  # Run boot
  bash boot.sh --no-embeddings 2>&1 | head -20 > /tmp/boot_output.txt || true
  
  # Check that API key is not in output or logs
  if ! grep -q "secret_test_key" /tmp/boot_output.txt .boot-log 2>/dev/null; then
    log_pass "API key not found in logs"
  else
    log_fail "API key found in logs (security issue!)"
  fi
  
  rm -f /tmp/boot_output.txt
  unset PANELIN_API_KEY
}

# Test 9: Index validation script
test_index_validation() {
  log_test "Test 9: Index validation script"
  
  # Create a valid index
  export PANELIN_ROOT="$TEST_DIR"
  export GENERATE_EMBEDDINGS=0
  python3 boot_preload.py > /dev/null 2>&1 || true
  
  if [[ -f "knowledge_index.json" ]]; then
    # Check structure
    if python3 -c "
import json
with open('knowledge_index.json') as f:
    idx = json.load(f)
    assert 'version' in idx
    assert 'files' in idx
    assert 'statistics' in idx
    print('Index structure valid')
" 2>/dev/null; then
      log_pass "Index has valid structure"
    else
      log_fail "Index structure invalid"
    fi
  fi
}

# Test 10: Help and usage
test_help_and_usage() {
  log_test "Test 10: Help and usage"
  
  # Test unknown option
  if bash boot.sh --unknown-option 2>&1 | grep -q "Unknown option"; then
    log_pass "Shows error for unknown options"
  else
    log_fail "Did not handle unknown option"
  fi
}

# Main test execution
main() {
  echo "=========================================="
  echo "BOOT Process Smoke Test Suite"
  echo "=========================================="
  echo ""
  
  # Setup
  setup_test_env
  
  # Run tests
  test_boot_script_syntax
  test_python_script_syntax
  test_environment_validation
  test_idempotency
  test_force_flag
  test_knowledge_indexer
  test_artifacts
  test_no_secrets_logged
  test_index_validation
  test_help_and_usage
  
  # Cleanup
  cleanup_test_env
  
  # Summary
  echo ""
  echo "=========================================="
  echo "Test Results"
  echo "=========================================="
  echo -e "${GREEN}Passed:${NC} $TESTS_PASSED"
  echo -e "${RED}Failed:${NC} $TESTS_FAILED"
  echo ""
  
  if [[ $TESTS_FAILED -eq 0 ]]; then
    echo -e "${GREEN}All tests passed!${NC}"
    exit 0
  else
    echo -e "${RED}Some tests failed!${NC}"
    exit 1
  fi
}

# Trap cleanup on exit
trap cleanup_test_env EXIT

# Run main
main "$@"
