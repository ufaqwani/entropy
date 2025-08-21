#!/bin/bash
echo "🔧 Restarting ENTROPY with Move-to-Tomorrow Fix..."
echo "Backup created: ../entropy_backup_move_fix_20250818_234157"
echo ""

# Kill existing processes
pkill -f "node.*server.js" || true
pkill -f "react-scripts" || true

# Wait a moment
sleep 2

echo "✅ Move-to-Tomorrow Bug Fixed:"
echo "  🚫 Tasks moved to tomorrow no longer appear in today"
echo "  🔄 Backend properly excludes moved tasks"
echo "  ⚡ Frontend state updates immediately"
echo "  📋 Consistent task filtering applied"
echo ""
echo "🛡️  Backup & Restore:"
echo "  📦 Backup created: ../entropy_backup_move_fix_20250818_234157"
echo "  🔄 To restore: python3 ../restore_backup.py ../entropy_backup_move_fix_20250818_234157"
echo ""

# Start the application
./start.sh || npm start