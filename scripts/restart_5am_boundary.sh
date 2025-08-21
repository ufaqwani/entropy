#!/bin/bash
echo "🕔 Restarting ENTROPY with 5 AM Day Boundaries..."
echo "Backup created: ../entropy_backup_5am_boundary_20250819_003010"
echo ""

# Kill existing processes
pkill -f "node.*server.js" || true
pkill -f "react-scripts" || true

# Wait a moment
sleep 2

echo "✅ 5 AM Day Boundary Implementation Complete:"
echo "  🕔 Days now start at 5 AM instead of midnight"
echo "  📅 Today: 5 AM today → 5 AM tomorrow"
echo "  📅 Tomorrow: 5 AM tomorrow → 5 AM day after"
echo "  💡 Early morning (12-5 AM) counts as previous day"
echo ""
echo "🧪 Test the boundaries:"
echo "  ./test_5am_boundaries.sh"
echo ""
echo "🛡️  Backup & Restore:"
echo "  📦 Backup created: ../entropy_backup_5am_boundary_20250819_003010"
echo "  🔄 To restore: python3 ../restore_backup.py ../entropy_backup_5am_boundary_20250819_003010"
echo ""

# Start the application
./start.sh