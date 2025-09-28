# Multi-stage build for MS-Passengers Database Ingestion Container
# PostgreSQL CDC-enabled data extraction for Bus MVP system

# ========================================
# BUILD STAGE
# ========================================
FROM python:3.11-slim as builder

# Build arguments
ARG BUILD_DATE
ARG VERSION=1.0.0

# Metadata
LABEL maintainer="Bus MVP Team" \
      description="PostgreSQL ingestion container for passenger data" \
      version="${VERSION}" \
      build-date="${BUILD_DATE}"

# Install system dependencies for building
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    libpq-dev \
    pkg-config \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --user -r requirements.txt

# ========================================
# RUNTIME STAGE
# ========================================
FROM python:3.11-slim

# Install runtime system dependencies
RUN apt-get update && apt-get install -y \
    libpq5 \
    postgresql-client \
    curl \
    procps \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user for security
RUN groupadd -r ingestion && useradd -r -g ingestion ingestion

# Set working directory
WORKDIR /app

# Copy Python packages from builder
COPY --from=builder /root/.local /home/ingestion/.local

# Copy application code
COPY --chown=ingestion:ingestion src/ ./src/
COPY --chown=ingestion:ingestion scripts/ ./scripts/
COPY --chown=ingestion:ingestion tests/ ./tests/

# Create necessary directories
RUN mkdir -p /app/data /app/logs /app/temp /app/config && \
    chown -R ingestion:ingestion /app

# Set environment variables
ENV PYTHONPATH=/app/src \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH=/home/ingestion/.local/bin:$PATH \
    USER=ingestion

# Health check configuration
ENV HEALTH_CHECK_PORT=8090
ENV HEALTH_CHECK_INTERVAL=30
ENV HEALTH_CHECK_TIMEOUT=10

# Switch to non-root user
USER ingestion

# Expose health check port
EXPOSE ${HEALTH_CHECK_PORT}

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:${HEALTH_CHECK_PORT}/health || exit 1

# Default command
CMD ["python", "src/main.py"]
