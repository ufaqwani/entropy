#!/usr/bin/env python3
"""
ENTROPY - Fix Move to Tomorrow (Tasks Disappearing Issue)
Ensures moved tasks appear in tomorrow's section instead of disappearing
"""

import os
import shutil
import json
from datetime import datetime

def create_backup():
    """Create backup before fixing"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = f"../entropy_backup_move_disappear_fix_{timestamp}"
    
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
    print("🔧 ENTROPY - Fix Move to Tomorrow (Tasks Disappearing)")
    print("=" * 55)
    
    # Check if we're in the right directory
    if not os.path.exists("backend") or not os.path.exists("frontend"):
        print("❌ Please run this script from the entropy-app directory")
        return
    
    # Create backup
    backup_dir = create_backup()
    if not backup_dir:
        print("❌ Cannot proceed without backup.")
        return
    
    print("🔧 Fixing backend to properly handle tomorrow tasks...")
    
    # 1. Fix backend tasks route to handle both today and tomorrow
    fixed_tasks_route = '''const express = require('express');
const router = express.Router();
const Task = require('../models/Task');

// Get today's and tomorrow's tasks - FIXED VERSION
router.get('/today', async (req, res) => {
    try {
        const today = new Date();
        today.setHours(0, 0, 0, 0);
        const tomorrow = new Date(today);
        tomorrow.setDate(tomorrow.getDate() + 1);
        const dayAfterTomorrow = new Date(tomorrow);
        dayAfterTomorrow.setDate(dayAfterTomorrow.getDate() + 1);
        
        // Get today's tasks (exclude moved tasks)
        const todayTasks = await Task.find({
            date: { $gte: today, $lt: tomorrow },
            $or: [
                { moved: { $exists: false } },
                { moved: false }
            ]
        }).sort({ priority: 1, createdAt: 1 });
        
        // Get tomorrow's tasks
        const tomorrowTasks = await Task.find({
            date: { $gte: tomorrow, $lt: dayAfterTomorrow }
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

// Move uncompleted tasks to tomorrow - FIXED to show tasks in tomorrow
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
                tasks: [],
                movedTaskIds: []
            });
        }
        
        const movedTaskIds = [];
        const newTomorrowTasks = [];
        
        for (let task of uncompletedTasks) {
            // Create NEW task with tomorrow's date (this makes it appear in tomorrow)
            const newTask = new Task({
                title: task.title,
                description: task.description,
                priority: task.priority,
                date: tomorrow // KEY FIX: Set date to tomorrow so it appears in tomorrow's list
            });
            
            await newTask.save();
            newTomorrowTasks.push(newTask);
            
            // Mark original task as moved (this removes it from today)
            await Task.findByIdAndUpdate(task._id, { moved: true });
            movedTaskIds.push(task._id);
        }
        
        const message = `Successfully moved ${newTomorrowTasks.length} task${newTomorrowTasks.length !== 1 ? 's' : ''} to tomorrow`;
        
        res.json({ 
            movedCount: newTomorrowTasks.length,
            message: message,
            tasks: newTomorrowTasks, // Return the new tomorrow tasks
            movedTaskIds: movedTaskIds // IDs of original tasks that were moved
        });
        
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

module.exports = router;'''
    
    update_file("backend/routes/tasks.js", fixed_tasks_route)
    
    print("🔄 Updating frontend to handle tomorrow tasks properly...")
    
    # 2. Update App.js to handle both today and tomorrow tasks
    try:
        with open("frontend/src/App.js", 'r') as f:
            app_content = f.read()
        
        # Update the state to include tomorrow tasks
        import re
        
        # Replace useState declarations to include tomorrow tasks
        if "tomorrowTasks" not in app_content:
            app_content = app_content.replace(
                "const [todayTasks, setTodayTasks] = useState([]);",
                "const [todayTasks, setTodayTasks] = useState([]);\n    const [tomorrowTasks, setTomorrowTasks] = useState([]);"
            )
        
        # Update loadTasks function
        new_load_tasks = '''    const loadTasks = async () => {
        try {
            setLoading(true);
            const response = await axios.get('/api/tasks/today');
            
            // FIXED: Handle both today and tomorrow tasks
            setTodayTasks(response.data.today || []);
            setTomorrowTasks(response.data.tomorrow || []);
        } catch (error) {
            console.error('Error loading tasks:', error);
            addNotification('Error Loading Tasks', 'Failed to load tasks', 'error');
        } finally {
            setLoading(false);
        }
    };'''
        
        app_content = re.sub(
            r'const loadTasks = async \(\) => \{[^}]*\}[^}]*\};',
            new_load_tasks,
            app_content,
            flags=re.DOTALL
        )
        
        # Update moveUncompletedTasks function
        new_move_function = '''    const moveUncompletedTasks = async () => {
        try {
            const response = await axios.post('/api/tasks/move-to-tomorrow');
            
            if (response.data.movedCount === 0) {
                addNotification('Nothing to Move', 'All tasks completed!', 'info');
            } else {
                // FIXED: Remove moved tasks from today AND add them to tomorrow
                const movedTaskIds = response.data.movedTaskIds || [];
                const newTomorrowTasks = response.data.tasks || [];
                
                // Remove from today's list
                setTodayTasks(prev => prev.filter(task => !movedTaskIds.includes(task._id)));
                
                // Add to tomorrow's list
                setTomorrowTasks(prev => [...prev, ...newTomorrowTasks]);
                
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
        
        app_content = re.sub(
            r'const moveUncompletedTasks = async \(\) => \{[^}]*\}[^}]*\};',
            new_move_function,
            app_content,
            flags=re.DOTALL
        )
        
        # Update the JSX to include tomorrow tasks section
        if "tomorrowTasks.length > 0" not in app_content:
            tomorrow_section = '''                            </div>
                            
                            {/* Tomorrow Section - FIXED to show moved tasks */}
                            {tomorrowTasks.length > 0 && (
                                <div className="tomorrow-section">
                                    <TomorrowTasks 
                                        tasks={tomorrowTasks}
                                        onUpdate={updateTask}
                                        onDelete={deleteTask}
                                    />
                                </div>
                            )}
                        </div>'''
            
            app_content = app_content.replace(
                "                            </div>\n                        </div>",
                tomorrow_section
            )
        
        # Make sure TomorrowTasks is imported
        if "TomorrowTasks" not in app_content:
            app_content = app_content.replace(
                "import TaskList from './components/TaskList';",
                "import TaskList from './components/TaskList';\nimport TomorrowTasks from './components/TomorrowTasks';"
            )
        
        update_file("frontend/src/App.js", app_content)
        
    except Exception as e:
        print(f"❌ Error updating App.js: {e}")
    
    # 3. Create/Update TomorrowTasks component if it doesn't exist
    print("📋 Creating/updating TomorrowTasks component...")
    
    tomorrow_tasks_component = '''import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { FiClock, FiArrowRight, FiCalendar, FiTrash2, FiCheck } from 'react-icons/fi';

const TomorrowTasks = ({ tasks, onUpdate, onDelete }) => {
    if (!tasks || tasks.length === 0) {
        return (
            <div className="tomorrow-empty">
                <FiCalendar className="empty-icon" />
                <h4>No tasks for tomorrow</h4>
                <p>Tasks moved from today will appear here</p>
            </div>
        );
    }

    const priorityConfig = {
        1: { label: 'High', color: '#ff6f6f' },
        2: { label: 'Medium', color: '#ffd966' },
        3: { label: 'Low', color: '#a5d6a7' }
    };

    const handleDelete = (taskId, taskTitle) => {
        if (window.confirm(`Delete "${taskTitle}" from tomorrow's tasks?`)) {
            onDelete(taskId);
        }
    };

    const handleComplete = (taskId, updates) => {
        onUpdate(taskId, updates);
    };

    return (
        <div className="tomorrow-tasks">
            <div className="tomorrow-header">
                <FiArrowRight className="tomorrow-icon" />
                <h3>Tomorrow's Tasks</h3>
                <span className="task-count">{tasks.length}</span>
            </div>
            
            <div className="tomorrow-list">
                <AnimatePresence>
                    {tasks.map((task, index) => (
                        <motion.div
                            key={task._id}
                            initial={{ opacity: 0, x: 20 }}
                            animate={{ opacity: 1, x: 0 }}
                            exit={{ opacity: 0, x: -20 }}
                            transition={{ delay: index * 0.05 }}
                            className={`tomorrow-task-item ${task.completed ? 'completed' : ''}`}
                        >
                            <div className="task-preview">
                                <div 
                                    className="priority-indicator"
                                    style={{ backgroundColor: priorityConfig[task.priority].color }}
                                ></div>
                                
                                <button
                                    className={`task-checkbox ${task.completed ? 'checked' : ''}`}
                                    onClick={() => handleComplete(task._id, { completed: !task.completed })}
                                    title={task.completed ? 'Mark as incomplete' : 'Mark as complete'}
                                >
                                    {task.completed && <FiCheck />}
                                </button>
                                
                                <div className="task-content">
                                    <h5 className={task.completed ? 'strikethrough' : ''}>{task.title}</h5>
                                    {task.description && (
                                        <p className="task-description">{task.description}</p>
                                    )}
                                </div>
                                
                                <div className="task-meta">
                                    <span className="priority-label">
                                        {priorityConfig[task.priority].label}
                                    </span>
                                    <div className="task-actions">
                                        <FiClock className="time-icon" title="Scheduled for tomorrow" />
                                        <button
                                            className="delete-btn"
                                            onClick={() => handleDelete(task._id, task.title)}
                                            title={`Delete "${task.title}"`}
                                        >
                                            <FiTrash2 />
                                        </button>
                                    </div>
                                </div>
                            </div>
                        </motion.div>
                    ))}
                </AnimatePresence>
            </div>
            
            <div className="tomorrow-footer">
                <p className="tomorrow-note">
                    💡 These tasks will become today's tasks tomorrow
                </p>
            </div>
        </div>
    );
};

export default TomorrowTasks;'''
    
    update_file("frontend/src/components/TomorrowTasks.js", tomorrow_tasks_component)
    
    # 4. Add CSS for tomorrow tasks if not exists
    print("🎨 Adding tomorrow tasks CSS...")
    
    tomorrow_css = '''
/* Tomorrow Tasks Styles */
.tomorrow-section {
    background: var(--bg-secondary);
    border: 2px solid var(--border-secondary);
    border-radius: 12px;
    padding: 1.5rem;
    margin-top: 2rem;
    transition: all 0.3s ease;
}

.tomorrow-tasks {
    width: 100%;
}

.tomorrow-header {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    margin-bottom: 1rem;
    padding-bottom: 0.75rem;
    border-bottom: 2px solid var(--border-secondary);
}

.tomorrow-icon {
    color: var(--text-tertiary);
    font-size: 1.2rem;
}

.tomorrow-header h3 {
    font-family: 'Roboto Mono', monospace;
    font-size: 1.3rem;
    font-weight: 700;
    color: var(--text-primary);
    letter-spacing: 0.05em;
    text-transform: uppercase;
    flex: 1;
}

.task-count {
    background: var(--border-secondary);
    color: var(--text-primary);
    padding: 0.25rem 0.75rem;
    border-radius: 8px;
    font-family: 'Roboto Mono', monospace;
    font-size: 0.8rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

.tomorrow-list {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
}

.tomorrow-task-item {
    background: var(--bg-primary);
    border: 1px solid var(--border-secondary);
    border-radius: 8px;
    padding: 1rem;
    transition: all 0.3s ease;
}

.tomorrow-task-item:hover {
    border-color: var(--border-primary);
    box-shadow: 0 2px 8px var(--shadow);
}

.tomorrow-task-item.completed {
    opacity: 0.7;
    background: var(--success-bg);
}

.task-preview {
    display: flex;
    align-items: center;
    gap: 1rem;
    width: 100%;
}

.priority-indicator {
    width: 4px;
    height: 40px;
    border-radius: 2px;
    flex-shrink: 0;
}

.tomorrow-task-item .task-checkbox {
    width: 24px;
    height: 24px;
    border-radius: 50%;
    border: 2px solid var(--accent-primary);
    background: var(--bg-primary);
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.3s ease;
    flex-shrink: 0;
    color: var(--bg-primary);
}

.tomorrow-task-item .task-checkbox:hover {
    border-color: var(--accent-secondary);
}

.tomorrow-task-item .task-checkbox.checked {
    background: var(--accent-primary);
    border-color: var(--accent-primary);
}

.tomorrow-task-item .task-content {
    flex: 1;
    min-width: 0;
}

.tomorrow-task-item .task-content h5 {
    font-family: 'Roboto Mono', monospace;
    font-size: 1rem;
    font-weight: 600;
    color: var(--text-primary);
    margin-bottom: 0.25rem;
}

.tomorrow-task-item .task-content h5.strikethrough {
    text-decoration: line-through;
    opacity: 0.6;
}

.tomorrow-task-item .task-description {
    font-family: 'Roboto Mono', monospace;
    font-size: 0.85rem;
    color: var(--text-tertiary);
    margin: 0;
}

.tomorrow-task-item .task-meta {
    display: flex;
    flex-direction: column;
    align-items: flex-end;
    gap: 0.5rem;
    flex-shrink: 0;
}

.tomorrow-task-item .task-actions {
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.priority-label {
    font-family: 'Roboto Mono', monospace;
    font-size: 0.75rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: var(--text-tertiary);
}

.time-icon {
    color: var(--text-muted);
    font-size: 0.9rem;
}

.tomorrow-task-item .delete-btn {
    background: transparent;
    border: none;
    color: var(--text-muted);
    cursor: pointer;
    padding: 0.25rem;
    border-radius: 4px;
    transition: all 0.3s ease;
    font-size: 0.9rem;
}

.tomorrow-task-item .delete-btn:hover {
    color: var(--text-primary);
    background: rgba(255, 255, 255, 0.1);
}

.tomorrow-footer {
    margin-top: 1rem;
    padding-top: 1rem;
    border-top: 1px solid var(--border-secondary);
}

.tomorrow-note {
    font-family: 'Roboto Mono', monospace;
    font-size: 0.8rem;
    color: var(--text-tertiary);
    text-align: center;
    font-style: italic;
    margin: 0;
}

.tomorrow-empty {
    text-align: center;
    padding: 2rem;
    color: var(--text-tertiary);
}

.empty-icon {
    font-size: 2rem;
    color: var(--text-muted);
    margin-bottom: 1rem;
}

.tomorrow-empty h4 {
    font-family: 'Roboto Mono', monospace;
    font-size: 1rem;
    font-weight: 600;
    color: var(--text-primary);
    margin-bottom: 0.5rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

.tomorrow-empty p {
    font-family: 'Roboto Mono', monospace;
    font-size: 0.9rem;
    color: var(--text-tertiary);
}

/* Mobile responsive */
@media (max-width: 768px) {
    .tomorrow-section {
        padding: 1rem;
        margin-top: 1.5rem;
    }
    
    .tomorrow-header {
        flex-wrap: wrap;
        gap: 0.5rem;
    }
    
    .tomorrow-header h3 {
        font-size: 1.1rem;
    }
    
    .task-preview {
        flex-direction: column;
        align-items: stretch;
        gap: 0.75rem;
    }
    
    .priority-indicator {
        width: 100%;
        height: 4px;
    }
    
    .tomorrow-task-item .task-meta {
        flex-direction: row;
        justify-content: space-between;
        align-items: center;
    }
}'''
    
    # Append to existing CSS if not already there
    with open("frontend/src/styles/App.css", 'a') as f:
        f.write(tomorrow_css)
    
    print("✅ Added tomorrow tasks CSS")
    
    # Create restart script
    restart_script = f'''#!/bin/bash
echo "🔧 Restarting ENTROPY with Move to Tomorrow Fix..."
echo "Backup created: {backup_dir}"
echo ""

# Kill existing processes
pkill -f "node.*server.js" || true
pkill -f "react-scripts" || true

# Wait a moment
sleep 2

echo "✅ Move to Tomorrow Fixes Applied:"
echo "  📅 Tasks moved to tomorrow now appear in Tomorrow section"
echo "  🔄 Backend creates new tasks with tomorrow's date"
echo "  ⚡ Frontend properly displays both today and tomorrow tasks"
echo "  📋 Tomorrow tasks can be completed and deleted"
echo ""
echo "🛡️  Backup & Restore:"
echo "  📦 Backup created: {backup_dir}"
echo "  🔄 To restore: python3 ../restore_backup.py {backup_dir}"
echo ""

# Start the application
./start.sh'''
    
    with open("restart_move_tomorrow_fixed.sh", 'w') as f:
        f.write(restart_script)
    os.chmod("restart_move_tomorrow_fixed.sh", 0o755)
    
    print(f"\n🎉 Move to Tomorrow Issue Fixed!")
    print("=" * 40)
    print("✅ Backend: Creates new tasks with tomorrow's date")
    print("✅ Frontend: Separate state for today and tomorrow tasks")
    print("✅ UI: Tomorrow section shows moved tasks")
    print("✅ Functionality: Can complete/delete tomorrow tasks")
    
    print(f"\n📦 BACKUP CREATED: {backup_dir}")
    print(f"🔄 Restore command: python3 ../restore_backup.py {backup_dir}")
    
    print("\n🔧 WHAT WAS FIXED:")
    print("• Backend now creates new tasks with tomorrow's date")
    print("• Frontend loads and displays both today/tomorrow tasks")
    print("• Move function adds tasks to tomorrow section")
    print("• Tomorrow tasks can be managed independently")
    
    print("\n🚀 To start with the fix:")
    print("./restart_move_tomorrow_fixed.sh")
    
    print("\n⚡ Tasks moved to tomorrow will now appear in Tomorrow section! ⚡")

if __name__ == "__main__":
    main()
