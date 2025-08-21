#!/bin/bash
echo "🔄 ENTROPY - Complete Fresh State Reset"
echo "======================================"
echo ""

if [ "$1" != "--confirm" ]; then
    echo "⚠️  WARNING: This will delete ALL your tasks and progress!"
    echo ""
    echo "To proceed, run: ./fresh_start.sh --confirm"
    exit 0
fi

echo "🗃️  Step 1: Resetting database..."
./reset_database.sh

echo ""
echo "🌐 Step 2: Clear frontend storage..."
echo "    Open this file in your browser: file://$(pwd)/clear_frontend_storage.html"
echo "    Click 'Clear All Frontend Storage' and close the tab"
echo ""

read -p "Press Enter after clearing frontend storage..."

echo ""
echo "🔄 Step 3: Restarting application..."

# Kill existing processes
pkill -f "node.*server.js" || true
pkill -f "react-scripts" || true

sleep 2

# Start fresh
./start.sh &

echo ""
echo "🧪 Step 4: Testing persistence..."
sleep 10
./test_persistence.sh

echo ""
echo "🎉 Fresh state setup complete!"
echo "=============================="
echo ""
echo "📱 Your app is running at: http://localhost:3000"
echo "🧪 Data persistence test results above"
echo ""
echo "🛡️  Backup created: ../entropy_backup_before_reset_20250821_014536"
echo ""