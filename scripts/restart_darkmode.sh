#!/bin/bash
echo "🌙 Restarting ENTROPY with Dark Mode Theme..."
echo "Backup created: ../entropy_backup_darkmode_only_20250818_233321"
echo ""

# Kill existing processes
pkill -f "node.*server.js" || true
pkill -f "react-scripts" || true

# Wait a moment
sleep 2

echo "✅ Dark Mode Features Added:"
echo "  🌙 Theme toggle button in header"
echo "  🎨 Complete light/dark theme system"
echo "  💾 Automatic theme preference saving"
echo "  📱 Mobile-optimized theme toggle"
echo "  🔄 Smooth theme transitions"
echo ""
echo "🛡️  Backup & Restore:"
echo "  📦 Backup created: ../entropy_backup_darkmode_only_20250818_233321"
echo "  🔄 To restore: python3 ../restore_backup.py ../entropy_backup_darkmode_only_20250818_233321"
echo ""

# Start the application
./start.sh