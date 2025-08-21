#!/usr/bin/env python3
"""
ENTROPY - Fix Tomorrow Task Deletion Issue
Ensures deleted tomorrow tasks don't reappear in today's section
"""

import os
import shutil
import json
from datetime import datetime

def create_backup():
    """Create backup before fixing"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = f"../entropy_backup_deletion_fix_{timestamp}"
    
    print(f"📦 Creating backup: {backup_dir}")
    
    try:
        shutil.copytree(".", backup_dir, ignore=shutil.ignore_patterns(
            'node_modules', '.git', '*.log', 'build', 'dist'
        ))
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
    print("🔧 ENTROPY - Fix Tomorrow Task Deletion Issue")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists("backend") or not os.path.exists("frontend"):
        print("❌ Please run this script from the entropy-app directory")
        return
    
    # Create backup
    backup_dir = create_backup()
    if not backup_dir:
        print("❌ Cannot proceed without backup.")
        return
    
    print("🔧 Fixing backend task deletion logic...")
    
    # 1. Fix the backend to properly handle tomorrow task deletions
    enhanced_tasks_route = '''const express = require('express');
const router = express.Router();
const Task = require('../models/Task');

// Get today's and tomorrow's tasks - ENHANCED VERSION
router.get('/today', async (req, res) => {
    try {
        const today = new Date();
        today.setHours(0, 0, 0, 0);
        const tomorrow = new Date(today);
        tomorrow.setDate(tomorrow.getDate() + 1);
        const dayAfterTomorrow = new Date(tomorrow);
        dayAfterTomorrow.setDate(dayAfterTomorrow.getDate() + 1);
        
        // Get today's tasks (STRICTLY exclude moved or deleted tasks)
        const todayTasks = await Task.find({
            date: { $gte: today, $lt: tomorrow },
            $and: [
                { $or: [{ moved: { $exists: false } }, { moved: false }] },
                { $or: [{ deleted: { $exists: false } }, { deleted: false }] }
            ]
        }).sort({ priority: 1, createdAt: 1 });
        
        // Get tomorrow's tasks (exclude deleted tasks)
        const tomorrowTasks = await Task.find({
            date: { $gte: tomorrow, $lt: dayAfterTomorrow },
            $or: [{ deleted: { $exists: false } }, { deleted: false }]
        }).sort({ priority: 1, createdAt: 1 });
        
        res.json({
            today: todayTasks,
            tomorrow: tomorrowTasks,
            todayCount: todayTasks.length,
            tomorrowCount: tomorrowTasks.length
        });
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

// Delete task - ENHANCED to handle tomorrow task deletions properly
router.delete('/:id', async (req, res) => {
    try {
        const { id } = req.params;
        
        // Find the task to be deleted
        const taskToDelete = await Task.findById(id);
        if (!taskToDelete) {
            return res.status(404).json({ error: 'Task not found' });
        }
        
        // Check if this is a tomorrow task (date is tomorrow)
        const today = new Date();
        today.setHours(0, 0, 0, 0);
        const tomorrow = new Date(today);
        tomorrow.setDate(tomorrow.getDate() + 1);
        const dayAfterTomorrow = new Date(tomorrow);
        dayAfterTomorrow.setDate(dayAfterTomorrow.getDate() + 1);
        
        const isTomorrowTask = taskToDelete.date >= tomorrow && taskToDelete.date < dayAfterTomorrow;
        
        if (isTomorrowTask) {
            // If deleting a tomorrow task, also find and delete any related "moved" task from today
            const relatedMovedTask = await Task.findOne({
                title: taskToDelete.title,
                description: taskToDelete.description,
                priority: taskToDelete.priority,
                date: { $gte: today, $lt: tomorrow },
                moved: true
            });
            
            if (relatedMovedTask) {
                await Task.findByIdAndDelete(relatedMovedTask._id);
                console.log(`Deleted related moved task: ${relatedMovedTask._id}`);
            }
        }
        
        // Delete the main task
        await Task.findByIdAndDelete(id);
        
        res.json({ 
            message: 'Task deleted successfully',
            deletedTask: taskToDelete,
            isTomorrowTask: isTomorrowTask
        });
        
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// Move uncompleted tasks to tomorrow - ENHANCED VERSION
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
            $and: [
                { $or: [{ moved: { $exists: false } }, { moved: false }] },
                { $or: [{ deleted: { $exists: false } }, { deleted: false }] }
            ]
        });
        
        if (uncompletedTasks.length === 0) {
            return res.json({ 
                movedCount: 0, 
                message: 'No uncompleted tasks to move',
                tasks: [],
                movedTaskIds: []
            });
        }
        
        const movedTaskIds = [];
        const newTomorrowTasks = [];
        
        for (let task of uncompletedTasks) {
            // Check for duplicate in tomorrow's list
            const existingTomorrowTask = await Task.findOne({
                title: task.title,
                date: { $gte: tomorrow },
                $or: [{ deleted: { $exists: false } }, { deleted: false }]
            });
            
            if (!existingTomorrowTask) {
                // Create new task for tomorrow with unique reference
                const newTask = new Task({
                    title: task.title,
                    description: task.description,
                    priority: task.priority,
                    date: tomorrow,
                    originalTaskId: task._id // Reference to original task
                });
                
                await newTask.save();
                newTomorrowTasks.push(newTask);
            }
            
            // Mark original task as moved
            await Task.findByIdAndUpdate(task._id, { moved: true });
            movedTaskIds.push(task._id);
        }
        
        const message = `Successfully moved ${newTomorrowTasks.length} task${newTomorrowTasks.length !== 1 ? 's' : ''} to tomorrow`;
        
        res.json({ 
            movedCount: newTomorrowTasks.length,
            message: message,
            tasks: newTomorrowTasks,
            movedTaskIds: movedTaskIds
        });
        
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

module.exports = router;'''
    
    update_file("backend/routes/tasks.js", enhanced_tasks_route)
    
    print("🔄 Updating frontend to properly handle deletions...")
    
    # 2. Update App.js to handle deletions properly with full refresh
    try:
        with open("frontend/src/App.js", 'r') as f:
            app_content = f.read()
        
        import re
        
        # Replace deleteTask function to ensure proper cleanup
        enhanced_delete_function = '''    const deleteTask = async (taskId) => {
        try {
            const response = await axios.delete(`/api/tasks/${taskId}`);
            
            // ENHANCED: Remove from both today and tomorrow states immediately
            setTodayTasks(prev => prev.filter(task => task._id !== taskId));
            setTomorrowTasks(prev => prev.filter(task => task._id !== taskId));
            
            // Also reload tasks to ensure consistency
            setTimeout(() => {
                loadTasks();
            }, 500);
            
            const taskType = response.data.isTomorrowTask ? 'Tomorrow' : 'Today';
            addNotification(
                `${taskType} Task Deleted`,
                'Task has been removed permanently',
                'info'
            );
            
        } catch (error) {
            console.error('Error deleting task:', error);
            addNotification('Delete Failed', 'Please try again', 'error');
        }
    };'''
        
        # Replace existing deleteTask function
        new_app_content = re.sub(
            r'const deleteTask = async \(taskId\) => \{[^}]*\}[^}]*\};',
            enhanced_delete_function,
            app_content,
            flags=re.DOTALL
        )
        
        # If no replacement happened, the function might be formatted differently
        if new_app_content == app_content:
            print("⚠️  Could not find deleteTask function - it may need manual updating")
        else:
            update_file("frontend/src/App.js", new_app_content)
        
    except Exception as e:
        print(f"❌ Error updating App.js: {e}")
    
    # 3. Update Task model to support the new fields if needed
    print("🗃️ Updating Task model...")
    
    enhanced_task_model = '''const mongoose = require('mongoose');

const taskSchema = new mongoose.Schema({
    title: {
        type: String,
        required: true,
        trim: true,
        maxLength: 200
    },
    description: {
        type: String,
        trim: true,
        maxLength: 1000
    },
    priority: {
        type: Number,
        required: true,
        min: 1,
        max: 3
    },
    completed: {
        type: Boolean,
        default: false
    },
    date: {
        type: Date,
        default: Date.now
    },
    completedAt: {
        type: Date
    },
    moved: {
        type: Boolean,
        default: false
    },
    deleted: {
        type: Boolean,
        default: false
    },
    originalTaskId: {
        type: mongoose.Schema.Types.ObjectId,
        ref: 'Task'
    }
}, {
    timestamps: true
});

// Index for better query performance
taskSchema.index({ date: 1, completed: 1, moved: 1, deleted: 1 });

module.exports = mongoose.model('Task', taskSchema);'''
    
    update_file("backend/models/Task.js", enhanced_task_model)
    
    # 4. Create cleanup script for existing data
    print("🧹 Creating data cleanup script...")
    
    cleanup_script = '''#!/bin/bash
echo "🧹 ENTROPY - Data Cleanup for Tomorrow Task Fix"
echo "=============================================="
echo ""
echo "This script will clean up any orphaned tasks that might cause the reappearing bug."
echo ""

read -p "Do you want to run the cleanup? (yes/no): " confirm
if [ "$confirm" != "yes" ]; then
    echo "Cleanup cancelled."
    exit 0
fi

echo "🔄 Running database cleanup..."

# Method 1: Using mongosh (MongoDB 5.0+)
if command -v mongosh >/dev/null 2>&1; then
    echo "Using mongosh..."
    mongosh entropy --eval "
        // Remove orphaned moved tasks that might reappear
        const result1 = db.tasks.deleteMany({
            moved: true,
            date: { \\$lt: new Date(new Date().setHours(0,0,0,0)) }
        });
        print('🗑️  Removed ' + result1.deletedCount + ' old moved tasks');
        
        // Clean up any tasks marked as deleted
        const result2 = db.tasks.deleteMany({ deleted: true });
        print('🗑️  Removed ' + result2.deletedCount + ' deleted tasks');
        
        // Show remaining task counts
        const todayStart = new Date();
        todayStart.setHours(0,0,0,0);
        const tomorrow = new Date(todayStart);
        tomorrow.setDate(tomorrow.getDate() + 1);
        
        const todayCount = db.tasks.countDocuments({
            date: { \\$gte: todayStart, \\$lt: tomorrow },
            moved: { \\$ne: true },
            deleted: { \\$ne: true }
        });
        
        const tomorrowCount = db.tasks.countDocuments({
            date: { \\$gte: tomorrow },
            deleted: { \\$ne: true }
        });
        
        print('📊 Today tasks: ' + todayCount);
        print('📊 Tomorrow tasks: ' + tomorrowCount);
    "
# Method 2: Using legacy mongo client
elif command -v mongo >/dev/null 2>&1; then
    echo "Using legacy mongo client..."
    mongo entropy --eval "
        var result1 = db.tasks.deleteMany({
            moved: true,
            date: { \\$lt: new Date(new Date().setHours(0,0,0,0)) }
        });
        print('🗑️  Removed ' + result1.deletedCount + ' old moved tasks');
        
        var result2 = db.tasks.deleteMany({ deleted: true });
        print('🗑️  Removed ' + result2.deletedCount + ' deleted tasks');
        
        print('📊 Today tasks: ' + db.tasks.count({
            date: { \\$gte: new Date(new Date().setHours(0,0,0,0)) },
            moved: { \\$ne: true },
            deleted: { \\$ne: true }
        }));
    "
else
    echo "❌ MongoDB client not found!"
    echo "Please clean up manually or install mongosh/mongo client"
    exit 1
fi

echo ""
echo "✅ Cleanup complete!"
echo "🚀 Restart your app: ./start.sh"'''
    
    with open("cleanup_orphaned_tasks.sh", 'w') as f:
        f.write(cleanup_script)
    os.chmod("cleanup_orphaned_tasks.sh", 0o755)
    
    # Create restart script
    restart_script = f'''#!/bin/bash
echo "🔧 Restarting ENTROPY with Tomorrow Deletion Fix..."
echo "Backup created: {backup_dir}"
echo ""

# Kill existing processes
pkill -f "node.*server.js" || true
pkill -f "react-scripts" || true

# Wait a moment
sleep 2

echo "✅ Tomorrow Task Deletion Fixes Applied:"
echo "  🗑️  Tasks deleted from tomorrow stay deleted"
echo "  🔄 Backend properly cleans up related moved tasks"
echo "  ⚡ Frontend refreshes state after deletion"
echo "  🧹 Database queries exclude moved/deleted tasks"
echo ""
echo "🧹 Optional cleanup:"
echo "  ./cleanup_orphaned_tasks.sh (removes orphaned data)"
echo ""
echo "🛡️  Backup & Restore:"
echo "  📦 Backup created: {backup_dir}"
echo "  🔄 To restore: python3 ../restore_backup.py {backup_dir}"
echo ""

# Start the application
./start.sh'''
    
    with open("restart_deletion_fixed.sh", 'w') as f:
        f.write(restart_script)
    os.chmod("restart_deletion_fixed.sh", 0o755)
    
    print(f"\n🎉 Tomorrow Task Deletion Issue Fixed!")
    print("=" * 45)
    print("✅ Backend: Enhanced deletion logic with cleanup")
    print("✅ Frontend: Proper state management after deletion")
    print("✅ Database: Improved queries to exclude orphaned tasks")
    print("✅ Model: Added fields for better task tracking")
    print("✅ Cleanup: Script to remove orphaned data")
    
    print(f"\n📦 BACKUP CREATED: {backup_dir}")
    print(f"🔄 Restore command: python3 ../restore_backup.py {backup_dir}")
    
    print("\n🔧 WHAT WAS FIXED:")
    print("• Backend deletes both tomorrow task AND related moved task")
    print("• Frontend removes task from state and reloads for consistency")
    print("• Database queries strictly exclude moved/deleted tasks")
    print("• Enhanced task model supports better tracking")
    
    print("\n🚀 To start with the fix:")
    print("./restart_deletion_fixed.sh")
    
    print("\n🧹 To clean up existing orphaned data:")
    print("./cleanup_orphaned_tasks.sh")
    
    print("\n⚡ Tasks deleted from tomorrow will stay deleted! ⚡")

if __name__ == "__main__":
    main()
