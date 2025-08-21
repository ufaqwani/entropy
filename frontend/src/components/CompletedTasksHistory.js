import React, { useState, useEffect } from 'react';
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

export default CompletedTasksHistory;