#!/bin/bash
echo "🔄 Restarting ENTROPY with Smart Recurring Templates..."
echo "Backup created: ../entropy_backup_recurring_20250819_012137"
echo ""

# Install dependencies first
echo "📦 Installing dependencies..."
./install_cron.sh

# Kill existing processes
pkill -f "node.*server.js" || true
pkill -f "react-scripts" || true

# Wait a moment
sleep 2

echo "✅ Smart Recurring Templates System Implemented:"
echo "  🔄 Create unlimited recurring task templates"
echo "  ⏰ Automatic task generation at 5 AM boundaries"
echo "  📅 Daily, weekly, monthly, and custom schedules"
echo "  🎯 Category integration for organized automation"
echo "  📊 Template statistics and upcoming runs preview"
echo "  ⚡ Manual template execution and toggle control"
echo ""
echo "🎯 Getting Started:"
echo "  1. Click 'Templates' button to create your first template"
echo "  2. Set up Daily Planning, Weekly Reviews, etc."
echo "  3. Templates automatically create tasks at scheduled times"
echo "  4. Check 'Upcoming Runs' to see what's scheduled"
echo ""
echo "🛡️  Backup & Restore:"
echo "  📦 Backup created: ../entropy_backup_recurring_20250819_012137"
echo "  🔄 To restore: python3 ../restore_backup.py ../entropy_backup_recurring_20250819_012137"
echo ""

# Start the application
./start.sh