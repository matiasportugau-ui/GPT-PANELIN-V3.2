#!/bin/bash
# docker-entrypoint.sh - Container entrypoint with BOOT integration

set -e

echo "=========================================="
echo "Panelin GPT Container Starting"
echo "=========================================="

# Run BOOT process if not already completed
if [ ! -f /app/.boot-ready ]; then
  echo "Running BOOT process..."
  cd /app
  ./boot.sh --no-embeddings
else
  echo "BOOT already completed, skipping..."
fi

echo "Container ready, executing command: $@"
echo "=========================================="

# Execute the main container command
exec "$@"
