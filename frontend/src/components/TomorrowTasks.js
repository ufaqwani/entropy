import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { FiClock, FiArrowRight, FiArrowLeft, FiCalendar, FiTrash2, FiCheck } from 'react-icons/fi';

const TomorrowTasks = ({ tasks, onUpdate, onDelete, onMoveBack }) => {
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

    const handleMoveBack = (taskId, taskTitle) => {
        if (window.confirm(`Move "${taskTitle}" back to today's tasks?`)) {
            onMoveBack(taskId);
        }
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
                                    {task.category && (
                                        <div className="task-category-info">
                                            <span 
                                                className="category-badge"
                                                style={{ backgroundColor: task.category.color }}
                                            >
                                                {task.category.icon} {task.category.name}
                                            </span>
                                        </div>
                                    )}
                                </div>
                                
                                <div className="task-meta">
                                    <span className="priority-label">
                                        {priorityConfig[task.priority].label}
                                    </span>
                                    <div className="task-actions">
                                        <button
                                            className="move-back-btn"
                                            onClick={() => handleMoveBack(task._id, task.title)}
                                            title={`Move "${task.title}" back to today`}
                                        >
                                            <FiArrowLeft />
                                        </button>
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
                <p className="move-back-hint">
                    ⬅️ Changed your mind? Use the arrow button to move tasks back to today
                </p>
            </div>
        </div>
    );
};

export default TomorrowTasks;