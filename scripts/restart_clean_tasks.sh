#!/bin/bash
echo "📋 Restarting ENTROPY with Clean Task Display..."
echo "Backup created: ../entropy_backup_task_display_fix_20250819_121513"
echo ""

# Kill existing processes
pkill -f "node.*server.js" || true
pkill -f "react-scripts" || true

# Wait a moment
sleep 2

echo "✅ Clean Task Display Features:"
echo "  📊 Tasks sorted by priority (High → Medium → Low)"
echo "  🏷️  Category badges within each task"
echo "  📱 Clean, compact layout that saves space"
echo "  🎨 Priority indicators and visual cues"
echo "  💫 Smooth hover animations and interactions"
echo ""
echo "🎯 Task Display Improvements:"
echo "  • No more category grouping sections"
echo "  • Priority-first sorting for better focus"
echo "  • Compact category badges with icons"
echo "  • Left border priority strips"
echo "  • Enhanced mobile responsive design"
echo ""
echo "🛡️  Backup & Restore:"
echo "  📦 Backup created: ../entropy_backup_task_display_fix_20250819_121513"
echo "  🔄 To restore: python3 ../restore_backup.py ../entropy_backup_task_display_fix_20250819_121513"
echo ""

# Start the application
./start.sh