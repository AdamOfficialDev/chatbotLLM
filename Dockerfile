# Railway-optimized Dockerfile for Chat AI Application
FROM node:18-alpine

# Install Python for backend
RUN apk add --no-cache python3 py3-pip curl

# Set working directory
WORKDIR /app

# Copy package files (handle missing yarn.lock gracefully)
COPY package*.json ./
COPY yarn.loc* ./

# Install frontend dependencies with fallback
RUN yarn install --frozen-lockfile --network-timeout 100000 || \
    yarn install --network-timeout 100000

# Copy backend requirements first for better caching
COPY backend/requirements.txt ./backend/requirements.txt

# Install Python dependencies with retry logic
RUN pip3 install --no-cache-dir --timeout 100 --retries 3 -r backend/requirements.txt

# Copy all source files
COPY . .

# Build Next.js application
RUN yarn build

# Create optimized start script for Railway
RUN echo '#!/bin/sh\n\
# Railway startup script\n\
export PORT=${PORT:-3000}\n\
echo "=== Railway Deployment Starting ==="\n\
echo "PORT: $PORT"\n\
echo "NODE_ENV: $NODE_ENV"\n\
echo "Starting backend on port 8001..."\n\
cd /app && python3 backend/server.py &\n\
BACKEND_PID=$!\n\
echo "Backend PID: $BACKEND_PID"\n\
sleep 10\n\
echo "Starting frontend on port $PORT..."\n\
cd /app && npm start -- --hostname 0.0.0.0 --port $PORT\n\
' > start.sh && chmod +x start.sh

# Expose port for Railway
EXPOSE $PORT

# Health check for Railway monitoring
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
  CMD curl -f http://localhost:$PORT/api/health || exit 1

# Start the application
CMD ["./start.sh"]