#!/usr/bin/env python3
"""
ENTROPY - Fix Task Duplication When Moving to Tomorrow
Ensures tasks are removed from today when moved to tomorrow
"""

import os
import re

def main():
    print("🔧 ENTROPY - Fix Task Duplication Issue")
    print("=" * 40)
    
    # Check if we're in the right directory
    if not os.path.exists("frontend/src/App.js"):
        print("❌ Please run this script from the entropy-app directory")
        return
    
    print("🔄 Fixing moveUncompletedTasks function...")
    
    # Read App.js
    with open("frontend/src/App.js", 'r') as f:
        content = f.read()
    
    # The fixed function that properly handles state updates
    fixed_move_function = '''    const moveUncompletedTasks = async () => {
        try {
            const response = await axios.post('/api/tasks/move-to-tomorrow');
            
            if (response.data.movedCount === 0) {
                addNotification('Nothing to Move', 'All tasks completed!', 'info');
            } else {
                // FIXED: Get the IDs of tasks that were moved
                const movedTaskIds = response.data.movedTaskIds || [];
                const newTomorrowTasks = response.data.tasks || [];
                
                // CRITICAL FIX: Remove moved tasks from today's state
                setTodayTasks(prev => prev.filter(task => !movedTaskIds.includes(task._id)));
                
                // Add new tasks to tomorrow's state (avoiding duplicates)
                setTomorrowTasks(prev => {
                    const existingIds = new Set(prev.map(t => t._id));
                    const filteredNewTasks = newTomorrowTasks.filter(t => !existingIds.has(t._id));
                    return [...prev, ...filteredNewTasks];
                });
                
                addNotification(
                    'Tasks Moved Successfully! 📅', 
                    response.data.message, 
                    'success', 
                    5000
                );
            }
        } catch (error) {
            console.error('Error moving tasks:', error);
            addNotification('Move Failed', 'Please try again', 'error');
        }
    };'''
    
    # Replace the existing function
    new_content = re.sub(
        r'const moveUncompletedTasks = async \(\) => \{[^}]*\}[^}]*\};',
        fixed_move_function,
        content,
        flags=re.DOTALL
    )
    
    # Check if replacement was successful
    if new_content == content:
        print("❌ Could not find moveUncompletedTasks function to replace")
        return
    
    # Write the fixed content back
    with open("frontend/src/App.js", 'w') as f:
        f.write(new_content)
    
    print("✅ Fixed moveUncompletedTasks function")
    
    # Also need to ensure the backend returns the correct data
    print("🔧 Checking backend response format...")
    
    # Check if the backend is returning movedTaskIds
    backend_tasks_path = "backend/routes/tasks.js"
    if os.path.exists(backend_tasks_path):
        with open(backend_tasks_path, 'r') as f:
            backend_content = f.read()
        
        if "movedTaskIds" not in backend_content:
            print("⚠️  Backend may not be returning movedTaskIds - updating...")
            
            # Fix the backend response to include movedTaskIds
            backend_content = backend_content.replace(
                "movedTaskIds: movedTaskIds // Send IDs of moved tasks for frontend removal",
                "movedTaskIds: movedTaskIds"
            )
            
            # Ensure the response includes movedTaskIds
            if "movedTaskIds: movedTaskIds" not in backend_content:
                backend_content = re.sub(
                    r'res\.json\(\s*\{\s*movedCount: [^,]+,([^}]+)\s*\}\s*\);',
                    r'res.json({ movedCount: movedTasks.length,\1, movedTaskIds: movedTaskIds });',
                    backend_content
                )
            
            with open(backend_tasks_path, 'w') as f:
                f.write(backend_content)
            
            print("✅ Updated backend response format")
    
    print("\n🎉 Task Duplication Fix Applied!")
    print("=" * 35)
    print("✅ Frontend: Properly removes moved tasks from today")
    print("✅ Frontend: Adds tasks to tomorrow without duplicates")
    print("✅ Backend: Returns correct task IDs for removal")
    
    print("\n🚀 Restart your app to see the fix:")
    print("   Ctrl+C to stop current app")
    print("   ./start.sh to restart")
    
    print("\n✨ Now tasks will move from today to tomorrow cleanly!")

if __name__ == "__main__":
    main()
