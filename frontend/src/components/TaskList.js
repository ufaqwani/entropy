import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { FiCheck, FiTrash2, FiArrowUp, FiArrowDown } from 'react-icons/fi';

const TaskList = ({ tasks, onUpdate, onDelete, onMoveUp, onMoveDown }) => {
    if (!tasks || tasks.length === 0) {
        return (
            <div className="no-tasks">
                <h3>No tasks yet</h3>
                <p>Add your first task to start battling entropy!</p>
            </div>
        );
    }

    const priorityConfig = {
        1: { label: 'High', color: '#ff6f6f', icon: '🔥' },
        2: { label: 'Medium', color: '#ffd966', icon: '⚡' },
        3: { label: 'Low', color: '#a5d6a7', icon: '📋' }
    };

    const handleComplete = (taskId, completed) => {
        onUpdate(taskId, { completed });
    };

    const handleDelete = (taskId, taskTitle) => {
        if (window.confirm(`Delete "${taskTitle}"?`)) {
            onDelete(taskId);
        }
    };

    return (
        <div className="task-list">
            <div className="task-list-header">
                <h3>Today's Tasks</h3>
                <div className="task-count-info">
                    {tasks.filter(t => t.completed).length} of {tasks.length} completed
                </div>
            </div>
            
            <div className="tasks-container">
                <AnimatePresence>
                    {tasks.map((task, index) => (
                        <motion.div
                            key={task._id}
                            className={`task-item ${task.completed ? 'completed' : ''}`}
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            exit={{ opacity: 0, y: -20 }}
                            transition={{ delay: index * 0.05 }}
                            whileHover={{ scale: 1.01 }}
                        >
                            <div className="task-content">
                                {/* Priority Indicator */}
                                <div className="task-priority-strip" 
                                     style={{ backgroundColor: priorityConfig[task.priority].color }}>
                                </div>
                                
                                {/* Checkbox */}
                                <button
                                    className={`task-checkbox ${task.completed ? 'checked' : ''}`}
                                    onClick={() => handleComplete(task._id, !task.completed)}
                                    title={task.completed ? 'Mark as incomplete' : 'Mark as complete'}
                                >
                                    {task.completed && <FiCheck />}
                                </button>

                                {/* Task Details */}
                                <div className="task-details">
                                    <div className="task-header">
                                        <h4 className={task.completed ? 'strikethrough' : ''}>
                                            {task.title}
                                        </h4>
                                        
                                        {/* Category Badge */}
                                        {task.category && (
                                            <div className="task-category-badge"
                                                 style={{ backgroundColor: task.category.color }}>
                                                <span className="category-icon">{task.category.icon}</span>
                                                <span className="category-name">{task.category.name}</span>
                                            </div>
                                        )}
                                    </div>
                                    
                                    {task.description && (
                                        <p className="task-description">{task.description}</p>
                                    )}
                                </div>

                                {/* Priority & Actions */}
                                <div className="task-meta">
                                    <div className="priority-info">
                                        <span className="priority-badge"
                                              style={{ backgroundColor: priorityConfig[task.priority].color }}>
                                            {priorityConfig[task.priority].icon}
                                        </span>
                                        <span className="priority-label">
                                            {priorityConfig[task.priority].label}
                                        </span>
                                    </div>
                                    
                                    <div className="task-actions-buttons">
                                        <button
                                            className="icon-btn"
                                            onClick={() => onMoveUp(task._id)}
                                            title="Move Up"
                                            disabled={index === 0}
                                        >
                                            <FiArrowUp />
                                        </button>
                                        <button
                                            className="icon-btn"
                                            onClick={() => onMoveDown(task._id)}
                                            title="Move Down"
                                            disabled={index === tasks.length - 1}
                                        >
                                            <FiArrowDown />
                                        </button>
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
        </div>
    );
};

export default TaskList;