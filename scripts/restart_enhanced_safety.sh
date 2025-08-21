#!/bin/bash
echo "🛡️  Restarting ENTROPY with Enhanced Safety Features..."
echo "Backup created: ../entropy_backup_20250818_225250"
echo ""

# Kill existing processes
pkill -f "node.*server.js" || true
pkill -f "react-scripts" || true

# Wait a moment
sleep 2

echo "✅ New Safety Features Added:"
echo "  📦 Automatic backup system created"
echo "  🗑️  Delete tomorrow tasks functionality"
echo "  🚫 Duplicate task prevention"
echo "  🔄 Enhanced error handling"
echo "  📱 Better mobile experience"
echo ""
echo "🛡️  Backup & Restore:"
echo "  📦 Backup created: ../entropy_backup_20250818_225250"
echo "  🔄 To restore: python3 ../restore_backup.py ../entropy_backup_20250818_225250"
echo ""

# Start the application
./start.sh