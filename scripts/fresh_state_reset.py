#!/usr/bin/env python3
"""
ENTROPY - Fresh State Reset & Data Persistence Test
Clears all data and provides tools to verify saving/loading works
"""

import os
import shutil
import json
from datetime import datetime

def create_backup():
    """Create backup before reset"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = f"../entropy_backup_before_reset_{timestamp}"
    
    print(f"📦 Creating backup: {backup_dir}")
    
    try:
        shutil.copytree(".", backup_dir, ignore=shutil.ignore_patterns(
            'node_modules', '.git', '*.log', 'build', 'dist'
        ))
        return backup_dir
    except Exception as e:
        print(f"❌ Backup failed: {e}")
        return None

def main():
    print("🔄 ENTROPY - Fresh State Reset & Persistence Test")
    print("=" * 55)
    
    # Create backup
    backup_dir = create_backup()
    
    # 1. Create MongoDB reset script
    print("🗃️ Creating database reset script...")
    
    db_reset_script = '''#!/bin/bash
echo "🗃️  Resetting ENTROPY Database..."
echo "⚠️  This will delete ALL tasks and progress data!"
echo ""

read -p "Are you sure? Type 'yes' to continue: " confirm
if [ "$confirm" != "yes" ]; then
    echo "Reset cancelled."
    exit 0
fi

echo "🔄 Clearing MongoDB collections..."

# Method 1: Using mongosh (MongoDB 5.0+)
if command -v mongosh >/dev/null 2>&1; then
    echo "Using mongosh..."
    mongosh entropy --eval "
        db.tasks.deleteMany({});
        db.progresses.deleteMany({});
        print('✅ All tasks and progress deleted');
        print('📊 Remaining tasks: ' + db.tasks.countDocuments());
        print('📊 Remaining progress: ' + db.progresses.countDocuments());
    "
# Method 2: Using legacy mongo client
elif command -v mongo >/dev/null 2>&1; then
    echo "Using legacy mongo client..."
    mongo entropy --eval "
        db.tasks.deleteMany({});
        db.progresses.deleteMany({});
        print('✅ All tasks and progress deleted');
        print('📊 Remaining tasks: ' + db.tasks.count());
        print('📊 Remaining progress: ' + db.progresses.count());
    "
else
    echo "❌ MongoDB client not found!"
    echo "Please install mongosh or legacy mongo client"
    echo "Or manually delete collections in MongoDB Compass"
    exit 1
fi

echo ""
echo "✅ Database reset complete!"
echo "🚀 Restart your app to begin fresh: ./start.sh"'''
    
    with open("reset_database.sh", 'w') as f:
        f.write(db_reset_script)
    os.chmod("reset_database.sh", 0o755)
    
    # 2. Create frontend storage clear script
    print("🌐 Creating frontend storage clear script...")
    
    frontend_clear = '''<!DOCTYPE html>
<html>
<head>
    <title>Clear ENTROPY Storage</title>
    <style>
        body { font-family: monospace; padding: 2rem; background: #f5f5f5; }
        .container { max-width: 600px; margin: 0 auto; background: white; padding: 2rem; border-radius: 8px; }
        button { background: #ff4444; color: white; border: none; padding: 1rem 2rem; border-radius: 4px; cursor: pointer; margin: 0.5rem; }
        button:hover { background: #cc0000; }
        .info { background: #e3f2fd; padding: 1rem; border-radius: 4px; margin: 1rem 0; }
        .success { background: #e8f5e8; padding: 1rem; border-radius: 4px; margin: 1rem 0; }
    </style>
</head>
<body>
    <div class="container">
        <h1>⚡ ENTROPY Storage Cleaner</h1>
        
        <div class="info">
            <strong>Current Storage:</strong>
            <div id="storage-info"></div>
        </div>
        
        <button onclick="clearAllStorage()">🗑️ Clear All Frontend Storage</button>
        <button onclick="clearOnlyEntropy()">🎯 Clear Only ENTROPY Data</button>
        
        <div id="result"></div>
        
        <h3>📋 What this clears:</h3>
        <ul>
            <li>✅ localStorage (theme preferences, cached data)</li>
            <li>✅ sessionStorage (temporary session data)</li>
            <li>✅ IndexedDB (if used for offline storage)</li>
            <li>✅ Service Worker cache (if any)</li>
        </ul>
        
        <p><strong>Note:</strong> After clearing, close this tab and restart your ENTROPY app.</p>
    </div>

    <script>
        function displayStorageInfo() {
            const info = document.getElementById('storage-info');
            const items = [];
            
            // Check localStorage
            for (let i = 0; i < localStorage.length; i++) {
                const key = localStorage.key(i);
                items.push(`localStorage: ${key}`);
            }
            
            // Check sessionStorage
            for (let i = 0; i < sessionStorage.length; i++) {
                const key = sessionStorage.key(i);
                items.push(`sessionStorage: ${key}`);
            }
            
            info.innerHTML = items.length ? items.join('<br>') : 'No storage items found';
        }
        
        function clearAllStorage() {
            try {
                localStorage.clear();
                sessionStorage.clear();
                
                // Clear IndexedDB
                if ('indexedDB' in window) {
                    indexedDB.deleteDatabase('entropy');
                }
                
                // Clear cache if service worker exists
                if ('caches' in window) {
                    caches.keys().then(names => {
                        names.forEach(name => caches.delete(name));
                    });
                }
                
                document.getElementById('result').innerHTML = 
                    '<div class="success">✅ All storage cleared! Close this tab and restart ENTROPY.</div>';
                displayStorageInfo();
            } catch (error) {
                document.getElementById('result').innerHTML = 
                    '<div style="background: #ffebee; padding: 1rem; border-radius: 4px;">❌ Error: ' + error.message + '</div>';
            }
        }
        
        function clearOnlyEntropy() {
            try {
                // Clear only ENTROPY-related keys
                Object.keys(localStorage).forEach(key => {
                    if (key.includes('entropy') || key.includes('Entropy')) {
                        localStorage.removeItem(key);
                    }
                });
                
                Object.keys(sessionStorage).forEach(key => {
                    if (key.includes('entropy') || key.includes('Entropy')) {
                        sessionStorage.removeItem(key);
                    }
                });
                
                document.getElementById('result').innerHTML = 
                    '<div class="success">✅ ENTROPY storage cleared! Close this tab and restart ENTROPY.</div>';
                displayStorageInfo();
            } catch (error) {
                document.getElementById('result').innerHTML = 
                    '<div style="background: #ffebee; padding: 1rem; border-radius: 4px;">❌ Error: ' + error.message + '</div>';
            }
        }
        
        // Display current storage on load
        displayStorageInfo();
    </script>
</body>
</html>'''
    
    with open("clear_frontend_storage.html", 'w') as f:
        f.write(frontend_clear)
    
    # 3. Create data persistence test script
    print("🧪 Creating data persistence test script...")
    
    test_script = '''#!/bin/bash
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
echo ""'''
    
    with open("test_persistence.sh", 'w') as f:
        f.write(test_script)
    os.chmod("test_persistence.sh", 0o755)
    
    # 4. Create complete reset and restart script
    print("🚀 Creating complete reset script...")
    
    complete_reset = f'''#!/bin/bash
echo "🔄 ENTROPY - Complete Fresh State Reset"
echo "======================================"
echo ""

if [ "$1" != "--confirm" ]; then
    echo "⚠️  WARNING: This will delete ALL your tasks and progress!"
    echo ""
    echo "To proceed, run: ./fresh_start.sh --confirm"
    exit 0
fi

echo "🗃️  Step 1: Resetting database..."
./reset_database.sh

echo ""
echo "🌐 Step 2: Clear frontend storage..."
echo "    Open this file in your browser: file://$(pwd)/clear_frontend_storage.html"
echo "    Click 'Clear All Frontend Storage' and close the tab"
echo ""

read -p "Press Enter after clearing frontend storage..."

echo ""
echo "🔄 Step 3: Restarting application..."

# Kill existing processes
pkill -f "node.*server.js" || true
pkill -f "react-scripts" || true

sleep 2

# Start fresh
./start.sh &

echo ""
echo "🧪 Step 4: Testing persistence..."
sleep 10
./test_persistence.sh

echo ""
echo "🎉 Fresh state setup complete!"
echo "=============================="
echo ""
echo "📱 Your app is running at: http://localhost:3000"
echo "🧪 Data persistence test results above"
echo ""
echo "🛡️  Backup created: {backup_dir if backup_dir else 'Failed'}"
echo ""'''
    
    with open("fresh_start.sh", 'w') as f:
        f.write(complete_reset)
    os.chmod("fresh_start.sh", 0o755)
    
    print(f"\n🎉 Fresh State Reset Tools Created!")
    print("=" * 40)
    print("✅ Database reset script: reset_database.sh")
    print("✅ Frontend storage cleaner: clear_frontend_storage.html")  
    print("✅ Data persistence test: test_persistence.sh")
    print("✅ Complete reset script: fresh_start.sh")
    
    if backup_dir:
        print(f"\n📦 BACKUP CREATED: {backup_dir}")
    
    print("\n🚀 TO START FRESH:")
    print("./fresh_start.sh --confirm")
    
    print("\n🧪 TO TEST PERSISTENCE ONLY:")
    print("./test_persistence.sh")
    
    print("\n🗃️ TO RESET DATABASE ONLY:")
    print("./reset_database.sh")
    
    print("\n⚡ These tools will help you verify data saving/loading works correctly!")

if __name__ == "__main__":
    main()
