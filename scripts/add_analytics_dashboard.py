#!/usr/bin/env python3
"""
ENTROPY - Advanced Analytics Dashboard
Professional productivity insights with charts and trends analysis
"""

import os
import shutil
import json
from datetime import datetime

def create_backup():
    """Create backup before adding analytics"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = f"../entropy_backup_analytics_{timestamp}"
    
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
    os.makedirs(os.path.dirname(file_path) if os.path.dirname(file_path) else '.', exist_ok=True)
    with open(file_path, 'w') as f:
        f.write(content)
    print(f"✅ Updated: {file_path}")

def main():
    print("📊 ENTROPY - Advanced Analytics Dashboard")
    print("=" * 45)
    print("🎯 Professional productivity insights & trends")
    print("📈 Beautiful charts with completion analytics")
    print("")
    
    # Check if we're in the right directory
    if not os.path.exists("backend") or not os.path.exists("frontend"):
        print("❌ Please run this script from the entropy-app directory")
        return
    
    # Create backup
    backup_dir = create_backup()
    if not backup_dir:
        print("❌ Cannot proceed without backup.")
        return
    
    print("📊 Creating Analytics API endpoints...")
    
    # 1. Create Analytics API routes
    analytics_routes = '''const express = require('express');
const router = express.Router();
const Task = require('../models/Task');
const Category = require('../models/Category');

// Helper function for 5 AM day boundaries
function getDayBoundaries(referenceDate = new Date()) {
    const current = new Date(referenceDate);
    
    const todayStart = new Date(current);
    todayStart.setHours(5, 0, 0, 0);
    
    if (current.getHours() < 5) {
        todayStart.setDate(todayStart.getDate() - 1);
    }
    
    const tomorrowStart = new Date(todayStart);
    tomorrowStart.setDate(tomorrowStart.getDate() + 1);
    
    return { todayStart, tomorrowStart };
}

// Get comprehensive analytics overview
router.get('/overview', async (req, res) => {
    try {
        const now = new Date();
        const { todayStart } = getDayBoundaries(now);
        
        // Calculate date ranges
        const weekStart = new Date(todayStart);
        weekStart.setDate(weekStart.getDate() - 7);
        
        const monthStart = new Date(todayStart);
        monthStart.setDate(monthStart.getDate() - 30);
        
        // Total statistics
        const totalTasks = await Task.countDocuments({
            $or: [{ deleted: { $exists: false } }, { deleted: false }]
        });
        
        const totalCompleted = await Task.countDocuments({
            completed: true,
            $or: [{ deleted: { $exists: false } }, { deleted: false }]
        });
        
        // Today's stats
        const todayTasks = await Task.countDocuments({
            date: { $gte: todayStart },
            $or: [{ deleted: { $exists: false } }, { deleted: false }]
        });
        
        const todayCompleted = await Task.countDocuments({
            date: { $gte: todayStart },
            completed: true,
            $or: [{ deleted: { $exists: false } }, { deleted: false }]
        });
        
        // Weekly stats
        const weeklyTasks = await Task.countDocuments({
            date: { $gte: weekStart },
            $or: [{ deleted: { $exists: false } }, { deleted: false }]
        });
        
        const weeklyCompleted = await Task.countDocuments({
            date: { $gte: weekStart },
            completed: true,
            $or: [{ deleted: { $exists: false } }, { deleted: false }]
        });
        
        // Monthly stats
        const monthlyTasks = await Task.countDocuments({
            date: { $gte: monthStart },
            $or: [{ deleted: { $exists: false } }, { deleted: false }]
        });
        
        const monthlyCompleted = await Task.countDocuments({
            date: { $gte: monthStart },
            completed: true,
            $or: [{ deleted: { $exists: false } }, { deleted: false }]
        });
        
        // Calculate completion rates
        const todayCompletionRate = todayTasks === 0 ? 0 : Math.round((todayCompleted / todayTasks) * 100);
        const weeklyCompletionRate = weeklyTasks === 0 ? 0 : Math.round((weeklyCompleted / weeklyTasks) * 100);
        const monthlyCompletionRate = monthlyTasks === 0 ? 0 : Math.round((monthlyCompleted / monthlyTasks) * 100);
        const overallCompletionRate = totalTasks === 0 ? 0 : Math.round((totalCompleted / totalTasks) * 100);
        
        res.json({
            overview: {
                totalTasks,
                totalCompleted,
                overallCompletionRate
            },
            periods: {
                today: {
                    tasks: todayTasks,
                    completed: todayCompleted,
                    completionRate: todayCompletionRate
                },
                weekly: {
                    tasks: weeklyTasks,
                    completed: weeklyCompleted,
                    completionRate: weeklyCompletionRate
                },
                monthly: {
                    tasks: monthlyTasks,
                    completed: monthlyCompleted,
                    completionRate: monthlyCompletionRate
                }
            }
        });
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// Get category breakdown analytics
router.get('/categories', async (req, res) => {
    try {
        const categories = await Category.find({ isActive: true });
        
        const categoryStats = await Promise.all(
            categories.map(async (category) => {
                const totalTasks = await Task.countDocuments({ 
                    category: category._id,
                    $or: [{ deleted: { $exists: false } }, { deleted: false }]
                });
                
                const completedTasks = await Task.countDocuments({ 
                    category: category._id,
                    completed: true,
                    $or: [{ deleted: { $exists: false } }, { deleted: false }]
                });
                
                const pendingTasks = totalTasks - completedTasks;
                const completionRate = totalTasks === 0 ? 0 : Math.round((completedTasks / totalTasks) * 100);
                
                // Priority breakdown
                const priorityBreakdown = await Task.aggregate([
                    {
                        $match: {
                            category: category._id,
                            $or: [{ deleted: { $exists: false } }, { deleted: false }]
                        }
                    },
                    {
                        $group: {
                            _id: '$priority',
                            total: { $sum: 1 },
                            completed: { 
                                $sum: { $cond: ['$completed', 1, 0] } 
                            }
                        }
                    },
                    { $sort: { _id: 1 } }
                ]);
                
                return {
                    categoryId: category._id,
                    categoryName: category.name,
                    categoryColor: category.color,
                    categoryIcon: category.icon,
                    totalTasks,
                    completedTasks,
                    pendingTasks,
                    completionRate,
                    priorityBreakdown
                };
            })
        );
        
        // Sort by total tasks descending
        categoryStats.sort((a, b) => b.totalTasks - a.totalTasks);
        
        res.json(categoryStats);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// Get daily trends (last 7 days)
router.get('/trends/daily', async (req, res) => {
    try {
        const trends = [];
        const today = new Date();
        
        for (let i = 6; i >= 0; i--) {
            const date = new Date(today);
            date.setDate(date.getDate() - i);
            
            const { todayStart, tomorrowStart } = getDayBoundaries(date);
            
            const tasksCreated = await Task.countDocuments({
                date: { $gte: todayStart, $lt: tomorrowStart },
                $or: [{ deleted: { $exists: false } }, { deleted: false }]
            });
            
            const tasksCompleted = await Task.countDocuments({
                date: { $gte: todayStart, $lt: tomorrowStart },
                completed: true,
                $or: [{ deleted: { $exists: false } }, { deleted: false }]
            });
            
            const completionRate = tasksCreated === 0 ? 0 : Math.round((tasksCompleted / tasksCreated) * 100);
            
            trends.push({
                date: todayStart.toISOString().split('T')[0],
                dateLabel: todayStart.toLocaleDateString('en-US', { 
                    month: 'short', 
                    day: 'numeric' 
                }),
                tasksCreated,
                tasksCompleted,
                completionRate
            });
        }
        
        res.json(trends);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// Get productivity patterns
router.get('/patterns', async (req, res) => {
    try {
        const now = new Date();
        const monthStart = new Date(now);
        monthStart.setDate(monthStart.getDate() - 30);
        
        // Priority distribution
        const priorityStats = await Task.aggregate([
            {
                $match: {
                    date: { $gte: monthStart },
                    $or: [{ deleted: { $exists: false } }, { deleted: false }]
                }
            },
            {
                $group: {
                    _id: '$priority',
                    total: { $sum: 1 },
                    completed: { 
                        $sum: { $cond: ['$completed', 1, 0] } 
                    }
                }
            },
            { $sort: { _id: 1 } }
        ]);
        
        const priorityLabels = { 1: 'High', 2: 'Medium', 3: 'Low' };
        const priorityColors = { 1: '#ff6b6b', 2: '#ffd93d', 3: '#6bcf7f' };
        
        const priorityData = priorityStats.map(stat => ({
            priority: stat._id,
            label: priorityLabels[stat._id] || 'Unknown',
            color: priorityColors[stat._id] || '#gray',
            total: stat.total,
            completed: stat.completed,
            completionRate: stat.total === 0 ? 0 : Math.round((stat.completed / stat.total) * 100)
        }));
        
        // Completion streaks
        const recentCompletions = await Task.find({
            completed: true,
            completedAt: { $exists: true },
            $or: [{ deleted: { $exists: false } }, { deleted: false }]
        })
        .sort({ completedAt: -1 })
        .limit(100)
        .select('completedAt');
        
        const streakData = calculateCompletionStreaks(recentCompletions);
        
        // Most productive categories
        const productiveCategories = await Task.aggregate([
            {
                $match: {
                    date: { $gte: monthStart },
                    completed: true,
                    $or: [{ deleted: { $exists: false } }, { deleted: false }]
                }
            },
            {
                $group: {
                    _id: '$category',
                    completedCount: { $sum: 1 }
                }
            },
            {
                $lookup: {
                    from: 'categories',
                    localField: '_id',
                    foreignField: '_id',
                    as: 'category'
                }
            },
            { $unwind: '$category' },
            {
                $project: {
                    categoryName: '$category.name',
                    categoryIcon: '$category.icon',
                    categoryColor: '$category.color',
                    completedCount: 1
                }
            },
            { $sort: { completedCount: -1 } },
            { $limit: 5 }
        ]);
        
        res.json({
            priorityDistribution: priorityData,
            completionStreaks: streakData,
            productiveCategories
        });
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// Helper function to calculate completion streaks
function calculateCompletionStreaks(completions) {
    if (!completions || completions.length === 0) {
        return {
            currentStreak: 0,
            longestStreak: 0,
            totalCompletions: 0
        };
    }
    
    const dates = completions.map(c => {
        const date = new Date(c.completedAt);
        return date.toISOString().split('T')[0];
    });
    
    const uniqueDates = [...new Set(dates)].sort().reverse();
    
    let currentStreak = 0;
    let longestStreak = 0;
    let tempStreak = 1;
    
    const today = new Date().toISOString().split('T')[0];
    
    // Calculate current streak
    if (uniqueDates === today) {
        currentStreak = 1;
        for (let i = 1; i < uniqueDates.length; i++) {
            const prevDate = new Date(uniqueDates[i-1]);
            const currDate = new Date(uniqueDates[i]);
            const diffTime = Math.abs(prevDate - currDate);
            const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
            
            if (diffDays === 1) {
                currentStreak++;
            } else {
                break;
            }
        }
    }
    
    // Calculate longest streak
    for (let i = 1; i < uniqueDates.length; i++) {
        const prevDate = new Date(uniqueDates[i-1]);
        const currDate = new Date(uniqueDates[i]);
        const diffTime = Math.abs(prevDate - currDate);
        const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
        
        if (diffDays === 1) {
            tempStreak++;
        } else {
            longestStreak = Math.max(longestStreak, tempStreak);
            tempStreak = 1;
        }
    }
    
    longestStreak = Math.max(longestStreak, tempStreak);
    
    return {
        currentStreak,
        longestStreak,
        totalCompletions: completions.length,
        uniqueDays: uniqueDates.length
    };
}

module.exports = router;'''
    
    update_file("backend/routes/analytics.js", analytics_routes)
    
    print("🔧 Updating server to include analytics routes...")
    
    # 2. Update server.js to include analytics routes
    try:
        with open("backend/server.js", 'r') as f:
            server_content = f.read()
        
        # Add analytics routes import
        if "analyticsRoutes" not in server_content:
            server_content = server_content.replace(
                "const templateRoutes = require('./routes/templates');",
                "const templateRoutes = require('./routes/templates');\nconst analyticsRoutes = require('./routes/analytics');"
            )
            
            # Add analytics routes usage
            server_content = server_content.replace(
                "app.use('/api/templates', templateRoutes);",
                "app.use('/api/templates', templateRoutes);\napp.use('/api/analytics', analyticsRoutes);"
            )
        
        update_file("backend/server.js", server_content)
        
    except Exception as e:
        print(f"⚠️ Could not automatically update server.js: {e}")
    
    print("📊 Creating Analytics Dashboard component...")
    
    # 3. Create Analytics Dashboard component
    analytics_dashboard = '''import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
    FiTrendingUp, FiTarget, FiAward, FiCalendar, 
    FiBarChart2, FiPieChart, FiActivity, FiStar 
} from 'react-icons/fi';
import {
    Chart as ChartJS,
    CategoryScale,
    LinearScale,
    BarElement,
    Title,
    Tooltip,
    Legend,
    ArcElement,
    PointElement,
    LineElement,
} from 'chart.js';
import { Bar, Doughnut, Line } from 'react-chartjs-2';
import axios from 'axios';

ChartJS.register(
    CategoryScale,
    LinearScale,
    BarElement,
    Title,
    Tooltip,
    Legend,
    ArcElement,
    PointElement,
    LineElement
);

const AnalyticsDashboard = () => {
    const [overview, setOverview] = useState(null);
    const [categories, setCategories] = useState([]);
    const [trends, setTrends] = useState([]);
    const [patterns, setPatterns] = useState(null);
    const [loading, setLoading] = useState(true);
    const [activeTab, setActiveTab] = useState('overview');

    useEffect(() => {
        loadAnalyticsData();
    }, []);

    const loadAnalyticsData = async () => {
        try {
            setLoading(true);
            const [overviewRes, categoriesRes, trendsRes, patternsRes] = await Promise.all([
                axios.get('/api/analytics/overview'),
                axios.get('/api/analytics/categories'),
                axios.get('/api/analytics/trends/daily'),
                axios.get('/api/analytics/patterns')
            ]);
            
            setOverview(overviewRes.data);
            setCategories(categoriesRes.data);
            setTrends(trendsRes.data);
            setPatterns(patternsRes.data);
        } catch (error) {
            console.error('Error loading analytics:', error);
        } finally {
            setLoading(false);
        }
    };

    if (loading) {
        return (
            <div className="analytics-loading">
                <div className="loading-spinner"></div>
                <p>Loading analytics...</p>
            </div>
        );
    }

    if (!overview) {
        return (
            <div className="analytics-error">
                <h3>Analytics Unavailable</h3>
                <p>Unable to load analytics data. Please try again later.</p>
            </div>
        );
    }

    return (
        <div className="analytics-dashboard">
            <div className="analytics-header">
                <h1>📊 Analytics Dashboard</h1>
                <p>Your productivity insights and performance trends</p>
            </div>

            <div className="analytics-tabs">
                <button 
                    className={`tab ${activeTab === 'overview' ? 'active' : ''}`}
                    onClick={() => setActiveTab('overview')}
                >
                    <FiBarChart2 /> Overview
                </button>
                <button 
                    className={`tab ${activeTab === 'categories' ? 'active' : ''}`}
                    onClick={() => setActiveTab('categories')}
                >
                    <FiPieChart /> Categories
                </button>
                <button 
                    className={`tab ${activeTab === 'trends' ? 'active' : ''}`}
                    onClick={() => setActiveTab('trends')}
                >
                    <FiTrendingUp /> Trends
                </button>
                <button 
                    className={`tab ${activeTab === 'patterns' ? 'active' : ''}`}
                    onClick={() => setActiveTab('patterns')}
                >
                    <FiActivity /> Patterns
                </button>
            </div>

            <div className="analytics-content">
                <AnimatePresence mode="wait">
                    {activeTab === 'overview' && (
                        <OverviewTab key="overview" overview={overview} />
                    )}
                    {activeTab === 'categories' && (
                        <CategoriesTab key="categories" categories={categories} />
                    )}
                    {activeTab === 'trends' && (
                        <TrendsTab key="trends" trends={trends} />
                    )}
                    {activeTab === 'patterns' && (
                        <PatternsTab key="patterns" patterns={patterns} />
                    )}
                </AnimatePresence>
            </div>
        </div>
    );
};

// Overview Tab Component
const OverviewTab = ({ overview }) => {
    const statCards = [
        {
            title: 'Total Tasks',
            value: overview.overview.totalTasks,
            icon: <FiCalendar />,
            color: '#3b82f6'
        },
        {
            title: 'Completed',
            value: overview.overview.totalCompleted,
            icon: <FiTarget />,
            color: '#10b981'
        },
        {
            title: 'Overall Rate',
            value: `${overview.overview.overallCompletionRate}%`,
            icon: <FiTrendingUp />,
            color: '#8b5cf6'
        }
    ];

    const periodData = {
        labels: ['Today', 'This Week', 'This Month'],
        datasets: [
            {
                label: 'Tasks Created',
                data: [
                    overview.periods.today.tasks,
                    overview.periods.weekly.tasks,
                    overview.periods.monthly.tasks
                ],
                backgroundColor: 'rgba(59, 130, 246, 0.5)',
                borderColor: 'rgba(59, 130, 246, 1)',
                borderWidth: 2
            },
            {
                label: 'Tasks Completed',
                data: [
                    overview.periods.today.completed,
                    overview.periods.weekly.completed,
                    overview.periods.monthly.completed
                ],
                backgroundColor: 'rgba(16, 185, 129, 0.5)',
                borderColor: 'rgba(16, 185, 129, 1)',
                borderWidth: 2
            }
        ]
    };

    const chartOptions = {
        responsive: true,
        plugins: {
            legend: {
                position: 'top',
            },
            title: {
                display: true,
                text: 'Task Performance Overview'
            },
        },
        scales: {
            y: {
                beginAtZero: true,
                ticks: {
                    stepSize: 1
                }
            }
        }
    };

    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="overview-tab"
        >
            <div className="stats-grid">
                {statCards.map((stat, index) => (
                    <motion.div
                        key={stat.title}
                        className="stat-card"
                        initial={{ opacity: 0, scale: 0.9 }}
                        animate={{ opacity: 1, scale: 1 }}
                        transition={{ delay: index * 0.1 }}
                    >
                        <div 
                            className="stat-icon"
                            style={{ backgroundColor: stat.color }}
                        >
                            {stat.icon}
                        </div>
                        <div className="stat-content">
                            <h3>{stat.value}</h3>
                            <p>{stat.title}</p>
                        </div>
                    </motion.div>
                ))}
            </div>

            <div className="period-comparison">
                <h3>Period Comparison</h3>
                <div className="period-stats">
                    <div className="period-item">
                        <h4>Today</h4>
                        <div className="period-data">
                            <span className="completion-rate">{overview.periods.today.completionRate}%</span>
                            <span className="tasks-info">
                                {overview.periods.today.completed}/{overview.periods.today.tasks} completed
                            </span>
                        </div>
                    </div>
                    <div className="period-item">
                        <h4>This Week</h4>
                        <div className="period-data">
                            <span className="completion-rate">{overview.periods.weekly.completionRate}%</span>
                            <span className="tasks-info">
                                {overview.periods.weekly.completed}/{overview.periods.weekly.tasks} completed
                            </span>
                        </div>
                    </div>
                    <div className="period-item">
                        <h4>This Month</h4>
                        <div className="period-data">
                            <span className="completion-rate">{overview.periods.monthly.completionRate}%</span>
                            <span className="tasks-info">
                                {overview.periods.monthly.completed}/{overview.periods.monthly.tasks} completed
                            </span>
                        </div>
                    </div>
                </div>
            </div>

            <div className="chart-section">
                <Bar data={periodData} options={chartOptions} />
            </div>
        </motion.div>
    );
};

// Categories Tab Component
const CategoriesTab = ({ categories }) => {
    if (!categories || categories.length === 0) {
        return (
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                className="no-data"
            >
                <h3>No Category Data Available</h3>
                <p>Create some tasks to see category analytics</p>
            </motion.div>
        );
    }

    const categoryData = {
        labels: categories.map(cat => cat.categoryName),
        datasets: [{
            data: categories.map(cat => cat.totalTasks),
            backgroundColor: categories.map(cat => cat.categoryColor),
            borderColor: '#ffffff',
            borderWidth: 2
        }]
    };

    const chartOptions = {
        responsive: true,
        plugins: {
            legend: {
                position: 'right',
            },
            title: {
                display: true,
                text: 'Tasks Distribution by Category'
            },
        },
    };

    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="categories-tab"
        >
            <div className="categories-chart">
                <Doughnut data={categoryData} options={chartOptions} />
            </div>

            <div className="categories-breakdown">
                <h3>Category Performance</h3>
                <div className="categories-list">
                    {categories.map((category, index) => (
                        <motion.div
                            key={category.categoryId}
                            className="category-item"
                            initial={{ opacity: 0, x: -20 }}
                            animate={{ opacity: 1, x: 0 }}
                            transition={{ delay: index * 0.1 }}
                        >
                            <div className="category-header">
                                <span 
                                    className="category-icon"
                                    style={{ backgroundColor: category.categoryColor }}
                                >
                                    {category.categoryIcon}
                                </span>
                                <h4>{category.categoryName}</h4>
                                <span className="completion-badge">
                                    {category.completionRate}%
                                </span>
                            </div>
                            
                            <div className="category-stats">
                                <div className="stat">
                                    <span className="label">Total:</span>
                                    <span className="value">{category.totalTasks}</span>
                                </div>
                                <div className="stat">
                                    <span className="label">Completed:</span>
                                    <span className="value">{category.completedTasks}</span>
                                </div>
                                <div className="stat">
                                    <span className="label">Pending:</span>
                                    <span className="value">{category.pendingTasks}</span>
                                </div>
                            </div>
                            
                            <div className="progress-bar">
                                <div 
                                    className="progress-fill"
                                    style={{ 
                                        width: `${category.completionRate}%`,
                                        backgroundColor: category.categoryColor 
                                    }}
                                ></div>
                            </div>
                        </motion.div>
                    ))}
                </div>
            </div>
        </motion.div>
    );
};

// Trends Tab Component
const TrendsTab = ({ trends }) => {
    if (!trends || trends.length === 0) {
        return (
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                className="no-data"
            >
                <h3>No Trend Data Available</h3>
                <p>Use the app for a few days to see trends</p>
            </motion.div>
        );
    }

    const trendsData = {
        labels: trends.map(t => t.dateLabel),
        datasets: [
            {
                label: 'Tasks Created',
                data: trends.map(t => t.tasksCreated),
                borderColor: 'rgba(59, 130, 246, 1)',
                backgroundColor: 'rgba(59, 130, 246, 0.1)',
                tension: 0.4,
                fill: true
            },
            {
                label: 'Tasks Completed',
                data: trends.map(t => t.tasksCompleted),
                borderColor: 'rgba(16, 185, 129, 1)',
                backgroundColor: 'rgba(16, 185, 129, 0.1)',
                tension: 0.4,
                fill: true
            }
        ]
    };

    const chartOptions = {
        responsive: true,
        plugins: {
            legend: {
                position: 'top',
            },
            title: {
                display: true,
                text: '7-Day Productivity Trend'
            },
        },
        scales: {
            y: {
                beginAtZero: true,
                ticks: {
                    stepSize: 1
                }
            }
        }
    };

    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="trends-tab"
        >
            <div className="trends-chart">
                <Line data={trendsData} options={chartOptions} />
            </div>

            <div className="trends-summary">
                <h3>Weekly Summary</h3>
                <div className="trends-grid">
                    {trends.map((day, index) => (
                        <div key={day.date} className="trend-day">
                            <h4>{day.dateLabel}</h4>
                            <div className="day-stats">
                                <span className="tasks-created">{day.tasksCreated} created</span>
                                <span className="tasks-completed">{day.tasksCompleted} completed</span>
                                <span className="completion-rate">{day.completionRate}% rate</span>
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        </motion.div>
    );
};

// Patterns Tab Component
const PatternsTab = ({ patterns }) => {
    if (!patterns) {
        return (
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                className="no-data"
            >
                <h3>No Pattern Data Available</h3>
                <p>Complete more tasks to see patterns</p>
            </motion.div>
        );
    }

    const priorityData = {
        labels: patterns.priorityDistribution.map(p => p.label),
        datasets: [{
            data: patterns.priorityDistribution.map(p => p.total),
            backgroundColor: patterns.priorityDistribution.map(p => p.color),
            borderColor: '#ffffff',
            borderWidth: 2
        }]
    };

    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="patterns-tab"
        >
            <div className="patterns-grid">
                <div className="pattern-section">
                    <h3>Priority Distribution</h3>
                    <div className="priority-chart">
                        <Doughnut data={priorityData} />
                    </div>
                </div>

                <div className="pattern-section">
                    <h3>Completion Streaks</h3>
                    <div className="streaks-info">
                        <div className="streak-item">
                            <FiTarget className="streak-icon" />
                            <div>
                                <span className="streak-value">{patterns.completionStreaks.currentStreak}</span>
                                <span className="streak-label">Current Streak</span>
                            </div>
                        </div>
                        <div className="streak-item">
                            <FiAward className="streak-icon" />
                            <div>
                                <span className="streak-value">{patterns.completionStreaks.longestStreak}</span>
                                <span className="streak-label">Longest Streak</span>
                            </div>
                        </div>
                        <div className="streak-item">
                            <FiStar className="streak-icon" />
                            <div>
                                <span className="streak-value">{patterns.completionStreaks.totalCompletions}</span>
                                <span className="streak-label">Total Completed</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <div className="productive-categories">
                <h3>Most Productive Categories</h3>
                <div className="productive-list">
                    {patterns.productiveCategories.map((category, index) => (
                        <div key={category._id} className="productive-item">
                            <span className="rank">#{index + 1}</span>
                            <span 
                                className="category-icon"
                                style={{ backgroundColor: category.categoryColor }}
                            >
                                {category.categoryIcon}
                            </span>
                            <span className="category-name">{category.categoryName}</span>
                            <span className="completion-count">{category.completedCount} completed</span>
                        </div>
                    ))}
                </div>
            </div>
        </motion.div>
    );
};

export default AnalyticsDashboard;'''
    
    update_file("frontend/src/components/AnalyticsDashboard.js", analytics_dashboard)
    
    print("📦 Installing Chart.js dependencies...")
    
    # 4. Update frontend package.json to include chart.js
    try:
        with open("frontend/package.json", 'r') as f:
            package_data = json.load(f)
        
        dependencies_to_add = {
            "chart.js": "^4.4.0",
            "react-chartjs-2": "^5.2.0"
        }
        
        for dep, version in dependencies_to_add.items():
            if dep not in package_data.get("dependencies", {}):
                package_data.setdefault("dependencies", {})[dep] = version
        
        with open("frontend/package.json", 'w') as f:
            json.dump(package_data, f, indent=2)
        
        print("✅ Added Chart.js dependencies to package.json")
    except Exception as e:
        print(f"⚠️ Could not update package.json: {e}")
    
    print("🔄 Updating main App component to include analytics...")
    
    # 5. Update App.js to include analytics dashboard
    try:
        with open("frontend/src/App.js", 'r') as f:
            app_content = f.read()
        
        # Add AnalyticsDashboard import
        if "AnalyticsDashboard" not in app_content:
            app_content = app_content.replace(
                "import TemplateManager from './components/TemplateManager';",
                "import TemplateManager from './components/TemplateManager';\nimport AnalyticsDashboard from './components/AnalyticsDashboard';"
            )
        
        # Add Analytics to navigation
        if "analytics" not in app_content:
            app_content = app_content.replace(
                '''                <button 
                    className={currentView === 'audit' ? 'active' : ''}
                    onClick={() => setCurrentView('audit')}
                >
                    Daily Audit
                </button>''',
                '''                <button 
                    className={currentView === 'analytics' ? 'active' : ''}
                    onClick={() => setCurrentView('analytics')}
                >
                    Analytics
                </button>
                <button 
                    className={currentView === 'audit' ? 'active' : ''}
                    onClick={() => setCurrentView('audit')}
                >
                    Daily Audit
                </button>'''
            )
        
        # Add AnalyticsDashboard to main content
        if "currentView === 'analytics'" not in app_content:
            app_content = app_content.replace(
                '''{currentView === 'audit' && (
                    <DailyAudit 
                        progressData={progressData}
                        onAuditComplete={loadTodaysProgress}
                    />
                )}''',
                '''{currentView === 'analytics' && <AnalyticsDashboard />}
                
                {currentView === 'audit' && (
                    <DailyAudit 
                        progressData={progressData}
                        onAuditComplete={loadTodaysProgress}
                    />
                )}'''
            )
        
        update_file("frontend/src/App.js", app_content)
        
    except Exception as e:
        print(f"⚠️ Could not automatically update App.js: {e}")
    
    print("🎨 Adding comprehensive CSS for analytics dashboard...")
    
    # 6. Add CSS for analytics dashboard
    analytics_css = '''
/* Analytics Dashboard Styles */
.analytics-dashboard {
    padding: 2rem;
    max-width: 1200px;
    margin: 0 auto;
}

.analytics-header {
    text-align: center;
    margin-bottom: 2rem;
}

.analytics-header h1 {
    font-family: 'Roboto Mono', monospace;
    font-size: 2rem;
    font-weight: 700;
    color: var(--text-primary);
    margin-bottom: 0.5rem;
    text-transform: uppercase;
    letter-spacing: 0.1em;
}

.analytics-header p {
    color: var(--text-secondary);
    font-size: 1.1rem;
}

.analytics-loading,
.analytics-error {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 4rem;
    text-align: center;
}

.analytics-loading p,
.analytics-error p {
    color: var(--text-tertiary);
    margin-top: 1rem;
}

/* Analytics Tabs */
.analytics-tabs {
    display: flex;
    justify-content: center;
    margin-bottom: 2rem;
    background: var(--bg-secondary);
    border-radius: 8px;
    padding: 0.5rem;
    border: 1px solid var(--border-secondary);
}

.analytics-tabs .tab {
    background: transparent;
    border: none;
    padding: 0.75rem 1.5rem;
    border-radius: 6px;
    cursor: pointer;
    font-family: 'Roboto Mono', monospace;
    font-weight: 600;
    font-size: 0.9rem;
    color: var(--text-secondary);
    transition: all 0.3s ease;
    display: flex;
    align-items: center;
    gap: 0.5rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

.analytics-tabs .tab:hover {
    background: var(--bg-tertiary);
    color: var(--text-primary);
}

.analytics-tabs .tab.active {
    background: var(--accent-primary);
    color: var(--bg-primary);
}

.analytics-content {
    min-height: 500px;
}

/* Overview Tab */
.overview-tab {
    display: flex;
    flex-direction: column;
    gap: 2rem;
}

.stats-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 1.5rem;
}

.stat-card {
    background: var(--bg-secondary);
    border: 1px solid var(--border-secondary);
    border-radius: 12px;
    padding: 1.5rem;
    display: flex;
    align-items: center;
    gap: 1rem;
    transition: all 0.3s ease;
}

.stat-card:hover {
    border-color: var(--border-primary);
    box-shadow: 0 4px 12px var(--shadow);
}

.stat-icon {
    width: 60px;
    height: 60px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    font-size: 1.5rem;
    flex-shrink: 0;
}

.stat-content h3 {
    font-family: 'Roboto Mono', monospace;
    font-size: 2rem;
    font-weight: 700;
    color: var(--text-primary);
    margin-bottom: 0.25rem;
}

.stat-content p {
    color: var(--text-secondary);
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    font-size: 0.9rem;
}

.period-comparison {
    background: var(--bg-secondary);
    border: 1px solid var(--border-secondary);
    border-radius: 12px;
    padding: 1.5rem;
}

.period-comparison h3 {
    font-family: 'Roboto Mono', monospace;
    font-size: 1.2rem;
    font-weight: 600;
    color: var(--text-primary);
    margin-bottom: 1rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

.period-stats {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1rem;
}

.period-item {
    background: var(--bg-primary);
    border: 1px solid var(--border-tertiary);
    border-radius: 8px;
    padding: 1rem;
    text-align: center;
}

.period-item h4 {
    font-family: 'Roboto Mono', monospace;
    color: var(--text-primary);
    margin-bottom: 0.5rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

.period-data {
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
}

.completion-rate {
    font-family: 'Roboto Mono', monospace;
    font-size: 1.5rem;
    font-weight: 700;
    color: var(--accent-primary);
}

.tasks-info {
    font-size: 0.8rem;
    color: var(--text-tertiary);
}

.chart-section {
    background: var(--bg-primary);
    border: 1px solid var(--border-secondary);
    border-radius: 12px;
    padding: 1.5rem;
}

/* Categories Tab */
.categories-tab {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 2rem;
}

.categories-chart {
    background: var(--bg-secondary);
    border: 1px solid var(--border-secondary);
    border-radius: 12px;
    padding: 1.5rem;
    display: flex;
    align-items: center;
    justify-content: center;
}

.categories-breakdown {
    background: var(--bg-secondary);
    border: 1px solid var(--border-secondary);
    border-radius: 12px;
    padding: 1.5rem;
}

.categories-breakdown h3 {
    font-family: 'Roboto Mono', monospace;
    font-size: 1.2rem;
    font-weight: 600;
    color: var(--text-primary);
    margin-bottom: 1rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

.categories-list {
    display: flex;
    flex-direction: column;
    gap: 1rem;
}

.category-item {
    background: var(--bg-primary);
    border: 1px solid var(--border-tertiary);
    border-radius: 8px;
    padding: 1rem;
}

.category-header {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    margin-bottom: 0.5rem;
}

.category-item .category-icon {
    width: 32px;
    height: 32px;
    border-radius: 6px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    font-size: 1rem;
    flex-shrink: 0;
}

.category-item h4 {
    font-family: 'Roboto Mono', monospace;
    color: var(--text-primary);
    font-weight: 600;
    flex: 1;
}

.completion-badge {
    background: var(--success-bg);
    color: var(--success-text);
    border: 1px solid var(--success-border);
    padding: 0.25rem 0.5rem;
    border-radius: 4px;
    font-family: 'Roboto Mono', monospace;
    font-size: 0.8rem;
    font-weight: 700;
}

.category-stats {
    display: flex;
    gap: 1rem;
    margin-bottom: 0.5rem;
}

.category-stats .stat {
    display: flex;
    gap: 0.25rem;
    font-family: 'Roboto Mono', monospace;
    font-size: 0.8rem;
}

.category-stats .label {
    color: var(--text-tertiary);
}

.category-stats .value {
    color: var(--text-primary);
    font-weight: 600;
}

.progress-bar {
    width: 100%;
    height: 6px;
    background: var(--bg-tertiary);
    border-radius: 3px;
    overflow: hidden;
}

.progress-fill {
    height: 100%;
    border-radius: 3px;
    transition: width 0.3s ease;
}

/* Trends Tab */
.trends-tab {
    display: flex;
    flex-direction: column;
    gap: 2rem;
}

.trends-chart {
    background: var(--bg-secondary);
    border: 1px solid var(--border-secondary);
    border-radius: 12px;
    padding: 1.5rem;
}

.trends-summary {
    background: var(--bg-secondary);
    border: 1px solid var(--border-secondary);
    border-radius: 12px;
    padding: 1.5rem;
}

.trends-summary h3 {
    font-family: 'Roboto Mono', monospace;
    font-size: 1.2rem;
    font-weight: 600;
    color: var(--text-primary);
    margin-bottom: 1rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

.trends-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
    gap: 1rem;
}

.trend-day {
    background: var(--bg-primary);
    border: 1px solid var(--border-tertiary);
    border-radius: 8px;
    padding: 1rem;
    text-align: center;
}

.trend-day h4 {
    font-family: 'Roboto Mono', monospace;
    color: var(--text-primary);
    margin-bottom: 0.5rem;
    font-size: 0.9rem;
    font-weight: 600;
}

.day-stats {
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
}

.day-stats span {
    font-family: 'Roboto Mono', monospace;
    font-size: 0.75rem;
    color: var(--text-tertiary);
}

/* Patterns Tab */
.patterns-tab {
    display: flex;
    flex-direction: column;
    gap: 2rem;
}

.patterns-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 2rem;
}

.pattern-section {
    background: var(--bg-secondary);
    border: 1px solid var(--border-secondary);
    border-radius: 12px;
    padding: 1.5rem;
}

.pattern-section h3 {
    font-family: 'Roboto Mono', monospace;
    font-size: 1.2rem;
    font-weight: 600;
    color: var(--text-primary);
    margin-bottom: 1rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    text-align: center;
}

.priority-chart {
    display: flex;
    justify-content: center;
    max-height: 300px;
}

.streaks-info {
    display: flex;
    flex-direction: column;
    gap: 1rem;
}

.streak-item {
    display: flex;
    align-items: center;
    gap: 1rem;
    background: var(--bg-primary);
    border: 1px solid var(--border-tertiary);
    border-radius: 8px;
    padding: 1rem;
}

.streak-icon {
    font-size: 1.5rem;
    color: var(--accent-primary);
}

.streak-value {
    display: block;
    font-family: 'Roboto Mono', monospace;
    font-size: 1.5rem;
    font-weight: 700;
    color: var(--text-primary);
}

.streak-label {
    display: block;
    font-size: 0.8rem;
    color: var(--text-tertiary);
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

.productive-categories {
    background: var(--bg-secondary);
    border: 1px solid var(--border-secondary);
    border-radius: 12px;
    padding: 1.5rem;
}

.productive-categories h3 {
    font-family: 'Roboto Mono', monospace;
    font-size: 1.2rem;
    font-weight: 600;
    color: var(--text-primary);
    margin-bottom: 1rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

.productive-list {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
}

.productive-item {
    display: flex;
    align-items: center;
    gap: 1rem;
    background: var(--bg-primary);
    border: 1px solid var(--border-tertiary);
    border-radius: 8px;
    padding: 0.75rem;
}

.productive-item .rank {
    font-family: 'Roboto Mono', monospace;
    font-weight: 700;
    color: var(--accent-primary);
    min-width: 30px;
}

.productive-item .category-icon {
    width: 24px;
    height: 24px;
    border-radius: 4px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    font-size: 0.9rem;
    flex-shrink: 0;
}

.productive-item .category-name {
    font-family: 'Roboto Mono', monospace;
    color: var(--text-primary);
    font-weight: 600;
    flex: 1;
}

.productive-item .completion-count {
    font-family: 'Roboto Mono', monospace;
    color: var(--text-tertiary);
    font-size: 0.8rem;
}

.no-data {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 4rem;
    text-align: center;
    background: var(--bg-secondary);
    border: 1px solid var(--border-secondary);
    border-radius: 12px;
}

.no-data h3 {
    font-family: 'Roboto Mono', monospace;
    color: var(--text-primary);
    margin-bottom: 0.5rem;
}

.no-data p {
    color: var(--text-tertiary);
}

/* Mobile responsive */
@media (max-width: 768px) {
    .analytics-dashboard {
        padding: 1rem;
    }
    
    .analytics-tabs {
        flex-direction: column;
        gap: 0.5rem;
    }
    
    .analytics-tabs .tab {
        justify-content: center;
        padding: 1rem;
    }
    
    .stats-grid {
        grid-template-columns: 1fr;
    }
    
    .period-stats {
        grid-template-columns: 1fr;
    }
    
    .categories-tab {
        grid-template-columns: 1fr;
    }
    
    .patterns-grid {
        grid-template-columns: 1fr;
    }
    
    .trends-grid {
        grid-template-columns: repeat(2, 1fr);
    }
    
    .category-stats {
        flex-direction: column;
        gap: 0.5rem;
    }
}

@media (max-width: 480px) {
    .analytics-header h1 {
        font-size: 1.5rem;
    }
    
    .stat-card {
        flex-direction: column;
        text-align: center;
    }
    
    .category-header {
        flex-wrap: wrap;
        justify-content: center;
    }
    
    .productive-item {
        flex-wrap: wrap;
        justify-content: space-between;
    }
    
    .trends-grid {
        grid-template-columns: 1fr;
    }
}'''
    
    # Append to existing CSS
    with open("frontend/src/styles/App.css", 'a') as f:
        f.write(analytics_css)
    
    print("✅ Added comprehensive analytics CSS")
    
    # 7. Create installation script for Chart.js
    install_script = '''#!/bin/bash
echo "📊 Installing Chart.js dependencies..."

cd frontend
npm install chart.js@^4.4.0 react-chartjs-2@^5.2.0

if [ $? -eq 0 ]; then
    echo "✅ Chart.js dependencies installed successfully"
else
    echo "❌ Failed to install Chart.js dependencies"
    echo "Please run manually: cd frontend && npm install chart.js react-chartjs-2"
fi

cd ..'''
    
    with open("install_chartjs.sh", 'w') as f:
        f.write(install_script)
    os.chmod("install_chartjs.sh", 0o755)
    
    # 8. Create restart script
    restart_script = f'''#!/bin/bash
echo "📊 Restarting ENTROPY with Advanced Analytics Dashboard..."
echo "Backup created: {backup_dir}"
echo ""

# Install dependencies first
echo "📦 Installing Chart.js dependencies..."
./install_chartjs.sh

# Kill existing processes
pkill -f "node.*server.js" || true
pkill -f "react-scripts" || true

# Wait a moment
sleep 2

echo "✅ Advanced Analytics Dashboard Implemented:"
echo "  📊 Comprehensive overview with key metrics"
echo "  📈 Beautiful charts with completion trends"
echo "  🎯 Category performance breakdown"
echo "  📅 7-day productivity trends analysis"
echo "  🏆 Completion streaks and patterns"
echo "  🎨 Professional responsive design"
echo ""
echo "🎯 Analytics Features:"
echo "  • Overview: Total stats, period comparisons, bar charts"
echo "  • Categories: Pie charts, completion rates, performance"
echo "  • Trends: 7-day line charts, daily breakdowns"
echo "  • Patterns: Priority distribution, streaks, top categories"
echo ""
echo "🛡️  Backup & Restore:"
echo "  📦 Backup created: {backup_dir}"
echo "  🔄 To restore: python3 ../restore_backup.py {backup_dir}"
echo ""

# Start the application
./start.sh'''
    
    with open("restart_analytics.sh", 'w') as f:
        f.write(restart_script)
    os.chmod("restart_analytics.sh", 0o755)
    
    print(f"\n🎉 Advanced Analytics Dashboard Complete!")
    print("=" * 50)
    print("✅ Backend: Comprehensive analytics API with 4 endpoints")
    print("✅ Database: Complex aggregations for insights and trends")
    print("✅ Frontend: Professional dashboard with Chart.js integration")
    print("✅ Charts: Bar, Line, Doughnut charts with beautiful styling")
    print("✅ Mobile: Fully responsive design for all devices")
    print("✅ Integration: Works with categories, 5 AM boundaries, templates")
    
    print(f"\n📦 BACKUP CREATED: {backup_dir}")
    print(f"🔄 Restore command: python3 ../restore_backup.py {backup_dir}")
    
    print("\n📊 PROFESSIONAL ANALYTICS FEATURES:")
    print("• **Overview Tab**: Key metrics, period comparisons, bar charts")
    print("• **Categories Tab**: Pie charts, performance breakdown, completion rates")
    print("• **Trends Tab**: 7-day line charts, daily productivity patterns")
    print("• **Patterns Tab**: Priority distribution, completion streaks, top categories")
    
    print("\n🎯 DATA-DRIVEN INSIGHTS:")
    print("• Track completion rates across different time periods")
    print("• Identify your most productive categories")
    print("• Monitor daily productivity trends")
    print("• See completion streaks and maintain momentum")
    print("• Analyze priority distribution patterns")
    
    print("\n📈 BEAUTIFUL VISUALIZATIONS:")
    print("• Interactive charts with Chart.js library")
    print("• Color-coded category representations")
    print("• Animated transitions and hover effects")
    print("• Professional dashboard design")
    
    print("\n🚀 To start with analytics:")
    print("./restart_analytics.sh")
    
    print("\n⚡ Your ENTROPY is now a data-driven productivity powerhouse! ⚡")

if __name__ == "__main__":
    main()
