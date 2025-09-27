#!/bin/bash

# Data Ingestion - Development Setup Script
# ========================================
# 
# This script sets up the data ingestion development environment
# Run from the data-ingestion directory

set -e

echo "🚀 Setting up Bus MVP Data Ingestion Development Environment"
echo "============================================================"

# Check if Docker and Docker Compose are installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Copy environment file if it doesn't exist
if [ ! -f .env ]; then
    echo "📄 Creating .env file from template..."
    cp .env.example .env
    echo "✅ .env file created. Please review and update the variables as needed."
else
    echo "📄 .env file already exists"
fi

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p ./monitoring
mkdir -p ./scripts
mkdir -p ./logs

# Check if main system is running (optional)
echo "🔍 Checking main system availability..."
if docker network ls | grep -q "bus-mvp-network"; then
    echo "✅ Main system network (bus-mvp-network) found"
    MAIN_SYSTEM_AVAILABLE=true
else
    echo "⚠️  Main system network not found. You may need to start the main system first."
    MAIN_SYSTEM_AVAILABLE=false
fi

# Build the images
echo "🔨 Building data ingestion containers..."
docker-compose build

# Start supporting services first
echo "🚀 Starting supporting services (Redis)..."
docker-compose up -d redis-cache

# Wait for supporting services to be ready
echo "⏳ Waiting for supporting services to be ready..."
sleep 10

# Check if we can connect to main system databases
if [ "$MAIN_SYSTEM_AVAILABLE" = true ]; then
    echo "🔍 Checking database connectivity..."
    
    # This would need to be implemented based on your main system setup
    echo "⚠️  Database connectivity check not implemented yet"
    echo "   Please ensure your main system databases are running:"
    echo "   - PostgreSQL (sql-db1:5432)"
    echo "   - MySQL (sql-db2:3306)"
    echo "   - MongoDB (nosql-db:27017)"
fi

echo ""
echo "✅ Development environment setup complete!"
echo ""
echo "🎯 Next steps:"
echo "   1. Review and update .env file with your database credentials"
echo "   2. Ensure main system databases are running"
echo "   3. Start the ingestion services:"
echo "      docker-compose up -d"
echo "   4. Check health status:"
echo "      curl http://localhost:8090/health  # ms-passengers-db"
echo "      curl http://localhost:8091/health  # ms-trips-db" 
echo "      curl http://localhost:8092/health  # ms-tickets-db"
echo ""
echo "🔍 Useful commands:"
echo "   - View logs: docker-compose logs -f"
echo "   - Stop services: docker-compose down"
echo "   - Rebuild: docker-compose up --build"
echo ""
echo "📊 Monitoring:"
echo "   - AWS S3 Console: https://console.aws.amazon.com/s3/"
echo "   - Prometheus (optional): http://localhost:9090"
echo ""
