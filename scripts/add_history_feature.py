#!/usr/bin/env python3
"""
ENTROPY - Add Task Completion History Feature Script
Automatically updates your existing ENTROPY app to track completed tasks history
"""

import os
import json
import re
from pathlib import Path

def update_file(file_path, content, mode='w'):
    """Update file with given content"""
    with open(file_path, mode) as f:
        f.write(content)
    print(f"✅ Updated: {file_path}")

def insert_after_line(file_path, search_line, new_content):
    """Insert new content after a specific line in file"""
    with open(file_path, 'r') as f:
        lines = f.readlines()
    
    for i, line in enumerate(lines):
        if search_line in line:
            lines.insert(i + 1, new_content + '\n')
            break
    
    with open(file_path, 'w') as f:
        f.writelines(lines)

def main():
    print("🔧 Adding Task Completion History Feature to ENTROPY")
    print("=" * 55)
    
    # Check if we're in the right directory
    if not os.path.exists("backend") or not os.path.exists("frontend"):
        print("❌ Please run this script from the entropy-app directory")
        print("   Run: cd entropy-app && python3 ../add_history_feature.py")
        return
    
    # 1. Create completed tasks route
    print("📁 Creating completed tasks API route...")
    
    completed_tasks_route = '''const express = require('express');
const router = express.Router();
const Task = require('../models/Task');

// Get completed tasks with completion timestamps (history)
router.get('/completed/history', async (req, res) => {
    try {
        const days = parseInt(req.query.days) || 30; // default 30 days
        const startDate = new Date();
        startDate.setDate(startDate.getDate() - days);
        startDate.setHours(0, 0, 0, 0);

        const completedTasks = await Task.find({
            completed: true,
            completedAt: { $gte: startDate }
        }).sort({ completedAt: -1 });

        // Group by date for better organization
        const groupedTasks = completedTasks.reduce((acc, task) => {
            const date = task.completedAt ? 
                task.completedAt.toISOString().split('T')[0] : 
                task.createdAt.toISOString().split('T');
            
            if (!acc[date]) {
                acc[date] = [];
            }
            acc[date].push(task);
            return acc;
        }, {});

        res.json({
            tasks: completedTasks,
            grouped: groupedTasks,
            totalCount: completedTasks.length
        });
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// Get completion stats
router.get('/completed/stats', async (req, res) => {
    try {
        const days = parseInt(req.query.days) || 30;
        const startDate = new Date();
        startDate.setDate(startDate.getDate() - days);
        startDate.setHours(0, 0, 0, 0);

        const completedTasks = await Task.find({
            completed: true,
            completedAt: { $gte: startDate }
        });

        const stats = {
            totalCompleted: completedTasks.length,
            avgPerDay: (completedTasks.length / days).toFixed(1),
            byPriority: {
                high: completedTasks.filter(t => t.priority === 1).length,
                medium: completedTasks.filter(t => t.priority === 2).length,
                low: completedTasks.filter(t => t.priority === 3).length
            }
        };

        res.json(stats);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

module.exports = router;'''
    
    update_file("backend/routes/completedTasks.js", completed_tasks_route)
    
    # 2. Update server.js to include the new route
    print("🔧 Updating backend server...")
    
    with open("backend/server.js", 'r') as f:
        server_content = f.read()
    
    # Add import if not already present
    if "completedTasksRoutes" not in server_content:
        server_content = server_content.replace(
            "const progressRoutes = require('./routes/progress');",
            "const progressRoutes = require('./routes/progress');\nconst completedTasksRoutes = require('./routes/completedTasks');"
        )
        
        # Add route usage
        server_content = server_content.replace(
            "app.use('/api/progress', progressRoutes);",
            "app.use('/api/progress', progressRoutes);\napp.use('/api/tasks', completedTasksRoutes);"
        )
    
    update_file("backend/server.js", server_content)
    
    # 3. Create the CompletedTasksHistory React component
    print("🎨 Creating React history component...")
    
    history_component = '''import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { FiClock, FiCalendar, FiCheck, FiAlertTriangle, FiTrendingUp } from 'react-icons/fi';
import { format, isToday, isYesterday, parseISO } from 'date-fns';
import axios from 'axios';

const CompletedTasksHistory = () => {
    const [historyData, setHistoryData] = useState({ tasks: [], grouped: {}, totalCount: 0 });
    const [stats, setStats] = useState(null);
    const [loading, setLoading] = useState(true);
    const [timeRange, setTimeRange] = useState(30);

    const priorityConfig = {
        1: { label: 'High', icon: FiAlertTriangle, color: '#e74c3c' },
        2: { label: 'Medium', icon: FiClock, color: '#f39c12' },
        3: { label: 'Low', icon: FiCheck, color: '#27ae60' }
    };

    useEffect(() => {
        loadHistoryData();
        loadStats();
    }, [timeRange]);

    const loadHistoryData = async () => {
        try {
            setLoading(true);
            const response = await axios.get(`/api/tasks/completed/history?days=${timeRange}`);
            setHistoryData(response.data);
        } catch (error) {
            console.error('Error loading history:', error);
        } finally {
            setLoading(false);
        }
    };

    const loadStats = async () => {
        try {
            const response = await axios.get(`/api/tasks/completed/stats?days=${timeRange}`);
            setStats(response.data);
        } catch (error) {
            console.error('Error loading stats:', error);
        }
    };

    const formatDateGroup = (dateKey) => {
        try {
            const date = parseISO(dateKey);
            if (isToday(date)) return 'Today';
            if (isYesterday(date)) return 'Yesterday';
            return format(date, 'MMMM d, yyyy');
        } catch {
            return dateKey;
        }
    };

    const formatTime = (dateString) => {
        try {
            return format(parseISO(dateString), 'h:mm a');
        } catch {
            return 'Unknown time';
        }
    };

    if (loading) {
        return (
            <div className="loading-container">
                <div className="loading-spinner"></div>
                <p>Loading your victory history...</p>
            </div>
        );
    }

    return (
        <div className="completed-tasks-history">
            <div className="history-header">
                <h2>🏆 Victory History</h2>
                <p>Your completed battles against entropy</p>
                
                <div className="time-range-selector">
                    {[7, 30, 90].map(days => (
                        <button
                            key={days}
                            className={timeRange === days ? 'active' : ''}
                            onClick={() => setTimeRange(days)}
                        >
                            {days} days
                        </button>
                    ))}
                </div>
            </div>

            {stats && (
                <div className="history-stats">
                    <div className="stat-card">
                        <h3>{historyData.totalCount}</h3>
                        <p>Tasks Completed</p>
                        <FiCheck className="stat-icon" />
                    </div>
                    <div className="stat-card">
                        <h3>{stats.avgPerDay}</h3>
                        <p>Avg Per Day</p>
                        <FiTrendingUp className="stat-icon" />
                    </div>
                    <div className="stat-card">
                        <h3>{stats.byPriority.high}</h3>
                        <p>High Priority</p>
                        <FiAlertTriangle className="stat-icon" />
                    </div>
                    <div className="stat-card">
                        <h3>{Object.keys(historyData.grouped).length}</h3>
                        <p>Active Days</p>
                        <FiCalendar className="stat-icon" />
                    </div>
                </div>
            )}

            {historyData.totalCount === 0 ? (
                <div className="no-data">
                    <h3>🌱 No completed tasks yet</h3>
                    <p>Start completing tasks to build your victory history!</p>
                    <div className="motivational-quote">
                        <em>"Every task completed is a victory against chaos."</em>
                    </div>
                </div>
            ) : (
                <div className="history-timeline">
                    <AnimatePresence>
                        {Object.keys(historyData.grouped)
                            .sort((a, b) => new Date(b) - new Date(a))
                            .map((dateKey, groupIndex) => (
                                <motion.div 
                                    key={dateKey}
                                    className="date-group"
                                    initial={{ opacity: 0, y: 30 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    transition={{ duration: 0.4, delay: groupIndex * 0.1 }}
                                >
                                    <div className="date-header">
                                        <FiCalendar className="date-icon" />
                                        <h3>{formatDateGroup(dateKey)}</h3>
                                        <span className="task-count">
                                            {historyData.grouped[dateKey].length} task{historyData.grouped[dateKey].length !== 1 ? 's' : ''}
                                        </span>
                                    </div>
                                    
                                    <div className="tasks-list">
                                        {historyData.grouped[dateKey].map((task, index) => {
                                            const PriorityIcon = priorityConfig[task.priority].icon;
                                            return (
                                                <motion.div 
                                                    key={task._id}
                                                    className="completed-task-item"
                                                    initial={{ opacity: 0, x: -30 }}
                                                    animate={{ opacity: 1, x: 0 }}
                                                    transition={{ delay: (groupIndex * 0.1) + (index * 0.05) }}
                                                    whileHover={{ scale: 1.02 }}
                                                >
                                                    <div className="task-check">
                                                        <FiCheck />
                                                    </div>
                                                    
                                                    <div className="task-content">
                                                        <h4>{task.title}</h4>
                                                        {task.description && (
                                                            <p className="task-description">{task.description}</p>
                                                        )}
                                                    </div>
                                                    
                                                    <div className="task-meta">
                                                        <div 
                                                            className="priority-badge"
                                                            style={{ backgroundColor: priorityConfig[task.priority].color }}
                                                        >
                                                            <PriorityIcon size={12} />
                                                            <span>{priorityConfig[task.priority].label}</span>
                                                        </div>
                                                        
                                                        <div className="completion-time">
                                                            <FiClock size={12} />
                                                            <span>{task.completedAt ? formatTime(task.completedAt) : 'Unknown'}</span>
                                                        </div>
                                                    </div>
                                                </motion.div>
                                            );
                                        })}
                                    </div>
                                </motion.div>
                            ))}
                    </AnimatePresence>
                </div>
            )}
        </div>
    );
};

export default CompletedTasksHistory;'''
    
    update_file("frontend/src/components/CompletedTasksHistory.js", history_component)
    
    # 4. Update App.js to include the new component
    print("🔄 Updating main App component...")
    
    with open("frontend/src/App.js", 'r') as f:
        app_content = f.read()
    
    # Add import if not present
    if "CompletedTasksHistory" not in app_content:
        app_content = app_content.replace(
            "import DailyAudit from './components/DailyAudit';",
            "import DailyAudit from './components/DailyAudit';\nimport CompletedTasksHistory from './components/CompletedTasksHistory';"
        )
    
    # Add navigation button
    if "History" not in app_content:
        nav_addition = '''                <button 
                    className={currentView === 'history' ? 'active' : ''}
                    onClick={() => setCurrentView('history')}
                >
                    History
                </button>'''
        
        app_content = app_content.replace(
            '''                <button 
                    className={currentView === 'progress' ? 'active' : ''}
                    onClick={() => setCurrentView('progress')}
                >
                    Progress
                </button>''',
            nav_addition + '''
                <button 
                    className={currentView === 'progress' ? 'active' : ''}
                    onClick={() => setCurrentView('progress')}
                >
                    Progress
                </button>'''
        )
    
    # Add history view to main content
    if "currentView === 'history'" not in app_content:
        history_view = '''
                {currentView === 'history' && (
                    <CompletedTasksHistory />
                )}'''
        
        app_content = app_content.replace(
            "                {currentView === 'progress' && (",
            history_view + "\n\n                {currentView === 'progress' && ("
        )
    
    update_file("frontend/src/App.js", app_content)
    
    # 5. Add CSS styles for the history component
    print("🎨 Adding history component styles...")
    
    history_css = '''
/* Completed Tasks History Styles */
.completed-tasks-history {
    background: rgba(0, 0, 0, 0.2);
    border-radius: 12px;
    padding: 2rem;
    border: 1px solid rgba(255, 255, 255, 0.1);
}

.history-header {
    text-align: center;
    margin-bottom: 2rem;
}

.history-header h2 {
    font-size: 1.8rem;
    font-weight: 600;
    margin-bottom: 0.5rem;
    background: linear-gradient(45deg, #27ae60, #2ecc71);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.history-header p {
    opacity: 0.8;
    margin-bottom: 1.5rem;
    font-size: 1.1rem;
}

.history-stats {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
    gap: 1.5rem;
    margin-bottom: 2rem;
}

.stat-card {
    background: rgba(255, 255, 255, 0.05);
    padding: 1.5rem;
    border-radius: 12px;
    text-align: center;
    border: 1px solid rgba(255, 255, 255, 0.1);
    position: relative;
    transition: all 0.3s ease;
}

.stat-card:hover {
    background: rgba(255, 255, 255, 0.08);
    border-color: rgba(39, 174, 96, 0.3);
    transform: translateY(-2px);
}

.stat-card h3 {
    font-size: 2rem;
    font-weight: 700;
    color: #27ae60;
    margin-bottom: 0.5rem;
}

.stat-card p {
    font-size: 0.9rem;
    opacity: 0.8;
    margin-bottom: 0.5rem;
}

.stat-icon {
    color: #27ae60;
    opacity: 0.3;
    position: absolute;
    top: 1rem;
    right: 1rem;
    font-size: 1.2rem;
}

.history-timeline {
    max-height: 70vh;
    overflow-y: auto;
    padding-right: 0.5rem;
}

.history-timeline::-webkit-scrollbar {
    width: 8px;
}

.history-timeline::-webkit-scrollbar-track {
    background: rgba(255, 255, 255, 0.1);
    border-radius: 4px;
}

.history-timeline::-webkit-scrollbar-thumb {
    background: rgba(39, 174, 96, 0.5);
    border-radius: 4px;
}

.date-group {
    margin-bottom: 2rem;
    border-left: 3px solid rgba(39, 174, 96, 0.3);
    padding-left: 1.5rem;
    position: relative;
}

.date-group::before {
    content: '';
    position: absolute;
    left: -6px;
    top: 0;
    width: 12px;
    height: 12px;
    background: #27ae60;
    border-radius: 50%;
    box-shadow: 0 0 0 4px rgba(26, 26, 46, 1);
}

.date-header {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    margin-bottom: 1rem;
    padding: 0.75rem 1rem;
    background: rgba(39, 174, 96, 0.1);
    border-radius: 8px;
    border: 1px solid rgba(39, 174, 96, 0.2);
}

.date-icon {
    color: #27ae60;
    font-size: 1.1rem;
}

.date-header h3 {
    font-size: 1.2rem;
    font-weight: 600;
    color: #27ae60;
    flex-grow: 1;
}

.task-count {
    background: rgba(39, 174, 96, 0.2);
    color: #27ae60;
    padding: 0.25rem 0.75rem;
    border-radius: 12px;
    font-size: 0.8rem;
    font-weight: 500;
    border: 1px solid rgba(39, 174, 96, 0.3);
}

.tasks-list {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
    margin-left: 1rem;
}

.completed-task-item {
    background: rgba(39, 174, 96, 0.05);
    border: 1px solid rgba(39, 174, 96, 0.2);
    border-radius: 10px;
    padding: 1.25rem;
    display: flex;
    align-items: center;
    gap: 1rem;
    transition: all 0.3s ease;
    position: relative;
    overflow: hidden;
}

.completed-task-item::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    width: 4px;
    height: 100%;
    background: #27ae60;
}

.completed-task-item:hover {
    background: rgba(39, 174, 96, 0.1);
    border-color: rgba(39, 174, 96, 0.4);
    box-shadow: 0 4px 12px rgba(39, 174, 96, 0.15);
}

.task-check {
    background: #27ae60;
    color: white;
    width: 28px;
    height: 28px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
    font-size: 0.9rem;
    box-shadow: 0 2px 6px rgba(39, 174, 96, 0.3);
}

.completed-task-item .task-content {
    flex: 1;
}

.completed-task-item .task-content h4 {
    font-size: 1.1rem;
    margin-bottom: 0.25rem;
    color: #ffffff;
    font-weight: 500;
}

.completed-task-item .task-description {
    font-size: 0.85rem;
    opacity: 0.7;
    margin: 0;
    line-height: 1.4;
}

.task-meta {
    display: flex;
    flex-direction: column;
    align-items: flex-end;
    gap: 0.5rem;
    flex-shrink: 0;
}

.priority-badge {
    display: flex;
    align-items: center;
    gap: 0.25rem;
    padding: 0.25rem 0.5rem;
    border-radius: 6px;
    font-size: 0.75rem;
    font-weight: 600;
    color: white;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.2);
}

.priority-badge span {
    font-size: 0.7rem;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.completion-time {
    display: flex;
    align-items: center;
    gap: 0.25rem;
    font-size: 0.8rem;
    opacity: 0.7;
    background: rgba(255, 255, 255, 0.05);
    padding: 0.25rem 0.5rem;
    border-radius: 4px;
}

.no-data {
    text-align: center;
    padding: 4rem 2rem;
    opacity: 0.8;
}

.no-data h3 {
    font-size: 1.5rem;
    margin-bottom: 1rem;
    color: #27ae60;
}

.no-data p {
    font-size: 1.1rem;
    margin-bottom: 1.5rem;
}

.motivational-quote {
    background: rgba(39, 174, 96, 0.1);
    border-left: 4px solid #27ae60;
    padding: 1rem 1.5rem;
    border-radius: 8px;
    font-style: italic;
    color: #27ae60;
    max-width: 400px;
    margin: 0 auto;
}

/* Responsive Design */
@media (max-width: 768px) {
    .history-stats {
        grid-template-columns: repeat(2, 1fr);
        gap: 1rem;
    }
    
    .stat-card {
        padding: 1rem;
    }
    
    .stat-card h3 {
        font-size: 1.5rem;
    }
    
    .completed-task-item {
        flex-direction: column;
        align-items: stretch;
        text-align: left;
        padding: 1rem;
    }
    
    .task-meta {
        flex-direction: row;
        justify-content: space-between;
        align-items: center;
        margin-top: 0.5rem;
    }
    
    .tasks-list {
        margin-left: 0;
    }
    
    .date-group {
        padding-left: 1rem;
    }
    
    .history-timeline {
        max-height: 60vh;
    }
}

@media (max-width: 480px) {
    .history-stats {
        grid-template-columns: 1fr;
    }
    
    .completed-tasks-history {
        padding: 1rem;
    }
    
    .date-header {
        flex-wrap: wrap;
        gap: 0.5rem;
    }
    
    .task-count {
        flex-shrink: 0;
    }
}'''
    
    # Append the CSS to the existing styles
    with open("frontend/src/styles/App.css", 'a') as f:
        f.write(history_css)
    
    print("✅ Added history component styles")
    
    # 6. Create a simple restart script
    restart_script = '''#!/bin/bash
echo "🔄 Restarting ENTROPY with new History feature..."

# Kill existing processes
pkill -f "node.*server.js" || true
pkill -f "react-scripts" || true

# Wait a moment
sleep 2

# Start the application
./start.sh'''
    
    update_file("restart.sh", restart_script)
    os.chmod("restart.sh", 0o755)
    
    print("\n🎉 Task Completion History feature added successfully!")
    print("=" * 55)
    print("✅ Backend: Added completed tasks API routes")
    print("✅ Frontend: Added CompletedTasksHistory component")
    print("✅ UI: Added History tab to navigation")
    print("✅ Styling: Added beautiful timeline styles")
    print("\n🚀 To use the new feature:")
    print("1. Restart your app: ./restart.sh")
    print("2. Complete some tasks to generate history")
    print("3. Click the 'History' tab to see your completed tasks!")
    print("\n⚡ Now you can track every victory against entropy! ⚡")

if __name__ == "__main__":
    main()
