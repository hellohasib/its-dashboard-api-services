#!/bin/bash

# Script to start ANPR service with Docker

set -e

echo "🚀 Starting ANPR Service with Docker..."
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found!"
    echo "Creating .env from .env.example..."
    
    if [ -f .env.example ]; then
        cp .env.example .env
        echo "✅ Created .env file. Please review and update the values."
        echo ""
    else
        echo "❌ .env.example not found. Please create a .env file manually."
        exit 1
    fi
fi

# Start services
echo "Starting Docker containers..."
docker-compose up -d mysql redis

echo "⏳ Waiting for database to be ready..."
sleep 10

echo "Starting ANPR service..."
docker-compose up -d anpr-service

echo ""
echo "✅ ANPR Service is starting!"
echo ""
echo "📊 Service URLs:"
echo "   - ANPR API: http://localhost:8002"
echo "   - Health Check: http://localhost:8002/health"
echo "   - API Docs: http://localhost:8002/docs"
echo ""
echo "📝 Useful commands:"
echo "   - View logs: docker-compose logs -f anpr-service"
echo "   - Check status: docker-compose ps"
echo "   - Stop service: docker-compose down"
echo ""
echo "🔍 Testing the service:"
echo "   curl http://localhost:8002/health"
echo ""

