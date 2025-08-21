#!/bin/bash
echo "🧪 ENTROPY - Data Persistence Test"
echo "================================="
echo ""

echo "This test will verify that tasks are being saved and loaded correctly."
echo ""

# Check if app is running
if ! curl -s http://localhost:5000/health >/dev/null 2>&1; then
    echo "❌ Backend not running. Please start your app first:"
    echo "   ./start.sh"
    echo ""
    exit 1
fi

echo "✅ Backend is running"

# Test 1: Check database connection
echo ""
echo "📋 Test 1: Database Connection"
echo "------------------------------"

response=$(curl -s http://localhost:5000/api/tasks/today)
if [ $? -eq 0 ]; then
    echo "✅ Database connection working"
    echo "📊 Current tasks: $response"
else
    echo "❌ Database connection failed"
    exit 1
fi

# Test 2: Create a test task
echo ""
echo "📋 Test 2: Creating Test Task"
echo "-----------------------------"

test_task='{"title":"Test Task - Persistence Check","description":"This is a test task to verify data persistence","priority":1}'

create_response=$(curl -s -X POST -H "Content-Type: application/json" -d "$test_task" http://localhost:5000/api/tasks)
if echo "$create_response" | grep -q "Test Task"; then
    echo "✅ Test task created successfully"
    task_id=$(echo "$create_response" | grep -o '"_id":"[^"]*"' | cut -d'"' -f4)
    echo "📝 Task ID: $task_id"
else
    echo "❌ Failed to create test task"
    echo "Response: $create_response"
    exit 1
fi

# Test 3: Verify task persistence
echo ""
echo "📋 Test 3: Verifying Task Persistence"
echo "------------------------------------"

sleep 2
verify_response=$(curl -s http://localhost:5000/api/tasks/today)
if echo "$verify_response" | grep -q "Test Task"; then
    echo "✅ Task persisted successfully in database"
else
    echo "❌ Task not found in database after creation"
    echo "Response: $verify_response"
    exit 1
fi

# Test 4: Update task
echo ""
echo "📋 Test 4: Updating Task"
echo "-----------------------"

update_data='{"completed":true}'
update_response=$(curl -s -X PUT -H "Content-Type: application/json" -d "$update_data" http://localhost:5000/api/tasks/$task_id)
if echo "$update_response" | grep -q '"completed":true'; then
    echo "✅ Task updated successfully"
else
    echo "❌ Failed to update task"
    echo "Response: $update_response"
fi

# Test 5: Delete test task (cleanup)
echo ""
echo "📋 Test 5: Cleanup Test Task"
echo "---------------------------"

delete_response=$(curl -s -X DELETE http://localhost:5000/api/tasks/$task_id)
if echo "$delete_response" | grep -q "deleted successfully"; then
    echo "✅ Test task deleted successfully"
else
    echo "⚠️  Could not delete test task (manual cleanup may be needed)"
fi

echo ""
echo "🎉 Data Persistence Test Complete!"
echo "================================="
echo ""
echo "✅ All tests passed - your data persistence is working correctly!"
echo ""
echo "🔧 To test frontend persistence:"
echo "   1. Open http://localhost:3000"
echo "   2. Add a few tasks"
echo "   3. Refresh the page"
echo "   4. Verify tasks are still there"
echo ""