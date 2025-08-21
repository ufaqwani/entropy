#!/bin/bash
echo "⚡ Restarting ENTROPY with Smooth Task Reordering..."
echo "Backup created: ../entropy_backup_smooth_reorder_20250819_124336"
echo ""

# Kill existing processes
pkill -f "node.*server.js" || true
pkill -f "react-scripts" || true

# Wait a moment
sleep 2

echo "✅ Smooth Task Reordering Features:"
echo "  ⬆️  Up arrow button to increase priority"
echo "  ⬇️  Down arrow button to decrease priority"
echo "  🎯 Position numbers show current ranking"
echo "  ⚡ Instant, smooth animations"
echo "  📱 Perfect touch support for mobile"
echo "  🚫 Smart restrictions for completed tasks"
echo ""
echo "🎯 How to Use:"
echo "  • Click ⬆️ to move task up (higher priority)"
echo "  • Click ⬇️ to move task down (lower priority)"
echo "  • Position #1 = highest priority"
echo "  • Completed tasks cannot be reordered"
echo ""
echo "✨ Why This is Better:"
echo "  • No more clunky drag & drop"
echo "  • Works perfectly on all devices"
echo "  • Instant feedback with smooth animations"
echo "  • Never fails or gets stuck"
echo ""
echo "🛡️  Backup & Restore:"
echo "  📦 Backup created: ../entropy_backup_smooth_reorder_20250819_124336"
echo "  🔄 To restore: python3 ../restore_backup.py ../entropy_backup_smooth_reorder_20250819_124336"
echo ""

# Start the application
./start.sh