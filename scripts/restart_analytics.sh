#!/bin/bash
echo "📊 Restarting ENTROPY with Advanced Analytics Dashboard..."
echo "Backup created: ../entropy_backup_analytics_20250819_015221"
echo ""

# Install dependencies first
echo "📦 Installing Chart.js dependencies..."
./install_chartjs.sh

# Kill existing processes
pkill -f "node.*server.js" || true
pkill -f "react-scripts" || true

# Wait a moment
sleep 2

echo "✅ Advanced Analytics Dashboard Implemented:"
echo "  📊 Comprehensive overview with key metrics"
echo "  📈 Beautiful charts with completion trends"
echo "  🎯 Category performance breakdown"
echo "  📅 7-day productivity trends analysis"
echo "  🏆 Completion streaks and patterns"
echo "  🎨 Professional responsive design"
echo ""
echo "🎯 Analytics Features:"
echo "  • Overview: Total stats, period comparisons, bar charts"
echo "  • Categories: Pie charts, completion rates, performance"
echo "  • Trends: 7-day line charts, daily breakdowns"
echo "  • Patterns: Priority distribution, streaks, top categories"
echo ""
echo "🛡️  Backup & Restore:"
echo "  📦 Backup created: ../entropy_backup_analytics_20250819_015221"
echo "  🔄 To restore: python3 ../restore_backup.py ../entropy_backup_analytics_20250819_015221"
echo ""

# Start the application
./start.sh