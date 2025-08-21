#!/bin/bash
echo "🔧 Restarting ENTROPY with Tomorrow Deletion Fix..."
echo "Backup created: ../entropy_backup_deletion_fix_20250819_001911"
echo ""

# Kill existing processes
pkill -f "node.*server.js" || true
pkill -f "react-scripts" || true

# Wait a moment
sleep 2

echo "✅ Tomorrow Task Deletion Fixes Applied:"
echo "  🗑️  Tasks deleted from tomorrow stay deleted"
echo "  🔄 Backend properly cleans up related moved tasks"
echo "  ⚡ Frontend refreshes state after deletion"
echo "  🧹 Database queries exclude moved/deleted tasks"
echo ""
echo "🧹 Optional cleanup:"
echo "  ./cleanup_orphaned_tasks.sh (removes orphaned data)"
echo ""
echo "🛡️  Backup & Restore:"
echo "  📦 Backup created: ../entropy_backup_deletion_fix_20250819_001911"
echo "  🔄 To restore: python3 ../restore_backup.py ../entropy_backup_deletion_fix_20250819_001911"
echo ""

# Start the application
./start.sh