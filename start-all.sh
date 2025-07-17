#!/bin/bash

# Start Backend
echo "🚀 Starting Backend..."
cd backend

# Activate virtual environment
if [ -d "venv" ]; then
    source venv/bin/activate
else
    echo "⚠️  Virtual environment not found. Creating one..."
    python3 -m venv venv
    source venv/bin/activate
    echo "📦 Installing Python dependencies..."
    pip install -r requirements.txt
fi

# Install uvicorn if missing
if ! command -v uvicorn &> /dev/null
then
    echo "📦 Installing uvicorn..."
    pip install uvicorn
fi

# Run backend
uvicorn app.main:app --reload &
BACKEND_PID=$!
cd ..

# Start Frontend
echo "🎨 Starting Frontend..."
cd frontend
npm install
npm start &

# Wait for backend to finish
wait $BACKEND_PID
