# MS Analytics - Development Guide

## Quick Start

1. **Install Dependencies**
   ```bash
   ./test_setup.sh
   ```

2. **Configure Environment**
   ```bash
   cp .env.template .env
   # Edit .env with your settings
   ```

3. **Start Development Server**
   ```bash
   ./start_dev.sh
   ```

4. **Access API Documentation**
   - Swagger UI: http://localhost:8010/docs
   - ReDoc: http://localhost:8010/redoc

## Environment Modes

### Local Mode (Mock Data)
```bash
ENVIRONMENT=local
```
- Uses mock data service
- No AWS credentials required
- Perfect for development and testing

### AWS Mode (Real Data)
```bash
ENVIRONMENT=aws
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
AWS_REGION=us-east-1
# ... other AWS settings
```
- Uses real AWS Athena, S3, and Glue
- Requires AWS credentials and resources

## API Endpoints

### Health Checks
- `GET /api/v1/health` - Full health check
- `GET /api/v1/health/ready` - Readiness probe
- `GET /api/v1/health/live` - Liveness probe

### Analytics
- `GET /api/v1/analytics/revenue-by-route` - Revenue analysis
- `GET /api/v1/analytics/occupancy-trends` - Occupancy trends
- `GET /api/v1/analytics/customer-segmentation` - Customer segments
- `GET /api/v1/analytics/route-performance` - Route performance

### Custom Queries (AWS only)
- `POST /api/v1/query/custom` - Execute custom SQL
- `GET /api/v1/query/tables` - List available tables

## Development Commands

```bash
# Test basic setup
./test_setup.sh

# Start development server
./start_dev.sh

# Run tests (once pytest is set up)
pytest tests/

# Format code
black src/
isort src/

# Type checking (if mypy added)
mypy src/
```

## Docker

```bash
# Build image
docker build -t ms-analytics .

# Run with local mode
docker run -p 8010:8010 -e ENVIRONMENT=local ms-analytics

# Run with AWS mode
docker run -p 8010:8010 --env-file .env ms-analytics
```

## Project Structure

```
ms-analytics/
├── src/
│   ├── main.py                 # FastAPI app entry point
│   └── app/
│       ├── api/                # API routes
│       ├── core/               # Configuration & logging
│       ├── models/             # Pydantic models
│       ├── services/           # Business logic
│       ├── queries/            # SQL templates
│       └── utils/              # Helper functions
├── tests/                      # Test files
├── requirements.txt            # Python dependencies
├── Dockerfile                  # Container configuration
├── .env.template              # Environment template
└── README_DEV.md              # This file
```

## Next Steps

1. Install dependencies and test basic setup
2. Configure AWS resources (if using AWS mode)
3. Test endpoints with sample queries
4. Integrate with other microservices
5. Add comprehensive tests
6. Set up CI/CD pipeline
