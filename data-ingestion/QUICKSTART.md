# Data Ingestion - Quick Start Guide

## Overview

This directory contains 3 specialized database ingestion containers for the Bus MVP system:

- **ms-passengers-db**: PostgreSQL CDC ingestion for passenger data
- **ms-trips-db**: MySQL binlog ingestion for trips and routes data  
- **ms-tickets-db**: MongoDB change streams ingestion for tickets data

Each container extracts data from its respective microservice database and stores it in object storage for analytics.

## Quick Start

### 1. Setup Environment

```bash
cd data-ingestion/

# Copy and configure environment variables
cp .env.example .env
# Edit .env with your database credentials

# Run setup script
./setup-dev.sh
```

### 2. Start Services

```bash
# Start all ingestion services
docker-compose up -d

# Or start individual services  
docker-compose up ms-passengers-db redis-cache -d
```

### 3. Check Health

```bash
# Check service health
curl http://localhost:8090/health  # ms-passengers-db
curl http://localhost:8091/health  # ms-trips-db
curl http://localhost:8092/health  # ms-tickets-db

# View logs
docker-compose logs -f ms-passengers-db
```

## Architecture

```
┌─────────────────────┐    ┌─────────────────────┐    ┌─────────────────────┐
│   ms-passengers-db  │    │    ms-trips-db      │    │   ms-tickets-db     │
│   (PostgreSQL CDC)  │    │   (MySQL Binlog)   │    │ (MongoDB Streams)   │
├─────────────────────┤    ├─────────────────────┤    ├─────────────────────┤
│ • CDC + Full Sync   │    │ • Binlog + Full     │    │ • Change Streams    │
│ • Health: :8090     │    │ • Health: :8091     │    │ • Health: :8092     │
│ • Batch: 1000       │    │ • Batch: 500        │    │ • Batch: 2000       │
│ • Interval: 5min    │    │ • Interval: 2min    │    │ • Real-time         │
└─────────┬───────────┘    └─────────┬───────────┘    └─────────┬───────────┘
          │                          │                          │
          └──────────────────────────┼──────────────────────────┘
                                     │
                          ┌─────────┴───────────┐
                          │   Object Storage    │
                          │      AWS S3         │
                          └─────────────────────┘
```

## Configuration

### Database Connections

```env
# PostgreSQL (ms-passengers)
SQL1_HOST=sql-db1
SQL1_DB=passengers_db
SQL1_USER=postgres
SQL1_PASSWORD=your_password

# MySQL (ms-trips)
SQL2_HOST=sql-db2  
SQL2_DB=trips_db
SQL2_USER=mysql
SQL2_PASSWORD=your_password

# MongoDB (ms-tickets)
NOSQL_HOST=nosql-db
NOSQL_DB=tickets_db
NOSQL_USER=mongo
NOSQL_PASSWORD=your_password
```

### Storage Configuration

```env
# AWS S3 (Production and Development)
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_REGION=us-east-1
AWS_S3_BUCKET=bus-mvp-data-lake
```

## Integration with Main System

### Option 1: Combined Docker Compose

```bash
# From infra/ directory
docker-compose -f docker-compose.yml -f ../data-ingestion/docker-compose.yml up
```

### Option 2: Network Connection

```bash
# Start main system first
cd infra/
docker-compose up -d

# Then start ingestion (will connect to bus-mvp-network)
cd ../data-ingestion/
docker-compose up -d
```

## Data Flow

### 1. MS-Passengers (PostgreSQL)
- **Initial**: Full table scan
- **Incremental**: CDC via replication slots
- **Frequency**: Every 5 minutes + real-time CDC
- **Data**: passenger profiles, registrations

### 2. MS-Trips (MySQL)
- **Initial**: Full extraction of trips & routes
- **Incremental**: Binary log parsing  
- **Frequency**: Every 2 minutes (trips), hourly (routes)
- **Data**: trip schedules, routes, availability

### 3. MS-Tickets (MongoDB)
- **Initial**: Collection scan
- **Incremental**: Change streams
- **Frequency**: Real-time + daily backup
- **Data**: bookings, ticket sales, payments

## Monitoring

### Health Endpoints

- `GET /health` - Overall health status
- `GET /health/ready` - Readiness probe
- `GET /health/live` - Liveness probe  
- `GET /metrics` - Prometheus metrics

### S3 Console
- URL: AWS Console S3 service  
   - Bucket: bus-mvp-data-lake### Logs
```bash
# View all logs
docker-compose logs -f

# Service-specific logs
docker-compose logs -f ms-passengers-db
docker-compose logs -f ms-trips-db
docker-compose logs -f ms-tickets-db

# Error logs only
docker-compose logs -f | grep ERROR
```

## Development

### Testing Connectivity

```bash
# Test database connections
docker-compose exec ms-passengers-db python scripts/health_check.py
docker-compose exec ms-trips-db python scripts/health_check.py
docker-compose exec ms-tickets-db python scripts/health_check.py
```

### Manual Data Extraction

```bash
# Run manual extraction (for testing)
docker-compose exec ms-passengers-db python -c "
import asyncio
from src.main import main
asyncio.run(main())
"
```

### Debugging

```bash
# Access container shell
docker-compose exec ms-passengers-db bash

# View container logs
docker logs bus-mvp-passengers-ingestion -f

# Check network connectivity
docker-compose exec ms-passengers-db ping sql-db1
```

## Troubleshooting

### Common Issues

1. **Database Connection Failed**
   ```bash
   # Check main system is running
   docker ps | grep sql-db1
   
   # Check network connectivity
   docker network ls | grep bus-mvp
   ```

2. **CDC/Change Streams Not Working**
   ```bash
   # PostgreSQL: Check replication slots
   docker exec sql-db1 psql -U postgres -d passengers_db -c "SELECT * FROM pg_replication_slots;"
   
   # MongoDB: Check replica set status
   docker exec nosql-db mongosh --eval "rs.status()"
   ```

3. **Object Storage Issues**
   ```bash
   # Check AWS S3 connectivity
   aws s3 ls s3://bus-mvp-data
   
   # Or test with Python
   python -c "import boto3; print(boto3.client('s3').list_buckets())"
   ```

### Performance Tuning

```env
# Increase batch sizes for better throughput
BATCH_SIZE=2000

# Reduce extraction intervals for lower latency  
EXTRACTION_INTERVAL=60

# Enable parallel processing
PARALLEL_WORKERS=4
```

## Production Deployment

### Environment Variables
```env
ENVIRONMENT=production
CDC_ENABLED=true
METRICS_ENABLED=true
LOG_LEVEL=INFO
```

### Security
- Use secrets management for database credentials
- Enable SSL/TLS for database connections
- Configure proper IAM roles for object storage

### Scaling
- Increase resource limits in docker-compose.yml
- Use multiple workers for parallel processing
- Monitor metrics and adjust batch sizes

## Support

For detailed information, see the main [README.md](README.md) file which contains comprehensive documentation including:

- Network requirements and configuration
- Database setup prerequisites
- CDC configuration steps
- Performance testing guidelines
- Integration patterns
- Monitoring and alerting setup
