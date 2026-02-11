# GPT-PANELIN BOOT Container
#
# This Dockerfile demonstrates how to containerize the GPT-PANELIN system
# with the BOOT process. It uses Python 3.11 and runs boot.sh on startup.

FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    GENERATE_EMBEDDINGS=0 \
    PYTHONDONTWRITEBYTECODE=1

# Install system dependencies (if needed)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    bash \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy BOOT scripts
COPY boot.sh .
COPY boot_preload.py .
COPY index_validator.py .

# Copy knowledge source files
COPY knowledge_src/ ./knowledge_src/

# Make scripts executable
RUN chmod +x boot.sh boot_preload.py index_validator.py

# Copy application files (add your application files here)
# COPY your_app/ ./your_app/

# Create non-root user for security
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Health check (optional - adjust as needed)
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD test -f .boot-ready || exit 1

# Run BOOT process on container start
ENTRYPOINT ["./boot.sh"]

# Default command (can be overridden)
CMD []

# Example usage:
# 
# Build:
#   docker build -t gpt-panelin:latest .
#
# Run (development mode, no embeddings):
#   docker run --rm gpt-panelin:latest
#
# Run with embeddings (use secrets management in production):
#   docker run --rm \
#     -e GENERATE_EMBEDDINGS=1 \
#     -e OPENAI_API_KEY="your-api-key" \
#     gpt-panelin:latest
#
# Run with custom command after boot:
#   docker run --rm gpt-panelin:latest && python your_app.py
