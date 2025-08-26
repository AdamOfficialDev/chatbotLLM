# Multi-stage build for optimized Railway deployment
FROM node:18-alpine AS frontend-builder

# Set working directory for frontend
WORKDIR /app

# Copy package files
COPY package*.json yarn.lock ./

# Install frontend dependencies
RUN yarn install --frozen-lockfile

# Copy frontend source
COPY . .

# Build Next.js application
RUN yarn build

# Python backend stage
FROM python:3.11-slim AS backend-builder

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy backend requirements
COPY backend/requirements.txt ./backend/

# Install Python dependencies
RUN pip install --no-cache-dir -r backend/requirements.txt

# Final stage - combine frontend and backend
FROM python:3.11-slim

# Install Node.js for running Next.js
RUN apt-get update && apt-get install -y \
    curl \
    && curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy Python dependencies from backend-builder
COPY --from=backend-builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=backend-builder /usr/local/bin /usr/local/bin

# Copy built Next.js application from frontend-builder
COPY --from=frontend-builder /app/.next ./.next
COPY --from=frontend-builder /app/node_modules ./node_modules
COPY --from=frontend-builder /app/package.json ./
COPY --from=frontend-builder /app/next.config.js ./
COPY --from=frontend-builder /app/public ./public

# Copy backend source
COPY backend ./backend

# Copy other necessary files
COPY components ./components
COPY lib ./lib
COPY hooks ./hooks
COPY app ./app
COPY tailwind.config.js ./
COPY postcss.config.js ./
COPY jsconfig.json ./
COPY components.json ./

# Create start script
RUN echo '#!/bin/bash\n\
# Get PORT from environment (Railway provides this)\n\
export PORT=${PORT:-3000}\n\
echo "Starting on PORT: $PORT"\n\
\n\
# Start backend in background\n\
cd /app && python backend/server.py &\n\
BACKEND_PID=$!\n\
\n\
# Wait for backend to start\n\
echo "Waiting for backend..."\n\
sleep 5\n\
\n\
# Check if backend started\n\
if kill -0 $BACKEND_PID 2>/dev/null; then\n\
    echo "Backend running (PID: $BACKEND_PID)"\n\
else\n\
    echo "Backend failed to start"\n\
    exit 1\n\
fi\n\
\n\
# Start frontend on Railway PORT\n\
cd /app && npm start -- --hostname 0.0.0.0 --port $PORT\n\
' > start.sh && chmod +x start.sh

# Expose port (Railway will set PORT environment variable)
EXPOSE $PORT

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
  CMD curl -f http://localhost:$PORT/api/health || exit 1

# Start the application
CMD ["./start.sh"]