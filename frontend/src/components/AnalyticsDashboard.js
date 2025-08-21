import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
    FiTrendingUp, FiTarget, FiAward, FiCalendar, 
    FiBarChart2, FiPieChart, FiActivity, FiStar 
} from 'react-icons/fi';

// CRITICAL FIX: Import and register ALL Chart.js components
import { Chart as ChartJS, registerables } from 'chart.js';
import { Bar, Doughnut, Line } from 'react-chartjs-2';
import axios from 'axios';

// Register ALL Chart.js components at once (fixes 99% of blank chart issues)
ChartJS.register(...registerables);

// Add "No Data" plugin
const noDataPlugin = {
    id: 'noData',
    beforeDraw: (chart) => {
        const hasData = chart.data.datasets.some(dataset => 
            dataset.data && dataset.data.length > 0 && 
            dataset.data.some(value => value !== null && value !== undefined && value !== 0)
        );
        
        if (!hasData) {
            const ctx = chart.ctx;
            const width = chart.width;
            const height = chart.height;
            
            chart.clear();
            ctx.save();
            ctx.textAlign = 'center';
            ctx.textBaseline = 'middle';
            ctx.font = "16px 'Roboto Mono'";
            ctx.fillStyle = '#666';
            ctx.fillText('No Data Available', width / 2, height / 2);
            ctx.fillText('Create and complete some tasks to see analytics', width / 2, height / 2 + 25);
            ctx.restore();
        }
    }
};

// Register the plugin
ChartJS.register(noDataPlugin);


const AnalyticsDashboard = () => {
    const [overview, setOverview] = useState(null);
    const [categories, setCategories] = useState([]);
    const [trends, setTrends] = useState([]);
    const [patterns, setPatterns] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [activeTab, setActiveTab] = useState('overview');

    useEffect(() => {
        loadAnalyticsData();
    }, []);

const loadAnalyticsData = async () => {
    try {
        setLoading(true);
        setError(null);
        
        console.log('🔍 Loading analytics data...');
        
        const [overviewRes, categoriesRes, trendsRes, patternsRes] = await Promise.all([
            axios.get('/api/analytics/overview'),
            axios.get('/api/analytics/categories'),
            axios.get('/api/analytics/trends/daily'),
            axios.get('/api/analytics/patterns')
        ]);
        
        // DEBUG: Log the actual data received
        console.log('📊 Analytics data received:', {
            overview: overviewRes.data,
            categories: categoriesRes.data,
            trends: trendsRes.data,
            patterns: patternsRes.data
        });
        
        setOverview(overviewRes.data);
        setCategories(categoriesRes.data);
        setTrends(trendsRes.data);
        setPatterns(patternsRes.data);
        
        console.log('✅ Analytics data loaded successfully');
        
    } catch (error) {
        console.error('❌ Error loading analytics:', error);
        setError('Failed to load analytics data: ' + error.message);
    } finally {
        setLoading(false);
    }
};


    if (loading) {
        return (
            <div className="analytics-loading">
                <div className="loading-spinner"></div>
                <p>Loading analytics...</p>
                <p style={{fontSize: '0.8rem', color: '#666'}}>
                    If this takes too long, check the browser console for errors
                </p>
            </div>
        );
    }

    if (error) {
        return (
            <div className="analytics-error">
                <h3>Analytics Error</h3>
                <p>{error}</p>
                <button onClick={loadAnalyticsData} className="btn-primary">
                    Retry Loading
                </button>
                <details style={{marginTop: '1rem'}}>
                    <summary>Troubleshooting</summary>
                    <ul style={{textAlign: 'left', marginTop: '0.5rem'}}>
                        <li>Check browser console for API errors</li>
                        <li>Ensure backend server is running</li>
                        <li>Create some tasks and complete them first</li>
                    </ul>
                </details>
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
    console.log('🎯 Categories data for charts:', categories);
    
    if (!categories || categories.length === 0) {
        return (
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                className="no-data"
            >
                <h3>No Category Data Available</h3>
                <p>Create some tasks with categories to see analytics</p>
                <div style={{marginTop: '1rem', fontSize: '0.9rem', color: '#666'}}>
                    <strong>To get analytics data:</strong>
                    <br />1. Create 2-3 categories
                    <br />2. Add 5+ tasks to different categories  
                    <br />3. Complete some of those tasks
                </div>
            </motion.div>
        );
    }

    // FIXED: Ensure data arrays have values
    const categoryData = {
        labels: categories.map(cat => cat.categoryName || 'Unnamed'),
        datasets: [{
            data: categories.map(cat => Math.max(cat.totalTasks || 0, 0)),
            backgroundColor: categories.map(cat => cat.categoryColor || '#3b82f6'),
            borderColor: '#ffffff',
            borderWidth: 2
        }]
    };

    console.log('📈 Chart data structure:', categoryData);

    const chartOptions = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                position: 'right',
                labels: {
                    color: '#666',
                    font: {
                        family: 'Roboto Mono'
                    }
                }
            },
            title: {
                display: true,
                text: 'Tasks Distribution by Category',
                color: '#333',
                font: {
                    family: 'Roboto Mono',
                    size: 16
                }
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
                <div style={{ height: '400px', width: '100%' }}>
                    <Doughnut data={categoryData} options={chartOptions} />
                </div>
            </div>

            <div className="categories-breakdown">
                <h3>Category Performance</h3>
                <div className="categories-list">
                    {categories.map((category, index) => (
                        <motion.div
                            key={category.categoryId || index}
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
                                    {category.completionRate || 0}%
                                </span>
                            </div>
                            
                            <div className="category-stats">
                                <div className="stat">
                                    <span className="label">Total:</span>
                                    <span className="value">{category.totalTasks || 0}</span>
                                </div>
                                <div className="stat">
                                    <span className="label">Completed:</span>
                                    <span className="value">{category.completedTasks || 0}</span>
                                </div>
                                <div className="stat">
                                    <span className="label">Pending:</span>
                                    <span className="value">{category.pendingTasks || 0}</span>
                                </div>
                            </div>
                            
                            <div className="progress-bar">
                                <div 
                                    className="progress-fill"
                                    style={{ 
                                        width: `${category.completionRate || 0}%`,
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

export default AnalyticsDashboard;