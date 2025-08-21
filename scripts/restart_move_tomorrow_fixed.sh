#!/bin/bash
echo "🔧 Restarting ENTROPY with Move to Tomorrow Fix..."
echo "Backup created: ../entropy_backup_move_disappear_fix_20250819_000424"
echo ""

# Kill existing processes
pkill -f "node.*server.js" || true
pkill -f "react-scripts" || true

# Wait a moment
sleep 2

echo "✅ Move to Tomorrow Fixes Applied:"
echo "  📅 Tasks moved to tomorrow now appear in Tomorrow section"
echo "  🔄 Backend creates new tasks with tomorrow's date"
echo "  ⚡ Frontend properly displays both today and tomorrow tasks"
echo "  📋 Tomorrow tasks can be completed and deleted"
echo ""
echo "🛡️  Backup & Restore:"
echo "  📦 Backup created: ../entropy_backup_move_disappear_fix_20250819_000424"
echo "  🔄 To restore: python3 ../restore_backup.py ../entropy_backup_move_disappear_fix_20250819_000424"
echo ""

# Start the application
./start.sh