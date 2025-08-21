#!/bin/bash
echo "🧹 Restarting ENTROPY - Clean & Fixed Version"
echo "Backup created: ../entropy_backup_cleanup_20250819_161423"
echo ""

# Kill existing processes
pkill -f "node.*server.js" || true
pkill -f "react-scripts" || true

# Wait a moment
sleep 2

echo "✅ Cleanup Complete - Removed Features:"
echo "  ❌ Up/Down arrow task reordering"
echo "  ❌ Move up/down API endpoints"
echo "  ❌ Problematic CSS causing analytics issues"
echo "  ❌ Complex state management bugs"
echo ""
echo "✅ What Still Works:"
echo "  📊 Analytics Dashboard with beautiful charts"
echo "  🏷️  Category system with visual badges"
echo "  🔄 Templates and recurring tasks"
echo "  ⬅️ Move tasks back from tomorrow to today"
echo "  🕔 5 AM day boundaries"
echo "  📱 Mobile responsive design"
echo ""
echo "🎯 Task Display:"
echo "  • Clean priority-based sorting (High → Medium → Low)"
echo "  • Category badges show task grouping"
echo "  • No complex reordering - simple and reliable"
echo ""
echo "🛡️  Backup & Restore:"
echo "  📦 Backup created: ../entropy_backup_cleanup_20250819_161423"
echo "  🔄 To restore: python3 ../restore_backup.py ../entropy_backup_cleanup_20250819_161423"
echo ""

# Start the application
./start.sh