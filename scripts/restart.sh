#!/bin/bash
echo "🔄 Restarting ENTROPY with new History feature..."

# Kill existing processes
pkill -f "node.*server.js" || true
pkill -f "react-scripts" || true

# Wait a moment
sleep 2

# Start the application
./start.sh