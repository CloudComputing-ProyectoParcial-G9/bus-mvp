#!/bin/bash

# MS Analytics - Quick Test Script

echo "🧪 MS Analytics Quick Test"
echo "========================="

# Check Python version
python3 --version

# Install dependencies if needed
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
else
    source venv/bin/activate
fi

# Run basic tests
echo "🔍 Testing basic imports..."
cd src

# Test imports
python3 -c "
try:
    from app.core.config import settings
    print('✅ Config import successful')
except Exception as e:
    print(f'❌ Config import failed: {e}')

try:
    from app.services.mock_service import MockAnalyticsService
    print('✅ Mock service import successful')
except Exception as e:
    print(f'❌ Mock service import failed: {e}')

try:
    from app.models.responses import HealthResponse
    print('✅ Models import successful')
except Exception as e:
    print(f'❌ Models import failed: {e}')
"

echo ""
echo "🚀 To start the development server:"
echo "   ./start_dev.sh"
echo ""
echo "📚 API Documentation will be available at:"
echo "   http://localhost:8010/docs"
