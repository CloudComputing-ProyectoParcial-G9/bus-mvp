#!/bin/bash

# MS Analytics Development Server Startup Script

echo "🚀 Starting MS Analytics Development Server..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📚 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file from template..."
    cp .env.template .env
    echo "✏️  Please edit .env file with your configuration"
fi

# Start the development server
echo "🌟 Starting FastAPI development server..."
cd src
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8010
