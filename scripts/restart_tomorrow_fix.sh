#!/bin/bash
echo "🔄 Restarting ENTROPY with Tomorrow Tasks & Custom Notifications..."

# Kill existing processes
pkill -f "node.*server.js" || true
pkill -f "react-scripts" || true

# Wait a moment
sleep 2

echo "✅ New Features Added:"
echo "  📅 Tomorrow tasks section shows moved tasks"
echo "  🔔 Beautiful in-app notifications replace ugly alerts"
echo "  🎯 Better task organization and feedback"
echo ""

# Start the application
./start.sh