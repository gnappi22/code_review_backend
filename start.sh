#!/bin/bash

# Code Review Service Startup Script

echo "🚀 Starting Code Review Service..."

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Creating from template..."
    cp env.example .env
    echo "📝 Please edit .env file and add your OpenAI API key"
    echo "   Then run this script again."
    exit 1
fi

# Check if OPENAI_API_KEY is set
if ! grep -q "OPENAI_API_KEY=sk-" .env; then
    echo "⚠️  OpenAI API key not found in .env file"
    echo "📝 Please add your OpenAI API key to the .env file"
    exit 1
fi

echo "✅ Environment configuration looks good"

# Create data directory if it doesn't exist
mkdir -p data

# Start the service with Docker Compose
echo "🐳 Starting service with Docker Compose..."
docker-compose up --build

echo "🎉 Service started! Visit http://localhost:8000/docs for API documentation"


