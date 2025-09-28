# MS Analytics - FastAPI with AWS Services
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/

# Create non-root user for security
RUN groupadd -r analytics && useradd -r -g analytics analytics
RUN chown -R analytics:analytics /app
USER analytics

# Expose port
EXPOSE 8010

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8010/api/v1/health/live || exit 1

# Set Python path
ENV PYTHONPATH=/app/src

# Start command
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8010"]

# Environment variables documentation:
# Required for AWS mode:
# - ENVIRONMENT=aws
# - AWS_REGION=us-east-1
# - AWS_ACCESS_KEY_ID (or use IAM role)
# - AWS_SECRET_ACCESS_KEY (or use IAM role)
# - AWS_S3_BUCKET=bus-mvp-data-lake
# - AWS_GLUE_CATALOG_DATABASE=bus_mvp_catalog
# - AWS_ATHENA_WORKGROUP=bus-mvp-analytics
# - QUERY_OUTPUT_PATH=s3://bus-mvp-query-results/athena-outputs/
#
# For local/mock mode:
# - ENVIRONMENT=local
