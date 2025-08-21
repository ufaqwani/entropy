#!/bin/bash
echo "🔄 Restarting ENTROPY with Drag & Drop Reordering..."
echo "Backup created: ../entropy_backup_reorder_20250819_123720"
echo ""

# Install dependencies first
echo "📦 Installing drag & drop dependencies..."
./install_dnd.sh

# Kill existing processes
pkill -f "node.*server.js" || true
pkill -f "react-scripts" || true

# Wait a moment
sleep 2

echo "✅ Drag & Drop Task Reordering Features:"
echo "  🔄 Drag tasks to reorder by importance"
echo "  🎯 Automatic priority updates based on position"
echo "  📍 Position indicators (#1, #2, #3)"
echo "  🚫 Completed tasks cannot be reordered"
echo "  📱 Mobile-friendly touch drag support"
echo ""
echo "🎯 How to Use:"
echo "  1. Grab the ⋮⋮ handle next to any task"
echo "  2. Drag it up or down to reorder"
echo "  3. Drop it in the new position"
echo "  4. Priority automatically updates (top = high priority)"
echo ""
echo "🛡️  Backup & Restore:"
echo "  📦 Backup created: ../entropy_backup_reorder_20250819_123720"
echo "  🔄 To restore: python3 ../restore_backup.py ../entropy_backup_reorder_20250819_123720"
echo ""

# Start the application
./start.sh