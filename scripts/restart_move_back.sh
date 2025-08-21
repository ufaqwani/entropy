#!/bin/bash
echo "⬅️  Restarting ENTROPY with Move Back to Today..."
echo "Backup created: ../entropy_backup_move_back_20250819_012806"
echo ""

# Kill existing processes
pkill -f "node.*server.js" || true
pkill -f "react-scripts" || true

# Wait a moment
sleep 2

echo "✅ Move Back to Today Functionality Added:"
echo "  ⬅️  Move tomorrow tasks back to today with one click"
echo "  🔍 Duplicate detection prevents task conflicts"
echo "  ⚡ Instant state updates in both sections"
echo "  🎨 Visual feedback with animations and notifications"
echo "  📱 Mobile-optimized controls and layout"
echo ""
echo "🔄 How to Use:"
echo "  1. Find a task in Tomorrow's section"
echo "  2. Click the ⬅️ arrow button next to it"
echo "  3. Task instantly moves back to Today's list"
echo "  4. Complete it today or move it back to tomorrow again"
echo ""
echo "🛡️  Backup & Restore:"
echo "  📦 Backup created: ../entropy_backup_move_back_20250819_012806"
echo "  🔄 To restore: python3 ../restore_backup.py ../entropy_backup_move_back_20250819_012806"
echo ""

# Start the application
./start.sh