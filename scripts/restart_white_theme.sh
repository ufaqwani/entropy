#!/bin/bash
echo "🔄 Restarting ENTROPY with new White Theme..."

# Kill existing processes
pkill -f "node.*server.js" || true
pkill -f "react-scripts" || true

# Wait a moment
sleep 2

echo "🎨 Starting ENTROPY with:"
echo "  ✅ White background & black text"
echo "  ✅ Modern Roboto Mono font"
echo "  ✅ Simplified, clean animations"
echo "  ✅ Mobile-optimized design"
echo ""

# Start the application
./start.sh