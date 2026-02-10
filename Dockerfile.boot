# Dockerfile for Panelin GPT with BOOT Integration
# 
# This Dockerfile demonstrates how to integrate the BOOT process
# into a containerized deployment of Panelin GPT.
#
# Build: docker build -f Dockerfile.boot -t panelin-gpt:boot .
# Run:   docker run -e GENERATE_EMBEDDINGS=0 panelin-gpt:boot

FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    bash \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy EVOLUCIONADOR requirements if exists
COPY .evolucionador/requirements.txt .evolucionador/requirements.txt
RUN pip install --no-cache-dir -r .evolucionador/requirements.txt

# Copy BOOT scripts
COPY boot.sh .
COPY boot_preload.py .
RUN chmod +x boot.sh

# Copy application files
COPY . .

# Environment variables with secure defaults
ENV PANELIN_ROOT=/app
ENV GENERATE_EMBEDDINGS=0
ENV PYTHON_BIN=python3

# Run BOOT process during build (optional)
# Comment out if you prefer to run BOOT at container start
# RUN ./boot.sh --no-embeddings

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD [ -f /app/.boot-ready ] || exit 1

# Entrypoint: Run BOOT if not already done, then start application
COPY docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]

# Default command (can be overridden)
CMD ["python3", "-m", "http.server", "8000"]
