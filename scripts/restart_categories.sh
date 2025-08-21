#!/bin/bash
echo "📂 Restarting ENTROPY with Required Categories System..."
echo "Backup created: ../entropy_backup_categories_20250819_005603"
echo ""

# Kill existing processes
pkill -f "node.*server.js" || true
pkill -f "react-scripts" || true

# Wait a moment
sleep 2

echo "✅ Professional Category System Implemented:"
echo "  📂 Create unlimited custom categories"
echo "  🎯 Every task MUST have a category (enforced)"
echo "  🎨 Visual organization with colors and icons"
echo "  📊 Task grouping by category in lists"
echo "  🗑️  Safe category deletion (prevents data loss)"
echo ""
echo "🎯 Getting Started:"
echo "  1. Click 'Categories' button to create your first category"
echo "  2. Add tasks - category selection is required"
echo "  3. Tasks are automatically grouped by category"
echo ""
echo "🛡️  Backup & Restore:"
echo "  📦 Backup created: ../entropy_backup_categories_20250819_005603"
echo "  🔄 To restore: python3 ../restore_backup.py ../entropy_backup_categories_20250819_005603"
echo ""

# Start the application
./start.sh