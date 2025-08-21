#!/usr/bin/env python3
"""
ENTROPY - Add Tomorrow Task Deletion + Duplicate Prevention + Backup System
Creates backups before making changes and adds enhanced task management
"""

import os
import shutil
import json
from datetime import datetime

def create_backup():
    """Create a timestamped backup of the current app"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = f"../entropy_backup_{timestamp}"
    
    print(f"📦 Creating backup: {backup_dir}")
    
    try:
        # Copy entire project to backup directory
        shutil.copytree(".", backup_dir, ignore=shutil.ignore_patterns(
            'node_modules', '.git', '*.log', 'build', 'dist'
        ))
        
        # Create backup info file
        backup_info = {
            "timestamp": timestamp,
            "date": datetime.now().isoformat(),
            "description": "Backup before adding tomorrow task deletion and duplicate prevention",
            "restore_command": f"../restore_backup.py {backup_dir}"
        }
        
        with open(f"{backup_dir}/backup_info.json", 'w') as f:
            json.dump(backup_info, f, indent=2)
        
        print(f"✅ Backup created successfully: {backup_dir}")
        return backup_dir
        
    except Exception as e:
        print(f"❌ Backup failed: {e}")
        return None

def create_restore_script():
    """Create a restore script for easy rollback"""
    restore_script = '''#!/usr/bin/env python3
"""
ENTROPY - Restore from Backup Script
Usage: python3 restore_backup.py <backup_directory>
"""

import os
import shutil
import sys
import json

def main():
    if len(sys.argv) != 2:
        print("Usage: python3 restore_backup.py <backup_directory>")
        print("Example: python3 restore_backup.py entropy_backup_20250818_224700")
        return
    
    backup_dir = sys.argv[1]
    
    if not os.path.exists(backup_dir):
        print(f"❌ Backup directory not found: {backup_dir}")
        return
    
    # Load backup info
    backup_info_path = os.path.join(backup_dir, "backup_info.json")
    if os.path.exists(backup_info_path):
        with open(backup_info_path, 'r') as f:
            info = json.load(f)
        print(f"📋 Restoring from backup created: {info['date']}")
        print(f"📋 Description: {info['description']}")
    
    response = input("⚠️  This will replace your current app. Continue? (yes/no): ")
    if response.lower() != 'yes':
        print("Restore cancelled.")
        return
    
    current_app = "entropy-app"
    
    try:
        # Create a backup of current state before restoring
        current_backup = f"entropy_current_backup_{info.get('timestamp', 'unknown')}"
        if os.path.exists(current_app):
            print(f"📦 Creating backup of current state: {current_backup}")
            shutil.copytree(current_app, current_backup, ignore=shutil.ignore_patterns(
                'node_modules', '.git', '*.log', 'build', 'dist'
            ))
        
        # Remove current app
        if os.path.exists(current_app):
            shutil.rmtree(current_app)
        
        # Restore from backup
        shutil.copytree(backup_dir, current_app, ignore=shutil.ignore_patterns(
            'backup_info.json'
        ))
        
        print("✅ Restore completed successfully!")
        print(f"🚀 To start the restored app: cd {current_app} && ./start.sh")
        print(f"💾 Your previous state was saved as: {current_backup}")
        
    except Exception as e:
        print(f"❌ Restore failed: {e}")
        return

if __name__ == "__main__":
    main()
'''
    
    with open("../restore_backup.py", 'w') as f:
        f.write(restore_script)
    
    os.chmod("../restore_backup.py", 0o755)
    print("✅ Created restore script: ../restore_backup.py")

def update_file(file_path, content):
    """Update file with given content"""
    with open(file_path, 'w') as f:
        f.write(content)
    print(f"✅ Updated: {file_path}")

def main():
    print("🛡️  ENTROPY - Enhanced Task Management + Safety Backup System")
    print("=" * 70)
    
    # Check if we're in the right directory
    if not os.path.exists("backend") or not os.path.exists("frontend"):
        print("❌ Please run this script from the entropy-app directory")
        return
    
    # 1. Create backup before making changes
    backup_dir = create_backup()
    if not backup_dir:
        print("❌ Cannot proceed without backup. Please check permissions.")
        return
    
    # 2. Create restore script
    create_restore_script()
    
    # 3. Update backend to check for duplicates and handle tomorrow tasks
    print("🔧 Updating backend with duplicate prevention...")
    
    enhanced_tasks_route = '''const express = require('express');
const router = express.Router();
const Task = require('../models/Task');

// Get today's and tomorrow's tasks
router.get('/today', async (req, res) => {
    try {
        const today = new Date();
        today.setHours(0, 0, 0, 0);
        const tomorrow = new Date(today);
        tomorrow.setDate(tomorrow.getDate() + 1);
        const dayAfterTomorrow = new Date(tomorrow);
        dayAfterTomorrow.setDate(dayAfterTomorrow.getDate() + 1);
        
        // Get today's tasks
        const todayTasks = await Task.find({
            date: { $gte: today, $lt: tomorrow },
            moved: { $ne: true } // Exclude moved tasks
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

// Check for duplicate tasks
router.post('/check-duplicate', async (req, res) => {
    try {
        const { title, date } = req.body;
        const targetDate = new Date(date);
        targetDate.setHours(0, 0, 0, 0);
        const nextDay = new Date(targetDate);
        nextDay.setDate(nextDay.getDate() + 1);
        
        // Check for existing task with same title on the same date
        const existingTask = await Task.findOne({
            title: { $regex: new RegExp(`^${title.trim()}$`, 'i') }, // Case-insensitive
            date: { $gte: targetDate, $lt: nextDay },
            completed: false,
            moved: { $ne: true }
        });
        
        res.json({
            isDuplicate: !!existingTask,
            existingTask: existingTask
        });
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// Get tasks for a specific date
router.get('/date/:date', async (req, res) => {
    try {
        const targetDate = new Date(req.params.date);
        targetDate.setHours(0, 0, 0, 0);
        const nextDay = new Date(targetDate);
        nextDay.setDate(nextDay.getDate() + 1);
        
        const tasks = await Task.find({
            date: { $gte: targetDate, $lt: nextDay }
        }).sort({ priority: 1, createdAt: 1 });
        
        res.json(tasks);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// Create new task with duplicate prevention
router.post('/', async (req, res) => {
    try {
        const { title, description, priority, date } = req.body;
        
        if (!title || !priority) {
            return res.status(400).json({ error: 'Title and priority are required' });
        }
        
        // Check for duplicates
        const taskDate = date ? new Date(date) : new Date();
        taskDate.setHours(0, 0, 0, 0);
        const nextDay = new Date(taskDate);
        nextDay.setDate(nextDay.getDate() + 1);
        
        const existingTask = await Task.findOne({
            title: { $regex: new RegExp(`^${title.trim()}$`, 'i') },
            date: { $gte: taskDate, $lt: nextDay },
            completed: false,
            moved: { $ne: true }
        });
        
        if (existingTask) {
            return res.status(409).json({ 
                error: 'Duplicate task detected',
                message: `A task with the title "${title}" already exists for this date`,
                existingTask: existingTask
            });
        }
        
        const task = new Task({
            title: title.trim(),
            description: description?.trim(),
            priority,
            date: taskDate
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
        
        // If updating title, check for duplicates
        if (updates.title) {
            const task = await Task.findById(id);
            if (!task) {
                return res.status(404).json({ error: 'Task not found' });
            }
            
            const taskDate = task.date;
            const nextDay = new Date(taskDate);
            nextDay.setDate(nextDay.getDate() + 1);
            
            const existingTask = await Task.findOne({
                _id: { $ne: id },
                title: { $regex: new RegExp(`^${updates.title.trim()}$`, 'i') },
                date: { $gte: taskDate, $lt: nextDay },
                completed: false,
                moved: { $ne: true }
            });
            
            if (existingTask) {
                return res.status(409).json({ 
                    error: 'Duplicate task detected',
                    message: `A task with the title "${updates.title}" already exists for this date`
                });
            }
            
            updates.title = updates.title.trim();
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

// Delete task (works for both today and tomorrow)
router.delete('/:id', async (req, res) => {
    try {
        const { id } = req.params;
        const task = await Task.findByIdAndDelete(id);
        
        if (!task) {
            return res.status(404).json({ error: 'Task not found' });
        }
        
        // Determine if it was a today or tomorrow task
        const today = new Date();
        today.setHours(0, 0, 0, 0);
        const tomorrow = new Date(today);
        tomorrow.setDate(tomorrow.getDate() + 1);
        
        let taskType = 'unknown';
        if (task.date >= today && task.date < tomorrow) {
            taskType = 'today';
        } else if (task.date >= tomorrow) {
            taskType = 'tomorrow';
        }
        
        res.json({ 
            message: 'Task deleted successfully',
            deletedTask: task,
            taskType: taskType
        });
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// Move uncompleted tasks to tomorrow - Enhanced
router.post('/move-to-tomorrow', async (req, res) => {
    try {
        const today = new Date();
        today.setHours(0, 0, 0, 0);
        const tomorrow = new Date(today);
        tomorrow.setDate(tomorrow.getDate() + 1);
        
        const uncompletedTasks = await Task.find({
            date: { $gte: today, $lt: tomorrow },
            completed: false,
            moved: { $ne: true }
        });
        
        if (uncompletedTasks.length === 0) {
            return res.json({ 
                movedCount: 0, 
                message: 'No uncompleted tasks to move',
                tasks: [] 
            });
        }
        
        const movedTasks = [];
        const duplicateSkipped = [];
        
        for (let task of uncompletedTasks) {
            // Check if task already exists for tomorrow
            const dayAfterTomorrow = new Date(tomorrow);
            dayAfterTomorrow.setDate(dayAfterTomorrow.getDate() + 1);
            
            const existingTomorrowTask = await Task.findOne({
                title: { $regex: new RegExp(`^${task.title.trim()}$`, 'i') },
                date: { $gte: tomorrow, $lt: dayAfterTomorrow },
                completed: false
            });
            
            if (existingTomorrowTask) {
                duplicateSkipped.push(task.title);
                // Just mark the today task as moved to avoid showing it again
                await Task.findByIdAndUpdate(task._id, { moved: true });
                continue;
            }
            
            const newTask = new Task({
                title: task.title,
                description: task.description,
                priority: task.priority,
                date: tomorrow
            });
            await newTask.save();
            movedTasks.push(newTask);
            
            // Mark original as moved
            await Task.findByIdAndUpdate(task._id, { moved: true });
        }
        
        let message = `Successfully moved ${movedTasks.length} task${movedTasks.length !== 1 ? 's' : ''} to tomorrow`;
        if (duplicateSkipped.length > 0) {
            message += `. Skipped ${duplicateSkipped.length} duplicate${duplicateSkipped.length !== 1 ? 's' : ''}: ${duplicateSkipped.join(', ')}`;
        }
        
        res.json({ 
            movedCount: movedTasks.length,
            duplicateSkipped: duplicateSkipped.length,
            tasks: movedTasks,
            message: message
        });
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

module.exports = router;'''
    
    update_file("backend/routes/tasks.js", enhanced_tasks_route)
    
    # 4. Update TomorrowTasks component to allow deletion
    print("📋 Updating Tomorrow tasks component with delete functionality...")
    
    enhanced_tomorrow_tasks = '''import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { FiClock, FiArrowRight, FiCalendar, FiTrash2, FiCheck } from 'react-icons/fi';

const TomorrowTasks = ({ tasks, onUpdate, onDelete, notifications }) => {
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
    
    update_file("frontend/src/components/TomorrowTasks.js", enhanced_tomorrow_tasks)
    
    # 5. Update TaskForm to check for duplicates
    print("📝 Updating TaskForm with duplicate prevention...")
    
    enhanced_task_form = '''import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { FiAlertTriangle } from 'react-icons/fi';
import axios from 'axios';

const TaskForm = ({ onSubmit, onCancel }) => {
    const [formData, setFormData] = useState({
        title: '',
        description: '',
        priority: 1
    });
    const [duplicateWarning, setDuplicateWarning] = useState(null);
    const [isChecking, setIsChecking] = useState(false);

    const checkForDuplicate = async (title) => {
        if (!title.trim()) {
            setDuplicateWarning(null);
            return;
        }

        try {
            setIsChecking(true);
            const response = await axios.post('/api/tasks/check-duplicate', {
                title: title.trim(),
                date: new Date().toISOString()
            });
            
            if (response.data.isDuplicate) {
                setDuplicateWarning({
                    message: `A task called "${title.trim()}" already exists for today`,
                    existingTask: response.data.existingTask
                });
            } else {
                setDuplicateWarning(null);
            }
        } catch (error) {
            console.error('Error checking for duplicates:', error);
            setDuplicateWarning(null);
        } finally {
            setIsChecking(false);
        }
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        
        if (!formData.title.trim()) return;
        
        // Final duplicate check before submission
        try {
            await checkForDuplicate(formData.title);
            
            // If there's a duplicate warning, ask for confirmation
            if (duplicateWarning) {
                const confirm = window.confirm(
                    `A similar task already exists. Do you want to create this task anyway?\\n\\nExisting: "${duplicateWarning.existingTask?.title}"\\nNew: "${formData.title}"`
                );
                if (!confirm) return;
            }
            
            onSubmit(formData);
            setFormData({ title: '', description: '', priority: 1 });
            setDuplicateWarning(null);
        } catch (error) {
            console.error('Error submitting task:', error);
        }
    };

    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: name === 'priority' ? parseInt(value) : value
        }));
        
        // Check for duplicates when title changes
        if (name === 'title') {
            const debounceTimeout = setTimeout(() => {
                checkForDuplicate(value);
            }, 500);
            
            return () => clearTimeout(debounceTimeout);
        }
    };

    return (
        <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            className="task-form-overlay"
        >
            <div className="task-form">
                <h3>Add New Task</h3>
                <form onSubmit={handleSubmit}>
                    <div className="form-group">
                        <label htmlFor="title">Task Title *</label>
                        <input
                            type="text"
                            id="title"
                            name="title"
                            value={formData.title}
                            onChange={handleChange}
                            placeholder="What needs to be done?"
                            maxLength={200}
                            required
                            autoFocus
                            className={duplicateWarning ? 'duplicate-warning' : ''}
                        />
                        {isChecking && (
                            <div className="checking-duplicate">
                                Checking for duplicates...
                            </div>
                        )}
                        {duplicateWarning && (
                            <motion.div 
                                className="duplicate-alert"
                                initial={{ opacity: 0, y: -10 }}
                                animate={{ opacity: 1, y: 0 }}
                            >
                                <FiAlertTriangle />
                                <span>{duplicateWarning.message}</span>
                            </motion.div>
                        )}
                    </div>

                    <div className="form-group">
                        <label htmlFor="description">Description (optional)</label>
                        <textarea
                            id="description"
                            name="description"
                            value={formData.description}
                            onChange={handleChange}
                            placeholder="Additional details..."
                            maxLength={1000}
                            rows={3}
                        />
                    </div>

                    <div className="form-group">
                        <label htmlFor="priority">Priority</label>
                        <select
                            id="priority"
                            name="priority"
                            value={formData.priority}
                            onChange={handleChange}
                        >
                            <option value={1}>🔥 High Priority</option>
                            <option value={2}>⚡ Medium Priority</option>
                            <option value={3}>📋 Low Priority</option>
                        </select>
                    </div>

                    <div className="form-actions">
                        <button type="button" onClick={onCancel} className="btn-cancel">
                            Cancel
                        </button>
                        <button 
                            type="submit" 
                            className={`btn-submit ${duplicateWarning ? 'duplicate-submit' : ''}`}
                            disabled={isChecking}
                        >
                            {duplicateWarning ? 'Add Anyway' : 'Add Task'}
                        </button>
                    </div>
                </form>
            </div>
        </motion.div>
    );
};

export default TaskForm;'''
    
    update_file("frontend/src/components/TaskForm.js", enhanced_task_form)
    
    # 6. Update App.js to handle the enhanced functionality
    print("🔄 Updating main App component...")
    
    with open("frontend/src/App.js", 'r') as f:
        app_content = f.read()
    
    # Update the addTask function to handle duplicates
    app_content = app_content.replace(
        '''const addTask = async (taskData) => {
        try {
            const response = await axios.post('/api/tasks', taskData);
            setTodayTasks(prev => [...prev, response.data]);
            setShowTaskForm(false);
            
            addNotification(
                'Task Added Successfully!', 
                `"${taskData.title}" has been added to today's battle plan`, 
                'success'
            );
        } catch (error) {
            console.error('Error adding task:', error);
            addNotification(
                'Failed to Add Task', 
                'There was an error adding your task. Please try again.', 
                'error'
            );
        }
    };''',
        '''const addTask = async (taskData) => {
        try {
            const response = await axios.post('/api/tasks', taskData);
            setTodayTasks(prev => [...prev, response.data]);
            setShowTaskForm(false);
            
            addNotification(
                'Task Added Successfully!', 
                `"${taskData.title}" has been added to today's battle plan`, 
                'success'
            );
        } catch (error) {
            console.error('Error adding task:', error);
            
            if (error.response?.status === 409) {
                // Duplicate task error
                addNotification(
                    'Duplicate Task Detected! ⚠️',
                    error.response.data.message,
                    'warning',
                    6000
                );
            } else {
                addNotification(
                    'Failed to Add Task', 
                    'There was an error adding your task. Please try again.', 
                    'error'
                );
            }
        }
    };'''
    )
    
    # Update the deleteTask function to provide better feedback
    app_content = app_content.replace(
        '''const deleteTask = async (taskId) => {
        try {
            await axios.delete(`/api/tasks/${taskId}`);
            
            // Remove from both lists
            setTodayTasks(prev => prev.filter(task => task._id !== taskId));
            setTomorrowTasks(prev => prev.filter(task => task._id !== taskId));
            
            addNotification(
                'Task Deleted', 
                'Task has been removed from your list', 
                'info'
            );
            
            loadTodaysProgress();
        } catch (error) {
            console.error('Error deleting task:', error);
            addNotification(
                'Delete Failed', 
                'Failed to delete the task. Please try again.', 
                'error'
            );
        }
    };''',
        '''const deleteTask = async (taskId) => {
        try {
            const response = await axios.delete(`/api/tasks/${taskId}`);
            
            // Remove from both lists
            setTodayTasks(prev => prev.filter(task => task._id !== taskId));
            setTomorrowTasks(prev => prev.filter(task => task._id !== taskId));
            
            const taskType = response.data.taskType;
            const taskTitle = response.data.deletedTask?.title || 'Task';
            
            addNotification(
                `${taskType === 'tomorrow' ? 'Tomorrow' : 'Today'} Task Deleted`,
                `"${taskTitle}" has been removed`,
                'info'
            );
            
            loadTodaysProgress();
        } catch (error) {
            console.error('Error deleting task:', error);
            addNotification(
                'Delete Failed', 
                'Failed to delete the task. Please try again.', 
                'error'
            );
        }
    };'''
    )
    
    update_file("frontend/src/App.js", app_content)
    
    # 7. Add CSS for new features
    print("🎨 Adding styles for duplicate prevention and tomorrow task actions...")
    
    additional_css = '''
/* Duplicate Prevention Styles */
.duplicate-warning {
    border-color: #ff9800 !important;
    background-color: #fff8e1 !important;
}

.checking-duplicate {
    font-family: 'Roboto Mono', monospace;
    font-size: 0.8rem;
    color: #666666;
    margin-top: 0.25rem;
    font-style: italic;
}

.duplicate-alert {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    background: #fff3cd;
    border: 1px solid #ffc107;
    color: #856404;
    padding: 0.5rem;
    border-radius: 6px;
    margin-top: 0.5rem;
    font-family: 'Roboto Mono', monospace;
    font-size: 0.8rem;
}

.duplicate-alert svg {
    flex-shrink: 0;
    font-size: 1rem;
}

.duplicate-submit {
    background: #ff9800 !important;
    border-color: #ff9800 !important;
}

.duplicate-submit:hover {
    background: #f57c00 !important;
    border-color: #f57c00 !important;
}

/* Enhanced Tomorrow Tasks Styles */
.tomorrow-task-item.completed {
    opacity: 0.7;
    background: #f0f8f0;
}

.tomorrow-task-item .task-checkbox {
    width: 24px;
    height: 24px;
    border-radius: 50%;
    border: 2px solid #000000;
    background: #ffffff;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.3s ease;
    flex-shrink: 0;
    color: #ffffff;
    margin-right: 0.75rem;
}

.tomorrow-task-item .task-checkbox:hover {
    border-color: #333333;
}

.tomorrow-task-item .task-checkbox.checked {
    background: #000000;
    border-color: #000000;
}

.tomorrow-task-item .task-content h5.strikethrough {
    text-decoration: line-through;
    opacity: 0.6;
}

.tomorrow-task-item .task-actions {
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.tomorrow-task-item .delete-btn {
    background: transparent;
    border: none;
    color: #999999;
    cursor: pointer;
    padding: 0.25rem;
    border-radius: 4px;
    transition: all 0.3s ease;
    font-size: 0.9rem;
}

.tomorrow-task-item .delete-btn:hover {
    color: #000000;
    background: rgba(0, 0, 0, 0.1);
}

.tomorrow-footer {
    margin-top: 1rem;
    padding-top: 1rem;
    border-top: 1px solid #e0e0e0;
}

.tomorrow-note {
    font-family: 'Roboto Mono', monospace;
    font-size: 0.8rem;
    color: #666666;
    text-align: center;
    font-style: italic;
    margin: 0;
}

/* Enhanced Task Preview Layout */
.task-preview {
    display: flex;
    align-items: center;
    gap: 1rem;
    width: 100%;
}

.task-preview .task-content {
    flex: 1;
    min-width: 0; /* Allows text truncation */
}

.task-preview .task-meta {
    display: flex;
    flex-direction: column;
    align-items: flex-end;
    gap: 0.5rem;
    flex-shrink: 0;
}

/* Backup Status Indicator */
.backup-status {
    position: fixed;
    bottom: 1rem;
    left: 1rem;
    background: #f0f8f0;
    border: 2px solid #4caf50;
    color: #2e7d32;
    padding: 0.5rem 1rem;
    border-radius: 8px;
    font-family: 'Roboto Mono', monospace;
    font-size: 0.8rem;
    font-weight: 600;
    z-index: 1000;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.backup-status.show {
    opacity: 1;
    transform: translateY(0);
}

.backup-status.hide {
    opacity: 0;
    transform: translateY(100px);
    transition: all 0.3s ease;
}

/* Improved Mobile Support */
@media (max-width: 768px) {
    .duplicate-alert {
        flex-direction: column;
        text-align: center;
        gap: 0.25rem;
    }
    
    .task-preview {
        flex-direction: column;
        align-items: stretch;
        gap: 0.75rem;
    }
    
    .task-preview .task-meta {
        flex-direction: row;
        justify-content: space-between;
        align-items: center;
    }
    
    .tomorrow-task-item .task-actions {
        justify-content: flex-end;
    }
}

@media (max-width: 480px) {
    .backup-status {
        left: 0.5rem;
        right: 0.5rem;
        text-align: center;
    }
    
    .duplicate-alert {
        font-size: 0.75rem;
        padding: 0.4rem;
    }
    
    .tomorrow-note {
        font-size: 0.75rem;
    }
}

/* Animation for task deletion */
@keyframes taskDelete {
    0% {
        opacity: 1;
        transform: translateX(0);
    }
    100% {
        opacity: 0;
        transform: translateX(-100px);
    }
}

.tomorrow-task-item.deleting {
    animation: taskDelete 0.3s ease-out forwards;
}

/* Focus accessibility improvements */
.tomorrow-task-item .task-checkbox:focus,
.tomorrow-task-item .delete-btn:focus {
    outline: 2px solid #000000;
    outline-offset: 2px;
}

/* High contrast mode support */
@media (prefers-contrast: high) {
    .duplicate-alert {
        background: #ffffff;
        border: 2px solid #000000;
        color: #000000;
    }
    
    .tomorrow-task-item .delete-btn:hover {
        background: #000000;
        color: #ffffff;
    }
}'''
    
    # Append to existing CSS
    with open("frontend/src/styles/App.css", 'a') as f:
        f.write(additional_css)
    
    print("✅ Added enhanced styles")
    
    # 8. Create comprehensive restart script
    restart_script = f'''#!/bin/bash
echo "🛡️  Restarting ENTROPY with Enhanced Safety Features..."
echo "Backup created: {backup_dir}"
echo ""

# Kill existing processes
pkill -f "node.*server.js" || true
pkill -f "react-scripts" || true

# Wait a moment
sleep 2

echo "✅ New Safety Features Added:"
echo "  📦 Automatic backup system created"
echo "  🗑️  Delete tomorrow tasks functionality"
echo "  🚫 Duplicate task prevention"
echo "  🔄 Enhanced error handling"
echo "  📱 Better mobile experience"
echo ""
echo "🛡️  Backup & Restore:"
echo "  📦 Backup created: {backup_dir}"
echo "  🔄 To restore: python3 ../restore_backup.py {backup_dir}"
echo ""

# Start the application
./start.sh'''
    
    update_file("restart_enhanced_safety.sh", restart_script)
    os.chmod("restart_enhanced_safety.sh", 0o755)
    
    # 9. Create quick backup list script
    backup_list_script = '''#!/bin/bash
echo "📦 Available ENTROPY Backups:"
echo "=============================="

cd ..
ls -la entropy_backup_* 2>/dev/null | while read -r line; do
    backup_dir=$(echo "$line" | awk '{print $NF}')
    if [[ -d "$backup_dir" && -f "$backup_dir/backup_info.json" ]]; then
        info=$(cat "$backup_dir/backup_info.json" 2>/dev/null)
        date=$(echo "$info" | grep '"date"' | cut -d'"' -f4)
        desc=$(echo "$info" | grep '"description"' | cut -d'"' -f4)
        echo "📂 $backup_dir"
        echo "   📅 Created: $date"
        echo "   📝 Description: $desc"
        echo "   🔄 Restore: python3 ../restore_backup.py $backup_dir"
        echo ""
    fi
done

if ! ls entropy_backup_* >/dev/null 2>&1; then
    echo "No backups found."
fi'''
    
    update_file("../list_backups.sh", backup_list_script)
    os.chmod("../list_backups.sh", 0o755)
    
    print("\n🎉 Enhanced ENTROPY with Safety Features Complete!")
    print("=" * 60)
    print("✅ Backup System: Automatic backups before changes")
    print("✅ Tomorrow Tasks: Can now delete tasks meant for tomorrow")
    print("✅ Duplicate Prevention: Checks for duplicate task names")
    print("✅ Enhanced UX: Better error handling and notifications")
    print("✅ Restore System: Easy rollback to previous versions")
    
    print(f"\n📦 BACKUP CREATED: {backup_dir}")
    print("\n🛡️  SAFETY COMMANDS:")
    print(f"🔄 Restore this backup: python3 ../restore_backup.py {backup_dir}")
    print("📋 List all backups: ../list_backups.sh")
    print("🚀 Start enhanced app: ./restart_enhanced_safety.sh")
    
    print("\n🎯 NEW FEATURES:")
    print("• Tomorrow tasks can be deleted with trash button")
    print("• Duplicate task names are automatically detected")
    print("• Enhanced notifications for all actions")
    print("• Automatic backup before any changes")
    print("• Easy restore system for safety")
    
    print("\n⚡ Your app is now safer and more powerful! ⚡")

if __name__ == "__main__":
    main()
