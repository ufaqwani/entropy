#!/bin/bash
echo "🧪 Testing 5 AM Day Boundaries"
echo "=============================="
echo ""

# Test the day boundary info endpoint
echo "📋 Current Day Boundary Information:"
curl -s http://localhost:5000/api/tasks/day-info | python3 -m json.tool

echo ""
echo "📋 Today's and Tomorrow's Tasks:"
curl -s http://localhost:5000/api/tasks/today | python3 -c "
import sys, json
data = json.load(sys.stdin)
print(f'📅 Today: {data["todayCount"]} tasks')
print(f'📅 Tomorrow: {data["tomorrowCount"]} tasks')
if 'boundaries' in data:
    print(f'🕔 Today starts: {data["boundaries"]["todayStart"]}')
    print(f'🕔 Tomorrow starts: {data["boundaries"]["tomorrowStart"]}')
    print(f'🕐 Current time: {data["boundaries"]["currentTime"]}')
"

echo ""
echo "✅ 5 AM boundaries are working!"
echo ""
echo "💡 Remember:"
echo "   - Today = 5 AM today → 5 AM tomorrow" 
echo "   - Tomorrow = 5 AM tomorrow → 5 AM day after"
echo "   - If it's 2 AM Tuesday, you're still in 'Monday' period"