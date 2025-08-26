# Simple Railway-optimized Dockerfile
FROM node:18-alpine

# Install Python for backend
RUN apk add --no-cache python3 py3-pip

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json yarn.lock ./

# Install frontend dependencies
RUN yarn install --production=false

# Copy all source files
COPY . .

# Install Python dependencies
RUN pip3 install -r backend/requirements.txt

# Build Next.js application
RUN yarn build

# Create simple start script
RUN echo '#!/bin/sh\n\
export PORT=${PORT:-3000}\n\
echo "Starting on PORT: $PORT"\n\
echo "Starting backend..."\n\
cd /app && python3 backend/server.py &\n\
sleep 5\n\
echo "Starting frontend..."\n\
cd /app && npm start -- --hostname 0.0.0.0 --port $PORT\n\
' > start.sh && chmod +x start.sh

# Expose port
EXPOSE $PORT

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
  CMD wget --no-verbose --tries=1 --spider http://localhost:$PORT/ || exit 1

# Start the application
CMD ["./start.sh"]