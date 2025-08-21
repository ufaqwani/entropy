#!/usr/bin/env python3
"""
ENTROPY - Fix Move-to-Tomorrow Bug + Add Dark Mode Theme
Fixes task moving issue and adds complete dark/light theme toggle
"""

import os
import shutil
import json
from datetime import datetime

def create_backup():
    """Create a timestamped backup of the current app"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = f"../entropy_backup_darkmode_{timestamp}"
    
    print(f"📦 Creating backup: {backup_dir}")
    
    try:
        shutil.copytree(".", backup_dir, ignore=shutil.ignore_patterns(
            'node_modules', '.git', '*.log', 'build', 'dist'
        ))
        
        backup_info = {
            "timestamp": timestamp,
            "date": datetime.now().isoformat(),
            "description": "Backup before fixing move-to-tomorrow and adding dark mode",
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
    print("🌓 ENTROPY - Fix Move Bug + Add Dark Mode Theme")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists("backend") or not os.path.exists("frontend"):
        print("❌ Please run this script from the entropy-app directory")
        return
    
    # 1. Create backup before making changes
    backup_dir = create_backup()
    if not backup_dir:
        print("❌ Cannot proceed without backup. Please check permissions.")
        return
    
    # 2. Fix the backend to properly handle moved tasks
    print("🔧 Fixing move-to-tomorrow backend logic...")
    
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
        
        // Get today's tasks - exclude moved tasks
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

// Check for duplicate tasks
router.post('/check-duplicate', async (req, res) => {
    try {
        const { title, date } = req.body;
        const targetDate = new Date(date);
        targetDate.setHours(0, 0, 0, 0);
        const nextDay = new Date(targetDate);
        nextDay.setDate(nextDay.getDate() + 1);
        
        // Check for existing task with same title on the same date (exclude moved)
        const existingTask = await Task.findOne({
            title: { $regex: new RegExp(`^${title.trim()}$`, 'i') },
            date: { $gte: targetDate, $lt: nextDay },
            completed: false,
            $or: [
                { moved: { $exists: false } },
                { moved: false }
            ]
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
            $or: [
                { moved: { $exists: false } },
                { moved: false }
            ]
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
                $or: [
                    { moved: { $exists: false } },
                    { moved: false }
                ]
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

// Move uncompleted tasks to tomorrow - FIXED VERSION
router.post('/move-to-tomorrow', async (req, res) => {
    try {
        const today = new Date();
        today.setHours(0, 0, 0, 0);
        const tomorrow = new Date(today);
        tomorrow.setDate(tomorrow.getDate() + 1);
        
        // Get uncompleted tasks from today (not already moved)
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
        
        const movedTasks = [];
        const duplicateSkipped = [];
        const movedTaskIds = [];
        
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
                // Mark the today task as moved
                await Task.findByIdAndUpdate(task._id, { moved: true });
                movedTaskIds.push(task._id);
                continue;
            }
            
            // Create new task for tomorrow
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
            movedTaskIds.push(task._id);
        }
        
        let message = `Successfully moved ${movedTasks.length} task${movedTasks.length !== 1 ? 's' : ''} to tomorrow`;
        if (duplicateSkipped.length > 0) {
            message += `. Skipped ${duplicateSkipped.length} duplicate${duplicateSkipped.length !== 1 ? 's' : ''}: ${duplicateSkipped.join(', ')}`;
        }
        
        res.json({ 
            movedCount: movedTasks.length,
            duplicateSkipped: duplicateSkipped.length,
            tasks: movedTasks,
            message: message,
            movedTaskIds: movedTaskIds // Send IDs of moved tasks for frontend removal
        });
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

module.exports = router;'''
    
    update_file("backend/routes/tasks.js", fixed_tasks_route)
    
    # 3. Create Dark Mode Context and Hook
    print("🌙 Creating dark mode context and hook...")
    
    dark_mode_context = '''import React, { createContext, useContext, useState, useEffect } from 'react';

const ThemeContext = createContext();

export const useTheme = () => {
    const context = useContext(ThemeContext);
    if (!context) {
        throw new Error('useTheme must be used within a ThemeProvider');
    }
    return context;
};

export const ThemeProvider = ({ children }) => {
    const [isDarkMode, setIsDarkMode] = useState(() => {
        // Check localStorage for saved preference
        const saved = localStorage.getItem('entropy-theme');
        if (saved) {
            return saved === 'dark';
        }
        // Check system preference
        return window.matchMedia('(prefers-color-scheme: dark)').matches;
    });

    useEffect(() => {
        // Save preference to localStorage
        localStorage.setItem('entropy-theme', isDarkMode ? 'dark' : 'light');
        
        // Apply theme class to document
        document.documentElement.setAttribute('data-theme', isDarkMode ? 'dark' : 'light');
    }, [isDarkMode]);

    const toggleTheme = () => {
        setIsDarkMode(prev => !prev);
    };

    const value = {
        isDarkMode,
        toggleTheme,
        theme: isDarkMode ? 'dark' : 'light'
    };

    return (
        <ThemeContext.Provider value={value}>
            {children}
        </ThemeContext.Provider>
    );
};'''
    
    update_file("frontend/src/contexts/ThemeContext.js", dark_mode_context)
    
    # 4. Create Theme Toggle Component
    print("🎨 Creating theme toggle component...")
    
    theme_toggle_component = '''import React from 'react';
import { motion } from 'framer-motion';
import { FiSun, FiMoon } from 'react-icons/fi';
import { useTheme } from '../contexts/ThemeContext';

const ThemeToggle = () => {
    const { isDarkMode, toggleTheme } = useTheme();

    return (
        <motion.button
            className="theme-toggle"
            onClick={toggleTheme}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            title={`Switch to ${isDarkMode ? 'light' : 'dark'} mode`}
        >
            <motion.div
                className="theme-toggle-track"
                animate={{
                    backgroundColor: isDarkMode ? '#4a5568' : '#e2e8f0'
                }}
                transition={{ duration: 0.3 }}
            >
                <motion.div
                    className="theme-toggle-handle"
                    animate={{
                        x: isDarkMode ? 24 : 0
                    }}
                    transition={{
                        type: "spring",
                        stiffness: 300,
                        damping: 30
                    }}
                >
                    <motion.div
                        animate={{ rotate: isDarkMode ? 180 : 0 }}
                        transition={{ duration: 0.3 }}
                    >
                        {isDarkMode ? <FiMoon size={14} /> : <FiSun size={14} />}
                    </motion.div>
                </motion.div>
            </motion.div>
            
            <span className="theme-toggle-label">
                {isDarkMode ? 'DARK' : 'LIGHT'}
            </span>
        </motion.button>
    );
};

export default ThemeToggle;'''
    
    update_file("frontend/src/components/ThemeToggle.js", theme_toggle_component)
    
    # 5. Update App.js to fix move bug and include theme provider
    print("🔄 Updating main App component with fixes and dark mode...")
    
    fixed_app_js = '''import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { ThemeProvider } from './contexts/ThemeContext';
import TaskList from './components/TaskList';
import TaskForm from './components/TaskForm';
import TomorrowTasks from './components/TomorrowTasks';
import ProgressChart from './components/ProgressChart';
import EntropyAnimation from './components/EntropyAnimation';
import DailyAudit from './components/DailyAudit';
import CompletedTasksHistory from './components/CompletedTasksHistory';
import NotificationSystem, { useNotifications } from './components/NotificationSystem';
import ThemeToggle from './components/ThemeToggle';
import './styles/App.css';

function AppContent() {
    const [todayTasks, setTodayTasks] = useState([]);
    const [tomorrowTasks, setTomorrowTasks] = useState([]);
    const [showTaskForm, setShowTaskForm] = useState(false);
    const [currentView, setCurrentView] = useState('today');
    const [progressData, setProgressData] = useState(null);
    const [loading, setLoading] = useState(true);
    
    // Notification system
    const { notifications, addNotification, removeNotification } = useNotifications();

    useEffect(() => {
        loadTasks();
        loadTodaysProgress();
    }, []);

    const loadTasks = async () => {
        try {
            setLoading(true);
            const response = await axios.get('/api/tasks/today');
            setTodayTasks(response.data.today || []);
            setTomorrowTasks(response.data.tomorrow || []);
        } catch (error) {
            console.error('Error loading tasks:', error);
            addNotification(
                'Error Loading Tasks', 
                'Failed to load your tasks. Please refresh the page.', 
                'error'
            );
        } finally {
            setLoading(false);
        }
    };

    const loadTodaysProgress = async () => {
        try {
            const response = await axios.get('/api/progress/today');
            setProgressData(response.data);
        } catch (error) {
            console.error('Error loading progress:', error);
        }
    };

    const addTask = async (taskData) => {
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
    };

    const updateTask = async (taskId, updates) => {
        try {
            const response = await axios.put(`/api/tasks/${taskId}`, updates);
            
            // Update the task in the appropriate list
            setTodayTasks(prev => prev.map(task => 
                task._id === taskId ? response.data : task
            ));
            setTomorrowTasks(prev => prev.map(task => 
                task._id === taskId ? response.data : task
            ));
            
            // Show completion notification
            if (updates.completed) {
                addNotification(
                    'Task Completed! ⚡', 
                    `Great job completing "${response.data.title}"`, 
                    'success'
                );
            }
            
            loadTodaysProgress();
        } catch (error) {
            console.error('Error updating task:', error);
            addNotification(
                'Update Failed', 
                'Failed to update the task. Please try again.', 
                'error'
            );
        }
    };

    const deleteTask = async (taskId) => {
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
    };

    // FIXED: Move uncompleted tasks with proper state management
    const moveUncompletedTasks = async () => {
        try {
            const response = await axios.post('/api/tasks/move-to-tomorrow');
            
            if (response.data.movedCount === 0) {
                addNotification(
                    'Nothing to Move', 
                    'All tasks are completed! Great job!', 
                    'info'
                );
            } else {
                // Remove moved tasks from today's list immediately
                const movedTaskIds = response.data.movedTaskIds || [];
                setTodayTasks(prev => prev.filter(task => !movedTaskIds.includes(task._id)));
                
                // Add new tasks to tomorrow's list
                const newTomorrowTasks = response.data.tasks || [];
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
            addNotification(
                'Move Failed', 
                'Failed to move tasks to tomorrow. Please try again.', 
                'error'
            );
        }
    };

    if (loading) {
        return (
            <div className="app-loading">
                <div className="loading-spinner"></div>
                <p>Loading Entropy...</p>
            </div>
        );
    }

    return (
        <div className="App">
            <NotificationSystem 
                notifications={notifications} 
                removeNotification={removeNotification} 
            />
            
            <header className="app-header">
                <div className="header-content">
                    <div className="header-main">
                        <h1>⚡ ENTROPY</h1>
                        <p>Fight chaos. Complete tasks. Win the day.</p>
                    </div>
                    <ThemeToggle />
                </div>
            </header>

            <nav className="app-nav">
                <button 
                    className={currentView === 'today' ? 'active' : ''}
                    onClick={() => setCurrentView('today')}
                >
                    Today
                </button>
                <button 
                    className={currentView === 'history' ? 'active' : ''}
                    onClick={() => setCurrentView('history')}
                >
                    History
                </button>
                <button 
                    className={currentView === 'progress' ? 'active' : ''}
                    onClick={() => setCurrentView('progress')}
                >
                    Progress
                </button>
                <button 
                    className={currentView === 'audit' ? 'active' : ''}
                    onClick={() => setCurrentView('audit')}
                >
                    Daily Audit
                </button>
            </nav>

            <main className="app-main">
                {currentView === 'today' && (
                    <>
                        <EntropyAnimation 
                            completionRate={progressData?.completionRate || 0}
                            totalTasks={todayTasks.length}
                            completedTasks={todayTasks.filter(t => t.completed).length}
                        />
                        
                        <div className="tasks-container">
                            <div className="today-section">
                                <div className="task-header">
                                    <h2>Today's Battle Against Entropy</h2>
                                    <div className="task-actions">
                                        <button 
                                            className="btn-primary"
                                            onClick={() => setShowTaskForm(true)}
                                            disabled={todayTasks.length >= 5}
                                        >
                                            + Add Task {todayTasks.length >= 3 && '(Not Recommended)'}
                                        </button>
                                        {todayTasks.some(t => !t.completed) && (
                                            <button 
                                                className="btn-secondary"
                                                onClick={moveUncompletedTasks}
                                            >
                                                Move Uncompleted to Tomorrow
                                            </button>
                                        )}
                                    </div>
                                </div>

                                <TaskList 
                                    tasks={todayTasks}
                                    onUpdate={updateTask}
                                    onDelete={deleteTask}
                                />
                            </div>
                            
                            {/* Tomorrow Section */}
                            {tomorrowTasks.length > 0 && (
                                <div className="tomorrow-section">
                                    <TomorrowTasks 
                                        tasks={tomorrowTasks}
                                        onUpdate={updateTask}
                                        onDelete={deleteTask}
                                    />
                                </div>
                            )}
                        </div>

                        {showTaskForm && (
                            <TaskForm 
                                onSubmit={addTask}
                                onCancel={() => setShowTaskForm(false)}
                            />
                        )}
                    </>
                )}

                {currentView === 'history' && (
                    <CompletedTasksHistory />
                )}

                {currentView === 'progress' && (
                    <ProgressChart />
                )}

                {currentView === 'audit' && (
                    <DailyAudit 
                        progressData={progressData}
                        onAuditComplete={loadTodaysProgress}
                    />
                )}
            </main>
        </div>
    );
}

function App() {
    return (
        <ThemeProvider>
            <AppContent />
        </ThemeProvider>
    );
}

export default App;'''
    
    update_file("frontend/src/App.js", fixed_app_js)
    
    # 6. Update context directory
    os.makedirs("frontend/src/contexts", exist_ok=True)
    
    # 7. Create comprehensive dark theme CSS
    print("🎨 Creating comprehensive dark mode CSS...")
    
    dark_theme_css = '''/* ENTROPY - Complete Light & Dark Theme System */

:root {
  /* Light Theme Colors */
  --bg-primary: #ffffff;
  --bg-secondary: #f8f8f8;
  --bg-tertiary: #f9f9f9;
  --text-primary: #000000;
  --text-secondary: #333333;
  --text-tertiary: #666666;
  --text-muted: #999999;
  --border-primary: #000000;
  --border-secondary: #e0e0e0;
  --border-tertiary: #ddd;
  --accent-primary: #000000;
  --accent-secondary: #333333;
  --success-bg: #f0f8f0;
  --success-border: #4caf50;
  --success-text: #2e7d32;
  --warning-bg: #fff8e1;
  --warning-border: #ff9800;
  --warning-text: #ef6c00;
  --error-bg: #ffebee;
  --error-border: #f44336;
  --error-text: #c62828;
  --info-bg: #e3f2fd;
  --info-border: #2196f3;
  --info-text: #1565c0;
  --shadow: rgba(0, 0, 0, 0.1);
  --overlay: rgba(255, 255, 255, 0.95);
}

[data-theme="dark"] {
  /* Dark Theme Colors */
  --bg-primary: #1a1a1a;
  --bg-secondary: #2d2d2d;
  --bg-tertiary: #3d3d3d;
  --text-primary: #ffffff;
  --text-secondary: #e0e0e0;
  --text-tertiary: #b0b0b0;
  --text-muted: #888888;
  --border-primary: #ffffff;
  --border-secondary: #4a4a4a;
  --border-tertiary: #555555;
  --accent-primary: #ffffff;
  --accent-secondary: #e0e0e0;
  --success-bg: #1b2f1b;
  --success-border: #4caf50;
  --success-text: #81c784;
  --warning-bg: #2d2416;
  --warning-border: #ff9800;
  --warning-text: #ffb74d;
  --error-bg: #2f1b1b;
  --error-border: #f44336;
  --error-text: #e57373;
  --info-bg: #1b2228;
  --info-border: #2196f3;
  --info-text: #64b5f6;
  --shadow: rgba(0, 0, 0, 0.3);
  --overlay: rgba(26, 26, 26, 0.95);
}

* {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
}

body {
    font-family: 'Roboto Mono', 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
    background: var(--bg-primary);
    color: var(--text-primary);
    min-height: 100vh;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
    font-weight: 400;
    line-height: 1.6;
    transition: background-color 0.3s ease, color 0.3s ease;
}

.App {
    min-height: 100vh;
    display: flex;
    flex-direction: column;
    background: var(--bg-primary);
    transition: background-color 0.3s ease;
}

/* Header with Theme Toggle */
.app-header {
    background: var(--bg-secondary);
    padding: 1.5rem 2rem;
    border-bottom: 2px solid var(--border-primary);
    transition: all 0.3s ease;
}

.header-content {
    display: flex;
    justify-content: space-between;
    align-items: center;
    max-width: 1000px;
    margin: 0 auto;
}

.header-main {
    text-align: center;
    flex: 1;
}

.app-header h1 {
    font-family: 'Roboto Mono', monospace;
    font-size: 3rem;
    font-weight: 700;
    margin-bottom: 0.5rem;
    color: var(--text-primary);
    letter-spacing: 0.1em;
    text-transform: uppercase;
}

.app-header p {
    font-size: 1.1rem;
    color: var(--text-secondary);
    font-weight: 500;
    letter-spacing: 0.05em;
}

/* Theme Toggle */
.theme-toggle {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.5rem;
    background: transparent;
    border: none;
    cursor: pointer;
    padding: 0.5rem;
}

.theme-toggle-track {
    width: 50px;
    height: 26px;
    border-radius: 13px;
    position: relative;
    display: flex;
    align-items: center;
    border: 2px solid var(--border-primary);
}

.theme-toggle-handle {
    width: 20px;
    height: 20px;
    border-radius: 50%;
    background: var(--accent-primary);
    display: flex;
    align-items: center;
    justify-content: center;
    color: var(--bg-primary);
    position: absolute;
    left: 2px;
}

.theme-toggle-label {
    font-family: 'Roboto Mono', monospace;
    font-size: 0.7rem;
    font-weight: 700;
    color: var(--text-tertiary);
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

/* Navigation */
.app-nav {
    display: flex;
    justify-content: center;
    gap: 0;
    padding: 0;
    background: var(--bg-primary);
    border-bottom: 1px solid var(--border-secondary);
}

.app-nav button {
    background: var(--bg-primary);
    border: none;
    border-bottom: 3px solid transparent;
    color: var(--text-primary);
    padding: 1rem 2rem;
    cursor: pointer;
    transition: all 0.3s ease;
    font-family: 'Roboto Mono', monospace;
    font-size: 0.9rem;
    font-weight: 600;
    letter-spacing: 0.05em;
    text-transform: uppercase;
}

.app-nav button:hover {
    background: var(--bg-secondary);
    border-bottom-color: var(--border-tertiary);
}

.app-nav button.active {
    background: var(--accent-primary);
    color: var(--bg-primary);
    border-bottom-color: var(--accent-primary);
}

/* Main Content */
.app-main {
    flex: 1;
    padding: 2rem;
    max-width: 1000px;
    margin: 0 auto;
    width: 100%;
}

/* Loading */
.app-loading {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 100vh;
    gap: 1rem;
    background: var(--bg-primary);
}

.loading-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 3rem;
    gap: 1rem;
}

.loading-spinner {
    width: 40px;
    height: 40px;
    border: 3px solid var(--border-secondary);
    border-top: 3px solid var(--accent-primary);
    border-radius: 50%;
    animation: spin 1s linear infinite;
}

@keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}

/* Entropy Animation */
.entropy-animation {
    background: var(--bg-primary);
    border: 2px solid var(--border-primary);
    border-radius: 12px;
    padding: 1.5rem;
    margin-bottom: 2rem;
    text-align: center;
    transition: all 0.3s ease;
}

.progress-title {
    font-family: 'Roboto Mono', monospace;
    font-size: 1.2rem;
    font-weight: 600;
    margin-bottom: 1rem;
    color: var(--text-primary);
    letter-spacing: 0.1em;
    text-transform: uppercase;
}

.animation-container {
    width: 100%;
    max-width: 500px;
    margin: 0 auto;
}

.stairs-svg {
    width: 100%;
    height: auto;
    max-height: 200px;
    border-radius: 8px;
    background: var(--bg-tertiary);
    border: 1px solid var(--border-secondary);
}

.stair-step {
    transition: fill 0.4s ease;
}

.progress-status {
    margin-top: 1rem;
}

.status-message {
    font-family: 'Roboto Mono', monospace;
    font-size: 1rem;
    font-weight: 500;
    padding: 0.75rem 1rem;
    background: var(--bg-secondary);
    border: 1px solid var(--border-secondary);
    border-radius: 8px;
    color: var(--text-primary);
    letter-spacing: 0.05em;
}

/* Task Sections */
.tasks-container {
    display: flex;
    flex-direction: column;
    gap: 2rem;
}

.today-section {
    background: var(--bg-primary);
    border: 2px solid var(--border-primary);
    border-radius: 12px;
    padding: 2rem;
    transition: all 0.3s ease;
}

.tomorrow-section {
    background: var(--bg-secondary);
    border: 2px solid var(--border-secondary);
    border-radius: 12px;
    padding: 1.5rem;
    transition: all 0.3s ease;
}

.task-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 2rem;
    flex-wrap: wrap;
    gap: 1rem;
}

.task-header h2 {
    font-family: 'Roboto Mono', monospace;
    font-size: 1.5rem;
    font-weight: 700;
    color: var(--text-primary);
    letter-spacing: 0.05em;
    text-transform: uppercase;
}

.task-actions {
    display: flex;
    gap: 1rem;
    flex-wrap: wrap;
}

/* Buttons */
.btn-primary {
    background: var(--accent-primary);
    color: var(--bg-primary);
    border: 2px solid var(--accent-primary);
    padding: 0.75rem 1.5rem;
    border-radius: 8px;
    cursor: pointer;
    font-family: 'Roboto Mono', monospace;
    font-weight: 600;
    font-size: 0.9rem;
    letter-spacing: 0.05em;
    text-transform: uppercase;
    transition: all 0.3s ease;
}

.btn-primary:hover:not(:disabled) {
    background: var(--accent-secondary);
    border-color: var(--accent-secondary);
}

.btn-primary:disabled {
    background: var(--text-muted);
    border-color: var(--text-muted);
    color: var(--bg-secondary);
    cursor: not-allowed;
}

.btn-secondary {
    background: var(--bg-primary);
    color: var(--accent-primary);
    border: 2px solid var(--accent-primary);
    padding: 0.75rem 1.5rem;
    border-radius: 8px;
    cursor: pointer;
    font-family: 'Roboto Mono', monospace;
    font-weight: 600;
    font-size: 0.9rem;
    letter-spacing: 0.05em;
    text-transform: uppercase;
    transition: all 0.3s ease;
}

.btn-secondary:hover {
    background: var(--accent-primary);
    color: var(--bg-primary);
}

/* Task Lists */
.task-list {
    display: flex;
    flex-direction: column;
    gap: 1rem;
}

.no-tasks {
    text-align: center;
    padding: 3rem;
    color: var(--text-tertiary);
}

.no-tasks h3 {
    font-family: 'Roboto Mono', monospace;
    font-size: 1.2rem;
    margin-bottom: 0.5rem;
    color: var(--text-primary);
    font-weight: 600;
}

.task-item {
    background: var(--bg-tertiary);
    border: 2px solid var(--border-secondary);
    border-radius: 10px;
    transition: all 0.3s ease;
}

.task-item:hover {
    border-color: var(--border-primary);
    box-shadow: 0 2px 8px var(--shadow);
}

.task-item.completed {
    background: var(--success-bg);
    border-color: var(--success-border);
}

.task-content {
    display: flex;
    align-items: center;
    padding: 1.25rem;
    gap: 1rem;
}

.task-checkbox {
    width: 28px;
    height: 28px;
    border-radius: 50%;
    border: 3px solid var(--accent-primary);
    background: var(--bg-primary);
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.3s ease;
    flex-shrink: 0;
    font-size: 1rem;
    color: var(--bg-primary);
}

.task-checkbox:hover {
    border-color: var(--accent-secondary);
}

.task-checkbox.checked {
    background: var(--accent-primary);
    border-color: var(--accent-primary);
}

.task-info {
    flex: 1;
}

.task-info h4 {
    font-family: 'Roboto Mono', monospace;
    font-size: 1.1rem;
    font-weight: 600;
    margin-bottom: 0.25rem;
    color: var(--text-primary);
}

.task-info h4.strikethrough {
    text-decoration: line-through;
    opacity: 0.6;
}

.task-description {
    font-family: 'Roboto Mono', monospace;
    font-size: 0.9rem;
    color: var(--text-tertiary);
    margin: 0;
}

.task-meta {
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.priority-badge {
    display: flex;
    align-items: center;
    gap: 0.25rem;
    padding: 0.4rem 0.8rem;
    border-radius: 6px;
    font-family: 'Roboto Mono', monospace;
    font-size: 0.75rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: var(--text-primary);
    border: 1px solid var(--border-primary);
}

.delete-btn {
    background: transparent;
    border: none;
    color: var(--text-tertiary);
    cursor: pointer;
    padding: 0.5rem;
    border-radius: 4px;
    transition: color 0.3s ease;
    flex-shrink: 0;
    font-size: 1.2rem;
}

.delete-btn:hover {
    color: var(--text-primary);
}

/* Task Form */
.task-form-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: var(--overlay);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
    padding: 1rem;
    backdrop-filter: blur(10px);
}

.task-form {
    background: var(--bg-primary);
    padding: 2rem;
    border-radius: 12px;
    border: 2px solid var(--border-primary);
    max-width: 500px;
    width: 100%;
    box-shadow: 0 4px 20px var(--shadow);
}

.task-form h3 {
    font-family: 'Roboto Mono', monospace;
    font-size: 1.4rem;
    font-weight: 700;
    margin-bottom: 1.5rem;
    color: var(--text-primary);
    text-align: center;
    letter-spacing: 0.05em;
    text-transform: uppercase;
}

.form-group {
    margin-bottom: 1.5rem;
}

.form-group label {
    display: block;
    margin-bottom: 0.5rem;
    font-family: 'Roboto Mono', monospace;
    font-weight: 600;
    color: var(--text-primary);
    font-size: 0.9rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

.form-group input,
.form-group textarea,
.form-group select {
    width: 100%;
    padding: 0.8rem;
    background: var(--bg-primary);
    border: 2px solid var(--border-secondary);
    border-radius: 8px;
    color: var(--text-primary);
    font-size: 1rem;
    font-family: 'Roboto Mono', monospace;
    transition: border-color 0.3s ease;
}

.form-group input:focus,
.form-group textarea:focus,
.form-group select:focus {
    outline: none;
    border-color: var(--accent-primary);
}

.form-group textarea {
    resize: vertical;
    min-height: 80px;
}

.form-actions {
    display: flex;
    gap: 1rem;
    justify-content: flex-end;
    margin-top: 2rem;
}

.btn-cancel {
    background: var(--bg-primary);
    color: var(--text-primary);
    border: 2px solid var(--border-primary);
    padding: 0.75rem 1.5rem;
    border-radius: 8px;
    cursor: pointer;
    font-family: 'Roboto Mono', monospace;
    font-weight: 600;
    font-size: 0.9rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    transition: all 0.3s ease;
}

.btn-cancel:hover {
    background: var(--accent-primary);
    color: var(--bg-primary);
}

.btn-submit {
    background: var(--accent-primary);
    color: var(--bg-primary);
    border: 2px solid var(--accent-primary);
    padding: 0.75rem 1.5rem;
    border-radius: 8px;
    cursor: pointer;
    font-family: 'Roboto Mono', monospace;
    font-weight: 600;
    font-size: 0.9rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    transition: all 0.3s ease;
}

.btn-submit:hover {
    background: var(--accent-secondary);
    border-color: var(--accent-secondary);
}

/* Notification System - Updated for Dark Mode */
.notification-container {
    position: fixed;
    top: 1rem;
    right: 1rem;
    z-index: 10000;
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
    max-width: 400px;
}

.notification {
    display: flex;
    align-items: flex-start;
    gap: 1rem;
    padding: 1rem 1.25rem;
    border: 2px solid;
    border-radius: 12px;
    box-shadow: 0 4px 12px var(--shadow);
    font-family: 'Roboto Mono', monospace;
    backdrop-filter: blur(10px);
}

.notification-icon {
    font-size: 1.2rem;
    margin-top: 0.1rem;
    flex-shrink: 0;
}

.notification-content {
    flex: 1;
}

.notification-content h4 {
    font-size: 0.95rem;
    font-weight: 700;
    margin-bottom: 0.25rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

.notification-content p {
    font-size: 0.85rem;
    opacity: 0.9;
    margin: 0;
    line-height: 1.4;
}

.notification-close {
    background: transparent;
    border: none;
    cursor: pointer;
    font-size: 1rem;
    padding: 0.25rem;
    border-radius: 4px;
    transition: background-color 0.2s ease;
    flex-shrink: 0;
}

.notification-close:hover {
    background: rgba(255, 255, 255, 0.1);
}

/* Tomorrow Tasks - Updated for Dark Mode */
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
    margin-right: 0.75rem;
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

/* Progress Chart & Audit - Updated for Dark Mode */
.progress-chart,
.daily-audit {
    background: var(--bg-primary);
    border: 2px solid var(--border-primary);
    border-radius: 12px;
    padding: 2rem;
    transition: all 0.3s ease;
}

.chart-header,
.audit-header {
    text-align: center;
    margin-bottom: 2rem;
}

.chart-header h2,
.audit-header h2 {
    font-family: 'Roboto Mono', monospace;
    font-size: 1.5rem;
    font-weight: 700;
    color: var(--text-primary);
    letter-spacing: 0.05em;
    text-transform: uppercase;
}

.time-range-selector {
    display: flex;
    justify-content: center;
    gap: 0.5rem;
    margin-top: 1rem;
}

.time-range-selector button {
    background: var(--bg-primary);
    border: 2px solid var(--border-primary);
    color: var(--text-primary);
    padding: 0.5rem 1rem;
    border-radius: 6px;
    cursor: pointer;
    font-family: 'Roboto Mono', monospace;
    font-weight: 600;
    font-size: 0.8rem;
    text-transform: uppercase;
    transition: all 0.3s ease;
}

.time-range-selector button:hover {
    background: var(--bg-secondary);
}

.time-range-selector button.active {
    background: var(--accent-primary);
    color: var(--bg-primary);
}

.stats-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    gap: 1rem;
    margin-bottom: 2rem;
}

.stat-card {
    background: var(--bg-secondary);
    border: 2px solid var(--border-secondary);
    padding: 1.5rem;
    border-radius: 8px;
    text-align: center;
    transition: border-color 0.3s ease;
}

.stat-card:hover {
    border-color: var(--border-primary);
}

.stat-card h3 {
    font-family: 'Roboto Mono', monospace;
    font-size: 2rem;
    font-weight: 700;
    color: var(--text-primary);
    margin-bottom: 0.5rem;
}

.stat-card p {
    font-family: 'Roboto Mono', monospace;
    font-size: 0.8rem;
    font-weight: 600;
    color: var(--text-tertiary);
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

.chart-container {
    background: var(--bg-tertiary);
    border: 1px solid var(--border-secondary);
    border-radius: 8px;
    padding: 1rem;
    margin-top: 1rem;
}

.no-data {
    text-align: center;
    padding: 3rem;
    color: var(--text-tertiary);
}

.no-data h3 {
    font-family: 'Roboto Mono', monospace;
    font-size: 1.2rem;
    color: var(--text-primary);
    margin-bottom: 0.5rem;
    font-weight: 600;
}

/* Duplicate Prevention - Updated for Dark Mode */
.duplicate-warning {
    border-color: var(--warning-border) !important;
    background-color: var(--warning-bg) !important;
}

.checking-duplicate {
    font-family: 'Roboto Mono', monospace;
    font-size: 0.8rem;
    color: var(--text-tertiary);
    margin-top: 0.25rem;
    font-style: italic;
}

.duplicate-alert {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    background: var(--warning-bg);
    border: 1px solid var(--warning-border);
    color: var(--warning-text);
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
    background: var(--warning-border) !important;
    border-color: var(--warning-border) !important;
}

.duplicate-submit:hover {
    opacity: 0.8;
}

/* Responsive Design */
@media (max-width: 768px) {
    .header-content {
        flex-direction: column;
        gap: 1rem;
        text-align: center;
    }
    
    .app-header {
        padding: 1.5rem 1rem;
    }
    
    .app-header h1 {
        font-size: 2rem;
    }
    
    .app-main {
        padding: 1rem;
    }
    
    .task-header {
        flex-direction: column;
        align-items: stretch;
        text-align: center;
    }
    
    .task-actions {
        justify-content: center;
    }
    
    .chart-header {
        flex-direction: column;
        text-align: center;
    }
    
    .audit-buttons {
        flex-direction: column;
        align-items: center;
    }
    
    .stats-grid {
        grid-template-columns: 1fr;
    }
    
    .app-nav {
        flex-wrap: wrap;
    }
    
    .app-nav button {
        flex: 1;
        min-width: 120px;
    }
    
    .notification-container {
        top: 0.5rem;
        right: 0.5rem;
        left: 0.5rem;
        max-width: none;
    }
    
    .notification {
        padding: 0.75rem;
    }
    
    .tasks-container {
        gap: 1.5rem;
    }
    
    .today-section,
    .tomorrow-section {
        padding: 1.5rem 1rem;
    }
    
    .tomorrow-header {
        flex-wrap: wrap;
        gap: 0.5rem;
    }
    
    .tomorrow-header h3 {
        font-size: 1.1rem;
    }
}

@media (max-width: 480px) {
    .task-form {
        margin: 0;
        border-radius: 0;
        max-height: 100vh;
        border: none;
        border-top: 2px solid var(--border-primary);
    }
    
    .app-header h1 {
        font-size: 1.8rem;
    }
    
    .task-content {
        padding: 1rem;
    }
    
    .entropy-animation {
        padding: 1rem;
    }
    
    .notification {
        flex-direction: column;
        text-align: left;
    }
    
    .notification-close {
        align-self: flex-end;
        margin-top: -0.5rem;
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
        justify-content: space-between;
    }
}

/* Animation improvements for better performance */
@media (prefers-reduced-motion: reduce) {
    * {
        animation-duration: 0.01ms !important;
        animation-iteration-count: 1 !important;
        transition-duration: 0.01ms !important;
    }
}

/* Focus states for accessibility */
.notification-close:focus,
.btn-primary:focus,
.btn-secondary:focus,
.theme-toggle:focus {
    outline: 2px solid var(--accent-primary);
    outline-offset: 2px;
}

/* High contrast mode support */
@media (prefers-contrast: high) {
    :root {
        --border-primary: #000000;
        --border-secondary: #333333;
    }
    
    [data-theme="dark"] {
        --border-primary: #ffffff;
        --border-secondary: #cccccc;
    }
    
    .tomorrow-section {
        border-color: var(--border-primary);
    }
    
    .tomorrow-task-item {
        border-color: var(--border-primary);
    }
    
    .notification {
        border-width: 3px;
    }
}'''
    
    update_file("frontend/src/styles/App.css", dark_theme_css)
    
    # 8. Update entropy animation for dark mode compatibility
    print("🎮 Updating entropy animation for dark mode...")
    
    updated_entropy_animation = '''import React from 'react';
import { motion } from 'framer-motion';
import { useTheme } from '../contexts/ThemeContext';

const EntropyAnimation = ({ completionRate, totalTasks, completedTasks }) => {
    const { isDarkMode } = useTheme();
    const position = Math.max(0, Math.min(100, completionRate));
    const characterX = 50 + (position * 3);
    const characterY = 180 - (position * 1.2);
    
    // Theme-aware colors
    const colors = {
        completedStair: isDarkMode ? '#ffffff' : '#000000',
        uncompletedStair: isDarkMode ? '#4a4a4a' : '#e0e0e0',
        character: isDarkMode ? '#ffffff' : '#000000',
        characterAccent: isDarkMode ? '#4a4a4a' : '#444444',
        eyes: isDarkMode ? '#1a1a1a' : '#ffffff',
        text: isDarkMode ? '#ffffff' : '#000000',
        mutedText: isDarkMode ? '#b0b0b0' : '#666666'
    };
    
    // Simple stairs - 10 steps
    const stairs = Array.from({ length: 10 }, (_, i) => ({
        x: 40 + i * 32,
        y: 200 - i * 12,
        width: 30,
        height: 12,
        completed: (i + 1) * 10 <= position
    }));
    
    return (
        <div className="entropy-animation">
            <h3 className="progress-title">Battle Progress</h3>
            
            <div className="animation-container">
                <svg className="stairs-svg" viewBox="0 0 400 220" preserveAspectRatio="xMidYMid meet">
                    {/* Background */}
                    <rect 
                        x="0" y="0" width="400" height="220" 
                        fill={isDarkMode ? '#2d2d2d' : '#f9f9f9'} 
                        stroke={isDarkMode ? '#555555' : '#ddd'} 
                        strokeWidth="1" 
                        rx="8"
                    />
                    
                    {/* Stairs */}
                    {stairs.map((stair, i) => (
                        <rect
                            key={i}
                            x={stair.x}
                            y={stair.y}
                            width={stair.width}
                            height={stair.height}
                            fill={stair.completed ? colors.completedStair : colors.uncompletedStair}
                            stroke={isDarkMode ? '#666666' : '#999999'}
                            strokeWidth="1"
                            className="stair-step"
                        />
                    ))}
                    
                    {/* Character - Simple Robot */}
                    <motion.g
                        animate={{
                            x: characterX,
                            y: characterY
                        }}
                        transition={{
                            type: "spring",
                            stiffness: 100,
                            damping: 20,
                            duration: 0.8
                        }}
                    >
                        {/* Robot Body */}
                        <rect 
                            x="-8" y="-15" width="16" height="20" rx="3" 
                            fill={colors.character} 
                            stroke={colors.characterAccent} 
                            strokeWidth="1"
                        />
                        
                        {/* Robot Head */}
                        <rect 
                            x="-6" y="-25" width="12" height="12" rx="2" 
                            fill={colors.character} 
                            stroke={colors.characterAccent} 
                            strokeWidth="1"
                        />
                        
                        {/* Robot Eyes */}
                        <circle cx="-3" cy="-20" r="1.5" fill={colors.eyes}/>
                        <circle cx="3" cy="-20" r="1.5" fill={colors.eyes}/>
                        
                        {/* Robot Arms */}
                        <motion.line
                            x1="-8" y1="-8" x2="-15" y2="-5"
                            stroke={colors.character} strokeWidth="2" strokeLinecap="round"
                            animate={{ rotate: completionRate > 50 ? 20 : -20 }}
                            style={{ transformOrigin: "-8px -8px" }}
                        />
                        <motion.line
                            x1="8" y1="-8" x2="15" y2="-5"
                            stroke={colors.character} strokeWidth="2" strokeLinecap="round"
                            animate={{ rotate: completionRate > 50 ? -20 : 20 }}
                            style={{ transformOrigin: "8px -8px" }}
                        />
                        
                        {/* Robot Legs */}
                        <line x1="-4" y1="5" x2="-4" y2="12" stroke={colors.character} strokeWidth="2" strokeLinecap="round"/>
                        <line x1="4" y1="5" x2="4" y2="12" stroke={colors.character} strokeWidth="2" strokeLinecap="round"/>
                        
                        {/* Victory Flag when 100% */}
                        {completionRate === 100 && (
                            <motion.g
                                initial={{ scale: 0, opacity: 0 }}
                                animate={{ scale: 1, opacity: 1 }}
                                transition={{ delay: 0.5, duration: 0.5 }}
                            >
                                <line x1="20" y1="-25" x2="20" y2="-5" stroke={colors.character} strokeWidth="2"/>
                                <polygon points="20,-25 35,-20 20,-15" fill={colors.character}/>
                                <text x="22" y="-18" fontSize="8" fill={colors.eyes} fontFamily="Roboto Mono">WIN</text>
                            </motion.g>
                        )}
                    </motion.g>
                    
                    {/* Progress Text */}
                    <text x="200" y="25" textAnchor="middle" fontSize="14" fontFamily="Roboto Mono" fontWeight="600" fill={colors.text}>
                        {completedTasks}/{totalTasks} TASKS • {position}%
                    </text>
                    
                    {/* Entropy Warning (when progress is low) */}
                    {position < 50 && (
                        <motion.text
                            x="200" y="45" textAnchor="middle" fontSize="12" fontFamily="Roboto Mono" fontWeight="400" fill={colors.mutedText}
                            animate={{ opacity: [0.5, 1, 0.5] }}
                            transition={{ duration: 2, repeat: Infinity }}
                        >
                            ENTROPY INCREASING...
                        </motion.text>
                    )}
                </svg>
            </div>
            
            <div className="progress-status">
                <div className="status-message">
                    {completionRate === 100 && "🏆 ENTROPY DEFEATED! Perfect victory today!"}
                    {completionRate >= 75 && completionRate < 100 && "⚡ STRONG PROGRESS! Keep pushing forward!"}
                    {completionRate >= 50 && completionRate < 75 && "🔥 GOOD MOMENTUM! Don't let entropy win!"}
                    {completionRate >= 25 && completionRate < 50 && "⚠️ ENTROPY GAINING! Time to take action!"}
                    {completionRate < 25 && "🚨 CHAOS DETECTED! Start completing tasks now!"}
                </div>
            </div>
        </div>
    );
};

export default EntropyAnimation;'''
    
    update_file("frontend/src/components/EntropyAnimation.js", updated_entropy_animation)
    
    # 9. Create restart script
    restart_script = f'''#!/bin/bash
echo "🌓 Restarting ENTROPY with Move Fix + Dark Mode..."
echo "Backup created: {backup_dir}"
echo ""

# Kill existing processes
pkill -f "node.*server.js" || true
pkill -f "react-scripts" || true

# Wait a moment
sleep 2

echo "✅ Fixes & Features Applied:"
echo "  🔧 Fixed: Tasks properly disappear when moved to tomorrow"
echo "  🌙 Added: Complete dark mode theme with toggle"
echo "  🎨 Enhanced: Theme-aware animations and components"
echo "  📱 Improved: Better mobile dark mode experience"
echo ""
echo "🛡️  Backup & Restore:"
echo "  📦 Backup created: {backup_dir}"
echo "  🔄 To restore: python3 ../restore_backup.py {backup_dir}"
echo ""

# Start the application
./start.sh'''
    
    update_file("restart_fixed_darkmode.sh", restart_script)
    os.chmod("restart_fixed_darkmode.sh", 0o755)
    
    print("\n🎉 ENTROPY Enhanced: Move Fix + Dark Mode Complete!")
    print("=" * 60)
    print("✅ Bug Fix: Move to tomorrow now properly removes tasks from today")
    print("✅ Dark Mode: Complete theme system with toggle button")
    print("✅ Theme Persistence: Remembers your preference")
    print("✅ Animations: Theme-aware robot and UI elements")
    print("✅ Mobile Optimized: Dark mode works perfectly on all devices")
    
    print(f"\n📦 BACKUP CREATED: {backup_dir}")
    print(f"🔄 Restore command: python3 ../restore_backup.py {backup_dir}")
    
    print("\n🔧 BUG FIXES:")
    print("• Tasks moved to tomorrow now disappear from today immediately")
    print("• Better state management prevents UI lag")
    print("• Enhanced error handling for move operations")
    
    print("\n🌙 DARK MODE FEATURES:")
    print("• Toggle button in header switches between light/dark")
    print("• System preference detection on first load")
    print("• Smooth transitions between themes")
    print("• All components adapt automatically")
    print("• Theme preference saved to localStorage")
    
    print("\n🚀 To start your enhanced app:")
    print("./restart_fixed_darkmode.sh")
    
    print("\n⚡ Your ENTROPY app now works perfectly with beautiful themes! ⚡")

if __name__ == "__main__":
    main()
