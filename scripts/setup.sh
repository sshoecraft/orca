#!/bin/bash

# Orca Job Orchestrator Setup Script
# Sets up the environment and initializes the database

set -e

echo "🐋 Orca Job Orchestrator Setup"
echo "=============================="

# Check Python version
echo "Checking Python version..."
python3 --version

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env file with your configuration"
else
    echo "✅ .env file already exists"
fi

# Check PostgreSQL connection
echo "Checking PostgreSQL connection..."
if command -v psql &> /dev/null; then
    echo "PostgreSQL client found"
    
    # Try to connect to database
    if psql postgresql://postgres:postgres@localhost/postgres -c "\l" &> /dev/null; then
        echo "✅ PostgreSQL connection successful"
        
        # Create database if it doesn't exist
        psql postgresql://postgres:postgres@localhost/postgres -c "CREATE DATABASE orca;" || echo "Database 'orca' already exists or creation failed"
        
        # Initialize database schema
        echo "Initializing database schema..."
        psql postgresql://postgres:postgres@localhost/orca -f database/init.sql
        echo "✅ Database schema initialized"
    else
        echo "❌ Failed to connect to PostgreSQL"
        echo "Please ensure PostgreSQL is running and accessible with:"
        echo "  - Host: localhost"
        echo "  - User: postgres"
        echo "  - Password: postgres"
        echo "  - Database: orca"
    fi
else
    echo "❌ psql command not found. Please install PostgreSQL client"
fi

echo ""
echo "🐋 Setup complete!"
echo ""
echo "To start the API server:"
echo "  source venv/bin/activate"
echo "  cd backend/api"
echo "  python main.py"
echo ""
echo "Or use uvicorn directly:"
echo "  uvicorn backend.api.main:app --reload --host 0.0.0.0 --port 8000"
echo ""
echo "API Documentation: http://localhost:8000/docs"
echo "Health Check: http://localhost:8000/health"