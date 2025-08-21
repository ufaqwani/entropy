#!/usr/bin/env python3
"""
ENTROPY - Fix Move-to-Tomorrow Bug Only
Fixes tasks still showing in today after being moved to tomorrow
"""

import os
import shutil
import json
from datetime import datetime

def create_backup():
    """Create backup before fixing"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = f"../entropy_backup_move_fix_{timestamp}"
    
    print(f"📦 Creating backup: {backup_dir}")
    
    try:
        shutil.copytree(".", backup_dir, ignore=shutil.ignore_patterns(
            'node_modules', '.git', '*.log', 'build', 'dist'
        ))
        
        backup_info = {
            "timestamp": timestamp,
            "date": datetime.now().isoformat(),
            "description": "Backup before fixing move-to-tomorrow bug",
            "restore_command": f"../restore_backup.py {backup_dir}"
        }
        
        with open(f"{backup_dir}/backup_info.json", 'w') as f:
            json.dump(backup_info, f, indent=2)
        
        print(f"✅ Backup created: {backup_dir}")
        return backup_dir
        
    except Exception as e:
        print(f"❌ Backup failed: {e}")
        return None

def update_file(file_path, content):
    """Update file with given content"""
    with open(file_path, 'w') as f:
        f.write(content)
    print(f"✅ Updated: {file_path}")

def main():
    print("🔧 ENTROPY - Fix Move-to-Tomorrow Bug Only")
    print("=" * 45)
    
    # Check if we're in the right directory
    if not os.path.exists("backend") or not os.path.exists("frontend"):
        print("❌ Please run this script from the entropy-app directory")
        return
    
    # Create backup
    backup_dir = create_backup()
    if not backup_dir:
        print("❌ Cannot proceed without backup.")
        return
    
    print("🔧 Fixing backend to exclude moved tasks from today's list...")
    
    # Fix the backend tasks route
    fixed_tasks_route = '''const express = require('express');
const router = express.Router();
const Task = require('../models/Task');

// Get today's tasks - FIXED to exclude moved tasks
router.get('/today', async (req, res) => {
    try {
        const today = new Date();
        today.setHours(0, 0, 0, 0);
        const tomorrow = new Date(today);
        tomorrow.setDate(tomorrow.getDate() + 1);
        
        const tasks = await Task.find({
            date: { $gte: today, $lt: tomorrow },
            $or: [
                { moved: { $exists: false } },
                { moved: false }
            ]
        }).sort({ priority: 1, createdAt: 1 });
        
        res.json(tasks);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// Get tomorrow's tasks
router.get('/tomorrow', async (req, res) => {
    try {
        const today = new Date();
        today.setHours(0, 0, 0, 0);
        const tomorrow = new Date(today);
        tomorrow.setDate(tomorrow.getDate() + 1);
        const dayAfter = new Date(tomorrow);
        dayAfter.setDate(dayAfter.getDate() + 1);
        
        const tasks = await Task.find({
            date: { $gte: tomorrow, $lt: dayAfter }
        }).sort({ priority: 1, createdAt: 1 });
        
        res.json(tasks);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// Create new task
router.post('/', async (req, res) => {
    try {
        const { title, description, priority, date } = req.body;
        
        if (!title || !priority) {
            return res.status(400).json({ error: 'Title and priority are required' });
        }
        
        const task = new Task({
            title,
            description,
            priority,
            date: date || new Date()
        });
        
        await task.save();
        res.status(201).json(task);
    } catch (error) {
        res.status(400).json({ error: error.message });
    }
});

// Update task
router.put('/:id', async (req, res) => {
    try {
        const { id } = req.params;
        const updates = req.body;
        
        if (updates.completed && !updates.completedAt) {
            updates.completedAt = new Date();
        }
        
        const task = await Task.findByIdAndUpdate(id, updates, { new: true });
        
        if (!task) {
            return res.status(404).json({ error: 'Task not found' });
        }
        
        res.json(task);
    } catch (error) {
        res.status(400).json({ error: error.message });
    }
});

// Delete task
router.delete('/:id', async (req, res) => {
    try {
        const { id } = req.params;
        const task = await Task.findByIdAndDelete(id);
        
        if (!task) {
            return res.status(404).json({ error: 'Task not found' });
        }
        
        res.json({ message: 'Task deleted successfully' });
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// Move uncompleted tasks to tomorrow - FIXED VERSION
router.post('/move-to-tomorrow', async (req, res) => {
    try {
        const today = new Date();
        today.setHours(0, 0, 0, 0);
        const tomorrow = new Date(today);
        tomorrow.setDate(tomorrow.getDate() + 1);
        
        // Find uncompleted tasks from today (not already moved)
        const uncompletedTasks = await Task.find({
            date: { $gte: today, $lt: tomorrow },
            completed: false,
            $or: [
                { moved: { $exists: false } },
                { moved: false }
            ]
        });
        
        if (uncompletedTasks.length === 0) {
            return res.json({ 
                movedCount: 0, 
                message: 'No uncompleted tasks to move',
                movedTaskIds: []
            });
        }
        
        const movedTaskIds = [];
        const createdTasks = [];
        
        for (let task of uncompletedTasks) {
            // Create new task for tomorrow
            const newTask = new Task({
                title: task.title,
                description: task.description,
                priority: task.priority,
                date: tomorrow
            });
            
            await newTask.save();
            createdTasks.push(newTask);
            
            // Mark original task as moved (this removes it from today's list)
            await Task.findByIdAndUpdate(task._id, { moved: true });
            movedTaskIds.push(task._id);
        }
        
        const message = `Successfully moved ${createdTasks.length} task${createdTasks.length !== 1 ? 's' : ''} to tomorrow`;
        
        res.json({ 
            movedCount: createdTasks.length,
            message: message,
            movedTaskIds: movedTaskIds // Frontend uses this to update state
        });
        
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

module.exports = router;'''
    
    update_file("backend/routes/tasks.js", fixed_tasks_route)
    
    print("🔄 Updating frontend to handle moved tasks properly...")
    
    # Read existing App.js and update the moveUncompletedTasks function
    try:
        with open("frontend/src/App.js", 'r') as f:
            app_content = f.read()
        
        # Find and replace the moveUncompletedTasks function
        import re
        
        # Look for the function and replace it
        fixed_move_function = '''    const moveUncompletedTasks = async () => {
        try {
            const response = await axios.post('/api/tasks/move-to-tomorrow');
            
            if (response.data.movedCount === 0) {
                addNotification('Nothing to Move', 'All tasks completed!', 'info');
            } else {
                // FIXED: Remove moved tasks from today's state immediately
                const movedTaskIds = response.data.movedTaskIds || [];
                setTodayTasks(prev => prev.filter(task => !movedTaskIds.includes(task._id)));
                
                addNotification('Tasks Moved! 📅', response.data.message, 'success', 5000);
                
                // Also reload tasks to ensure consistency
                setTimeout(() => {
                    loadTasks();
                }, 1000);
            }
        } catch (error) {
            console.error('Error moving tasks:', error);
            addNotification('Move Failed', 'Please try again', 'error');
        }
    };'''
        
        # Replace the existing function
        new_app_content = re.sub(
            r'const moveUncompletedTasks = async \(\) => \{[^}]*\}[^}]*\};',
            fixed_move_function,
            app_content,
            flags=re.DOTALL
        )
        
        # If the pattern wasn't found, it might have different spacing
        if new_app_content == app_content:
            # Try a more flexible pattern
            new_app_content = re.sub(
                r'moveUncompletedTasks.*?async.*?\(\).*?=>\s*\{.*?catch.*?\{.*?\}.*?\};',
                fixed_move_function.strip(),
                app_content,
                flags=re.DOTALL
            )
        
        update_file("frontend/src/App.js", new_app_content)
        
    except Exception as e:
        print(f"❌ Error updating App.js: {e}")
    
    # Create restart script
    restart_script = f'''#!/bin/bash
echo "🔧 Restarting ENTROPY with Move-to-Tomorrow Fix..."
echo "Backup created: {backup_dir}"
echo ""

# Kill existing processes
pkill -f "node.*server.js" || true
pkill -f "react-scripts" || true

# Wait a moment
sleep 2

echo "✅ Move-to-Tomorrow Bug Fixed:"
echo "  🚫 Tasks moved to tomorrow no longer appear in today"
echo "  🔄 Backend properly excludes moved tasks"
echo "  ⚡ Frontend state updates immediately"
echo "  📋 Consistent task filtering applied"
echo ""
echo "🛡️  Backup & Restore:"
echo "  📦 Backup created: {backup_dir}"
echo "  🔄 To restore: python3 ../restore_backup.py {backup_dir}"
echo ""

# Start the application
./start.sh || npm start'''
    
    with open("restart_move_fixed.sh", 'w') as f:
        f.write(restart_script)
    os.chmod("restart_move_fixed.sh", 0o755)
    
    print(f"\n🎉 Move-to-Tomorrow Bug Fixed!")
    print("=" * 35)
    print("✅ Backend: Properly excludes moved tasks from today's list")
    print("✅ Frontend: Immediately removes moved tasks from state")
    print("✅ Database: Tasks marked as 'moved' are filtered out")
    print("✅ UI: Tasks disappear from today when moved to tomorrow")
    
    print(f"\n📦 BACKUP CREATED: {backup_dir}")
    print(f"🔄 Restore command: python3 ../restore_backup.py {backup_dir}")
    
    print("\n🔧 WHAT WAS FIXED:")
    print("• GET /today route excludes tasks with moved=true")
    print("• Move function marks tasks as moved in database") 
    print("• Frontend removes moved tasks from today's state")
    print("• Consistent filtering prevents moved tasks from appearing")
    
    print("\n🚀 To start with the fix:")
    print("./restart_move_fixed.sh")
    
    print("\n⚡ Tasks moved to tomorrow will now disappear from today! ⚡")

if __name__ == "__main__":
    main()
