#!/bin/bash

echo "🎿 BIATHLON PRO - Starting application"
echo "======================================"

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed"
    exit 1
fi

# Check Node.js
if ! command -v npm &> /dev/null; then
    echo "❌ Node.js is not installed"
    exit 1
fi

# Install backend dependencies if needed
if [ ! -d "backend/venv" ]; then
    echo "📦 Installing backend dependencies..."
    cd backend
    python3 -m venv venv
    source venv/bin/activate 2>/dev/null || source venv/Scripts/activate 2>/dev/null
    pip install -r requirements.txt
    cd ..
fi

# Install frontend dependencies if needed
if [ ! -d "frontend/node_modules" ]; then
    echo "📦 Installing frontend dependencies..."
    cd frontend
    npm install
    cd ..
fi

# Start backend
echo "🚀 Starting backend on http://localhost:8000..."
cd backend
source venv/bin/activate 2>/dev/null || source venv/Scripts/activate 2>/dev/null
python main.py &
BACKEND_PID=$!
cd ..

# Wait for backend
sleep 3

# Start frontend
echo "🎨 Starting frontend on http://localhost:3000..."
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

echo ""
echo "\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\="
echo "✅ Biathlon Pro is running!"
echo "================================"
echo ""
echo "📊 Frontend: http://localhost:3000"
echo "🔧 Backend:  http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop"
echo ""

# Cleanup on exit
trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT TERM

# Wait
wait
