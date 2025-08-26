#!/bin/bash

# Railway deployment startup script
echo "Starting Railway deployment..."

# Set default port if not provided by Railway
export PORT=${PORT:-3000}

# Activate virtual environment if it exists
if [ -d "/opt/venv" ]; then
    export PATH="/opt/venv/bin:$PATH"
    echo "Using virtual environment: /opt/venv"
fi

echo "PORT set to: $PORT"
echo "Python path: $(which python)"

# Start backend in background on port 8001
echo "Starting FastAPI backend on port 8001..."
cd /app && python backend/server.py &
BACKEND_PID=$!

# Wait for backend to start
echo "Waiting for backend to start..."
sleep 5

# Check if backend is running
if kill -0 $BACKEND_PID 2>/dev/null; then
    echo "Backend started successfully (PID: $BACKEND_PID)"
else
    echo "Backend failed to start"
    exit 1
fi

# Start frontend on Railway's PORT
echo "Starting Next.js frontend on port $PORT..."
cd /app && npm start -- --hostname 0.0.0.0 --port $PORT

# If frontend exits, cleanup backend
echo "Frontend stopped, cleaning up backend..."
kill $BACKEND_PID 2>/dev/null || true