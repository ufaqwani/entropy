#!/usr/bin/env python3
"""
ENTROPY - Fix Tomorrow Tasks & Custom Notifications Script
Adds Tomorrow section and replaces ugly alerts with beautiful notifications
"""

import os
import re

def update_file(file_path, content):
    """Update file with given content"""
    with open(file_path, 'w') as f:
        f.write(content)
    print(f"✅ Updated: {file_path}")

def main():
    print("🔧 ENTROPY - Fixing Tomorrow Tasks & Custom Notifications")
    print("=" * 60)
    
    # Check if we're in the right directory
    if not os.path.exists("backend") or not os.path.exists("frontend"):
        print("❌ Please run this script from the entropy-app directory")
        return
    
    # 1. Update backend tasks route to include tomorrow's tasks
    print("📅 Updating backend to handle tomorrow's tasks...")
    
    updated_tasks_route = '''const express = require('express');
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
            date: { $gte: today, $lt: tomorrow }
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

// Move uncompleted tasks to tomorrow - IMPROVED
router.post('/move-to-tomorrow', async (req, res) => {
    try {
        const today = new Date();
        today.setHours(0, 0, 0, 0);
        const tomorrow = new Date(today);
        tomorrow.setDate(tomorrow.getDate() + 1);
        
        const uncompletedTasks = await Task.find({
            date: { $gte: today, $lt: tomorrow },
            completed: false
        });
        
        if (uncompletedTasks.length === 0) {
            return res.json({ 
                movedCount: 0, 
                message: 'No uncompleted tasks to move',
                tasks: [] 
            });
        }
        
        const movedTasks = [];
        for (let task of uncompletedTasks) {
            const newTask = new Task({
                title: task.title,
                description: task.description,
                priority: task.priority,
                date: tomorrow
            });
            await newTask.save();
            movedTasks.push(newTask);
            
            // Mark original as moved (optional: delete or mark as moved)
            await Task.findByIdAndUpdate(task._id, { moved: true });
        }
        
        res.json({ 
            movedCount: movedTasks.length, 
            tasks: movedTasks,
            message: `Successfully moved ${movedTasks.length} task${movedTasks.length !== 1 ? 's' : ''} to tomorrow`
        });
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

module.exports = router;'''
    
    update_file("backend/routes/tasks.js", updated_tasks_route)
    
    # 2. Create custom notification system
    print("🔔 Creating custom notification system...")
    
    notification_component = '''import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { FiCheck, FiInfo, FiAlertTriangle, FiX } from 'react-icons/fi';

const NotificationSystem = ({ notifications, removeNotification }) => {
    const getIcon = (type) => {
        switch (type) {
            case 'success': return <FiCheck />;
            case 'warning': return <FiAlertTriangle />;
            case 'error': return <FiX />;
            default: return <FiInfo />;
        }
    };

    const getColors = (type) => {
        switch (type) {
            case 'success': 
                return { bg: '#f0f8f0', border: '#4caf50', text: '#2e7d32' };
            case 'warning': 
                return { bg: '#fff8e1', border: '#ff9800', text: '#ef6c00' };
            case 'error': 
                return { bg: '#ffebee', border: '#f44336', text: '#c62828' };
            default: 
                return { bg: '#e3f2fd', border: '#2196f3', text: '#1565c0' };
        }
    };

    return (
        <div className="notification-container">
            <AnimatePresence>
                {notifications.map((notification) => {
                    const colors = getColors(notification.type);
                    
                    return (
                        <motion.div
                            key={notification.id}
                            initial={{ opacity: 0, y: -50, scale: 0.9 }}
                            animate={{ opacity: 1, y: 0, scale: 1 }}
                            exit={{ opacity: 0, y: -20, scale: 0.9 }}
                            transition={{ duration: 0.3 }}
                            className="notification"
                            style={{
                                backgroundColor: colors.bg,
                                borderColor: colors.border,
                                color: colors.text
                            }}
                        >
                            <div className="notification-icon">
                                {getIcon(notification.type)}
                            </div>
                            
                            <div className="notification-content">
                                <h4>{notification.title}</h4>
                                {notification.message && (
                                    <p>{notification.message}</p>
                                )}
                            </div>
                            
                            <button
                                className="notification-close"
                                onClick={() => removeNotification(notification.id)}
                                style={{ color: colors.text }}
                            >
                                <FiX />
                            </button>
                        </motion.div>
                    );
                })}
            </AnimatePresence>
        </div>
    );
};

// Hook to manage notifications
export const useNotifications = () => {
    const [notifications, setNotifications] = useState([]);

    const addNotification = (title, message = '', type = 'info', duration = 4000) => {
        const id = Date.now() + Math.random();
        const notification = { id, title, message, type };
        
        setNotifications(prev => [...prev, notification]);
        
        // Auto remove after duration
        setTimeout(() => {
            removeNotification(id);
        }, duration);
        
        return id;
    };

    const removeNotification = (id) => {
        setNotifications(prev => prev.filter(n => n.id !== id));
    };

    const clearAllNotifications = () => {
        setNotifications([]);
    };

    return {
        notifications,
        addNotification,
        removeNotification,
        clearAllNotifications
    };
};

export default NotificationSystem;'''
    
    update_file("frontend/src/components/NotificationSystem.js", notification_component)
    
    # 3. Create TomorrowTasks component
    print("📋 Creating Tomorrow tasks component...")
    
    tomorrow_tasks_component = '''import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { FiClock, FiArrowRight, FiCalendar } from 'react-icons/fi';

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
                            className="tomorrow-task-item"
                        >
                            <div className="task-preview">
                                <div 
                                    className="priority-indicator"
                                    style={{ backgroundColor: priorityConfig[task.priority].color }}
                                ></div>
                                
                                <div className="task-content">
                                    <h5>{task.title}</h5>
                                    {task.description && (
                                        <p className="task-description">{task.description}</p>
                                    )}
                                </div>
                                
                                <div className="task-meta">
                                    <span className="priority-label">
                                        {priorityConfig[task.priority].label}
                                    </span>
                                    <FiClock className="time-icon" />
                                </div>
                            </div>
                        </motion.div>
                    ))}
                </AnimatePresence>
            </div>
        </div>
    );
};

export default TomorrowTasks;'''
    
    update_file("frontend/src/components/TomorrowTasks.js", tomorrow_tasks_component)
    
    # 4. Update main App.js to include notifications and tomorrow tasks
    print("🔄 Updating main App component...")
    
    updated_app_js = '''import React, { useState, useEffect } from 'react';
import axios from 'axios';
import TaskList from './components/TaskList';
import TaskForm from './components/TaskForm';
import TomorrowTasks from './components/TomorrowTasks';
import ProgressChart from './components/ProgressChart';
import EntropyAnimation from './components/EntropyAnimation';
import DailyAudit from './components/DailyAudit';
import CompletedTasksHistory from './components/CompletedTasksHistory';
import NotificationSystem, { useNotifications } from './components/NotificationSystem';
import './styles/App.css';

function App() {
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
            addNotification(
                'Failed to Add Task', 
                'There was an error adding your task. Please try again.', 
                'error'
            );
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
    };

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
                addNotification(
                    'Tasks Moved Successfully! 📅', 
                    response.data.message, 
                    'success',
                    5000 // Show for 5 seconds
                );
                
                // Refresh the task lists to show updated data
                loadTasks();
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
                <h1>⚡ ENTROPY</h1>
                <p>Fight chaos. Complete tasks. Win the day.</p>
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

export default App;'''
    
    update_file("frontend/src/App.js", updated_app_js)
    
    # 5. Add CSS styles for notifications and tomorrow section
    print("🎨 Adding styles for notifications and tomorrow section...")
    
    additional_css = '''
/* Notification System Styles */
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
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
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
    background: rgba(0, 0, 0, 0.1);
}

/* Tasks Container Layout */
.tasks-container {
    display: flex;
    flex-direction: column;
    gap: 2rem;
}

.today-section {
    background: #ffffff;
    border: 2px solid #000000;
    border-radius: 12px;
    padding: 2rem;
}

.tomorrow-section {
    background: #f8f8f8;
    border: 2px solid #e0e0e0;
    border-radius: 12px;
    padding: 1.5rem;
}

/* Tomorrow Tasks Styles */
.tomorrow-tasks {
    width: 100%;
}

.tomorrow-header {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    margin-bottom: 1rem;
    padding-bottom: 0.75rem;
    border-bottom: 2px solid #e0e0e0;
}

.tomorrow-icon {
    color: #666666;
    font-size: 1.2rem;
}

.tomorrow-header h3 {
    font-family: 'Roboto Mono', monospace;
    font-size: 1.3rem;
    font-weight: 700;
    color: #000000;
    letter-spacing: 0.05em;
    text-transform: uppercase;
    flex: 1;
}

.task-count {
    background: #e0e0e0;
    color: #000000;
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
    background: #ffffff;
    border: 1px solid #ddd;
    border-radius: 8px;
    padding: 1rem;
    transition: all 0.3s ease;
}

.tomorrow-task-item:hover {
    border-color: #000000;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.task-preview {
    display: flex;
    align-items: center;
    gap: 1rem;
}

.priority-indicator {
    width: 4px;
    height: 40px;
    border-radius: 2px;
    flex-shrink: 0;
}

.tomorrow-task-item .task-content {
    flex: 1;
}

.tomorrow-task-item .task-content h5 {
    font-family: 'Roboto Mono', monospace;
    font-size: 1rem;
    font-weight: 600;
    color: #000000;
    margin-bottom: 0.25rem;
}

.tomorrow-task-item .task-description {
    font-family: 'Roboto Mono', monospace;
    font-size: 0.85rem;
    color: #666666;
    margin: 0;
}

.tomorrow-task-item .task-meta {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    flex-shrink: 0;
}

.priority-label {
    font-family: 'Roboto Mono', monospace;
    font-size: 0.75rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: #666666;
}

.time-icon {
    color: #999999;
    font-size: 0.9rem;
}

.tomorrow-empty {
    text-align: center;
    padding: 2rem;
    color: #666666;
}

.empty-icon {
    font-size: 2rem;
    color: #cccccc;
    margin-bottom: 1rem;
}

.tomorrow-empty h4 {
    font-family: 'Roboto Mono', monospace;
    font-size: 1rem;
    font-weight: 600;
    color: #000000;
    margin-bottom: 0.5rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

.tomorrow-empty p {
    font-family: 'Roboto Mono', monospace;
    font-size: 0.9rem;
    color: #666666;
}

/* Responsive Design for New Components */
@media (max-width: 768px) {
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

/* Animation improvements */
@keyframes slideInRight {
    from {
        opacity: 0;
        transform: translateX(20px);
    }
    to {
        opacity: 1;
        transform: translateX(0);
    }
}

.tomorrow-task-item {
    animation: slideInRight 0.3s ease-out;
}

/* Focus states for accessibility */
.notification-close:focus,
.btn-primary:focus,
.btn-secondary:focus {
    outline: 2px solid #000000;
    outline-offset: 2px;
}

/* High contrast mode support */
@media (prefers-contrast: high) {
    .tomorrow-section {
        background: #ffffff;
        border-color: #000000;
    }
    
    .tomorrow-task-item {
        border-color: #000000;
    }
    
    .notification {
        border-width: 3px;
    }
}'''
    
    # Append to existing CSS
    with open("frontend/src/styles/App.css", 'a') as f:
        f.write(additional_css)
    
    print("✅ Added notification and tomorrow section styles")
    
    # 6. Create restart script
    restart_script = '''#!/bin/bash
echo "🔄 Restarting ENTROPY with Tomorrow Tasks & Custom Notifications..."

# Kill existing processes
pkill -f "node.*server.js" || true
pkill -f "react-scripts" || true

# Wait a moment
sleep 2

echo "✅ New Features Added:"
echo "  📅 Tomorrow tasks section shows moved tasks"
echo "  🔔 Beautiful in-app notifications replace ugly alerts"
echo "  🎯 Better task organization and feedback"
echo ""

# Start the application
./start.sh'''
    
    update_file("restart_tomorrow_fix.sh", restart_script)
    os.chmod("restart_tomorrow_fix.sh", 0o755)
    
    print("\n🎉 Tomorrow Tasks & Custom Notifications Fixed!")
    print("=" * 55)
    print("✅ Backend: Updated to handle today + tomorrow tasks")
    print("✅ Frontend: Added tomorrow tasks section")  
    print("✅ Notifications: Custom in-app notification system")
    print("✅ UI/UX: No more ugly browser alerts!")
    print("✅ Layout: Clean separation of today vs tomorrow")
    print("\n🔧 Fixes Applied:")
    print("• Tomorrow tasks now appear in a dedicated section")
    print("• Beautiful toast notifications replace alert() calls")
    print("• Better visual feedback for all user actions")
    print("• Moved tasks are immediately visible")
    print("\n🚀 To see the improvements:")
    print("./restart_tomorrow_fix.sh")
    print("\n⚡ Now you can see exactly where your moved tasks go! ⚡")

if __name__ == "__main__":
    main()
