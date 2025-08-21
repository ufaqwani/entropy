import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { FiAlertTriangle, FiFolder } from 'react-icons/fi';
import axios from 'axios';

const TaskForm = ({ onSubmit, onCancel }) => {
    const [categories, setCategories] = useState([]);
    const [formData, setFormData] = useState({
        title: '',
        description: '',
        priority: 1,
        category: ''
    });
    const [duplicateWarning, setDuplicateWarning] = useState(null);
    const [isChecking, setIsChecking] = useState(false);
    const [loadingCategories, setLoadingCategories] = useState(true);

    useEffect(() => {
        loadCategories();
    }, []);

    const loadCategories = async () => {
        try {
            setLoadingCategories(true);
            const response = await axios.get('/api/categories');
            setCategories(response.data);
        } catch (error) {
            console.error('Error loading categories:', error);
        } finally {
            setLoadingCategories(false);
        }
    };

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
        
        if (!formData.title.trim() || !formData.category) {
            alert('Please fill in all required fields, including category selection.');
            return;
        }
        
        try {
            await checkForDuplicate(formData.title);
            
            if (duplicateWarning) {
                const confirm = window.confirm(
                    `A similar task already exists. Do you want to create this task anyway?\n\nExisting: "${duplicateWarning.existingTask?.title}"\nNew: "${formData.title}"`
                );
                if (!confirm) return;
            }
            
            onSubmit(formData);
            setFormData({ title: '', description: '', priority: 1, category: '' });
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
        
        if (name === 'title') {
            const debounceTimeout = setTimeout(() => {
                checkForDuplicate(value);
            }, 500);
            
            return () => clearTimeout(debounceTimeout);
        }
    };

    const selectedCategory = categories.find(cat => cat._id === formData.category);

    if (loadingCategories) {
        return (
            <motion.div
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                className="task-form-overlay"
            >
                <div className="task-form">
                    <h3>Loading Categories...</h3>
                    <div className="loading-spinner"></div>
                </div>
            </motion.div>
        );
    }

    if (categories.length === 0) {
        return (
            <motion.div
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                className="task-form-overlay"
            >
                <div className="task-form">
                    <div className="no-categories-message">
                        <FiFolder size={48} />
                        <h3>No Categories Available</h3>
                        <p>You need to create at least one category before adding tasks.</p>
                        <p>Categories help keep your tasks organized and professional.</p>
                        <div className="form-actions">
                            <button onClick={onCancel} className="btn-primary">
                                Close & Create Categories
                            </button>
                        </div>
                    </div>
                </div>
            </motion.div>
        );
    }

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
                        <label htmlFor="category">Category *</label>
                        <select
                            id="category"
                            name="category"
                            value={formData.category}
                            onChange={handleChange}
                            required
                            className={`category-select ${selectedCategory ? 'has-selection' : ''}`}
                        >
                            <option value="">Select a category...</option>
                            {categories.map(category => (
                                <option key={category._id} value={category._id}>
                                    {category.icon} {category.name}
                                </option>
                            ))}
                        </select>
                        {selectedCategory && (
                            <div className="selected-category-preview">
                                <span 
                                    className="category-color"
                                    style={{ backgroundColor: selectedCategory.color }}
                                ></span>
                                <span className="category-name">
                                    {selectedCategory.icon} {selectedCategory.name}
                                </span>
                            </div>
                        )}
                    </div>

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
                            disabled={isChecking || !formData.category}
                        >
                            {duplicateWarning ? 'Add Anyway' : 'Add Task'}
                        </button>
                    </div>
                </form>
            </div>
        </motion.div>
    );
};

export default TaskForm;