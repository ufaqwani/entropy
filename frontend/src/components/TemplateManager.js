import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
    FiPlus, FiEdit2, FiTrash2, FiPlay, FiPause, FiClock, 
    FiRepeat, FiCalendar, FiX, FiCheck, FiInfo 
} from 'react-icons/fi';
import axios from 'axios';

const TemplateManager = ({ isOpen, onClose, onTemplateChange }) => {
    const [templates, setTemplates] = useState([]);
    const [categories, setCategories] = useState([]);
    const [showForm, setShowForm] = useState(false);
    const [editingTemplate, setEditingTemplate] = useState(null);
    const [stats, setStats] = useState(null);
    const [loading, setLoading] = useState(false);
    
    const [formData, setFormData] = useState({
        name: '',
        description: '',
        category: '',
        taskTemplate: {
            title: '',
            description: '',
            priority: 2
        },
        recurrence: {
            type: 'daily',
            interval: 1,
            daysOfWeek: [],
            dayOfMonth: 1,
            time: {
                hour: 5,
                minute: 0
            }
        }
    });

    useEffect(() => {
        if (isOpen) {
            loadData();
        }
    }, [isOpen]);

    const loadData = async () => {
        try {
            setLoading(true);
            const [templatesRes, categoriesRes, statsRes] = await Promise.all([
                axios.get('/api/templates'),
                axios.get('/api/categories'),
                axios.get('/api/templates/stats')
            ]);
            
            setTemplates(templatesRes.data);
            setCategories(categoriesRes.data);
            setStats(statsRes.data);
        } catch (error) {
            console.error('Error loading data:', error);
        } finally {
            setLoading(false);
        }
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        
        if (!formData.name.trim() || !formData.category || !formData.taskTemplate.title.trim()) {
            alert('Please fill in all required fields');
            return;
        }
        
        try {
            if (editingTemplate) {
                const response = await axios.put(`/api/templates/${editingTemplate._id}`, formData);
                setTemplates(prev => prev.map(t => 
                    t._id === editingTemplate._id ? response.data : t
                ));
            } else {
                const response = await axios.post('/api/templates', formData);
                setTemplates(prev => [...prev, response.data]);
            }
            
            resetForm();
            onTemplateChange?.();
            loadData(); // Reload to get updated stats
        } catch (error) {
            console.error('Error saving template:', error);
            alert(error.response?.data?.message || 'Failed to save template');
        }
    };

    const handleToggle = async (template) => {
        try {
            const response = await axios.patch(`/api/templates/${template._id}/toggle`);
            setTemplates(prev => prev.map(t => 
                t._id === template._id ? response.data : t
            ));
            loadData(); // Reload stats
        } catch (error) {
            console.error('Error toggling template:', error);
        }
    };

    const handleRun = async (template) => {
        try {
            const response = await axios.post(`/api/templates/${template._id}/run`);
            alert(`Task created: "${response.data.task.title}"`);
            setTemplates(prev => prev.map(t => 
                t._id === template._id ? response.data.template : t
            ));
            onTemplateChange?.();
        } catch (error) {
            console.error('Error running template:', error);
            alert(error.response?.data?.message || 'Failed to run template');
        }
    };

    const handleEdit = (template) => {
        setEditingTemplate(template);
        setFormData({
            name: template.name,
            description: template.description || '',
            category: template.category._id,
            taskTemplate: template.taskTemplate,
            recurrence: template.recurrence
        });
        setShowForm(true);
    };

    const handleDelete = async (template) => {
        if (window.confirm(`Delete template "${template.name}"?`)) {
            try {
                await axios.delete(`/api/templates/${template._id}`);
                setTemplates(prev => prev.filter(t => t._id !== template._id));
                onTemplateChange?.();
                loadData();
            } catch (error) {
                console.error('Error deleting template:', error);
                alert('Failed to delete template');
            }
        }
    };

    const resetForm = () => {
        setFormData({
            name: '',
            description: '',
            category: '',
            taskTemplate: {
                title: '',
                description: '',
                priority: 2
            },
            recurrence: {
                type: 'daily',
                interval: 1,
                daysOfWeek: [],
                dayOfMonth: 1,
                time: {
                    hour: 5,
                    minute: 0
                }
            }
        });
        setEditingTemplate(null);
        setShowForm(false);
    };

    const formatNextRun = (nextRun) => {
        const date = new Date(nextRun);
        const now = new Date();
        const diffHours = Math.floor((date - now) / (1000 * 60 * 60));
        
        if (diffHours < 0) return 'Overdue';
        if (diffHours < 24) return `In ${diffHours}h`;
        
        const diffDays = Math.floor(diffHours / 24);
        return `In ${diffDays} day${diffDays !== 1 ? 's' : ''}`;
    };

    const getRecurrenceText = (recurrence) => {
        switch (recurrence.type) {
            case 'daily':
                return `Every ${recurrence.interval === 1 ? 'day' : `${recurrence.interval} days`}`;
            case 'weekly':
                const days = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
                const dayNames = recurrence.daysOfWeek.map(d => days[d]).join(', ');
                return `Weekly: ${dayNames || 'Monday'}`;
            case 'monthly':
                return `Monthly on day ${recurrence.dayOfMonth}`;
            default:
                return `Every ${recurrence.interval} days`;
        }
    };

    if (!isOpen) return null;

    return (
        <motion.div
            className="template-manager-overlay"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
        >
            <motion.div
                className="template-manager-modal"
                initial={{ scale: 0.9, y: 20 }}
                animate={{ scale: 1, y: 0 }}
                exit={{ scale: 0.9, y: 20 }}
                initial={{ scale: 0.9, y: 20 }}
                animate={{ scale: 1, y: 0 }}
                exit={{ scale: 0.9, y: 20 }}
            >
                <div className="modal-header">
                    <h2>🔄 Recurring Templates</h2>
                    <button className="close-btn" onClick={onClose}>
                        <FiX />
                    </button>
                </div>

                <div className="modal-content">
                    {!showForm ? (
                        <>
                            {/* Stats Overview */}
                            {stats && (
                                <div className="template-stats">
                                    <div className="stat-item">
                                        <FiRepeat className="stat-icon" />
                                        <div>
                                            <span className="stat-number">{stats.summary.activeTemplates}</span>
                                            <span className="stat-label">Active Templates</span>
                                        </div>
                                    </div>
                                    <div className="stat-item">
                                        <FiCalendar className="stat-icon" />
                                        <div>
                                            <span className="stat-number">{stats.upcomingRuns.length}</span>
                                            <span className="stat-label">Upcoming Runs</span>
                                        </div>
                                    </div>
                                </div>
                            )}

                            <div className="templates-header">
                                <h3>Your Templates</h3>
                                <button 
                                    className="btn-primary small"
                                    onClick={() => setShowForm(true)}
                                >
                                    <FiPlus /> New Template
                                </button>
                            </div>

                            {loading ? (
                                <div className="loading-templates">Loading...</div>
                            ) : templates.length === 0 ? (
                                <div className="no-templates">
                                    <FiRepeat size={48} />
                                    <h4>No templates yet</h4>
                                    <p>Create recurring task templates to automate your routine</p>
                                    <button 
                                        className="btn-primary"
                                        onClick={() => setShowForm(true)}
                                    >
                                        <FiPlus /> Create Template
                                    </button>
                                </div>
                            ) : (
                                <div className="templates-list">
                                    <AnimatePresence>
                                        {templates.map((template) => (
                                            <motion.div
                                                key={template._id}
                                                className={`template-card ${!template.isActive ? 'inactive' : ''}`}
                                                layout
                                                initial={{ opacity: 0, scale: 0.9 }}
                                                animate={{ opacity: 1, scale: 1 }}
                                                exit={{ opacity: 0, scale: 0.9 }}
                                            >
                                                <div className="template-header">
                                                    <div className="template-info">
                                                        <div className="template-category">
                                                            <span 
                                                                className="category-icon"
                                                                style={{ backgroundColor: template.category.color }}
                                                            >
                                                                {template.category.icon}
                                                            </span>
                                                            <span className="category-name">{template.category.name}</span>
                                                        </div>
                                                        <h4>{template.name}</h4>
                                                        {template.description && (
                                                            <p className="template-description">{template.description}</p>
                                                        )}
                                                    </div>
                                                    
                                                    <div className="template-status">
                                                        <span className={`status-badge ${template.isActive ? 'active' : 'inactive'}`}>
                                                            {template.isActive ? 'Active' : 'Inactive'}
                                                        </span>
                                                    </div>
                                                </div>
                                                
                                                <div className="template-details">
                                                    <div className="detail-item">
                                                        <strong>Creates:</strong> "{template.taskTemplate.title}"
                                                    </div>
                                                    <div className="detail-item">
                                                        <strong>Schedule:</strong> {getRecurrenceText(template.recurrence)} 
                                                        at {String(template.recurrence.time.hour).padStart(2, '0')}:
                                                        {String(template.recurrence.time.minute).padStart(2, '0')}
                                                    </div>
                                                    {template.isActive && (
                                                        <div className="detail-item">
                                                            <strong>Next run:</strong> 
                                                            <span className="next-run">
                                                                {formatNextRun(template.nextRun)}
                                                            </span>
                                                        </div>
                                                    )}
                                                    <div className="detail-item">
                                                        <strong>Tasks created:</strong> {template.createdTasksCount}
                                                    </div>
                                                </div>
                                                
                                                <div className="template-actions">
                                                    <button 
                                                        className={`toggle-btn ${template.isActive ? 'active' : 'inactive'}`}
                                                        onClick={() => handleToggle(template)}
                                                        title={template.isActive ? 'Deactivate template' : 'Activate template'}
                                                    >
                                                        {template.isActive ? <FiPause /> : <FiPlay />}
                                                    </button>
                                                    
                                                    {template.isActive && (
                                                        <button 
                                                            className="run-btn"
                                                            onClick={() => handleRun(template)}
                                                            title="Run template now"
                                                        >
                                                            <FiPlay />
                                                        </button>
                                                    )}
                                                    
                                                    <button 
                                                        className="edit-btn"
                                                        onClick={() => handleEdit(template)}
                                                        title="Edit template"
                                                    >
                                                        <FiEdit2 />
                                                    </button>
                                                    
                                                    <button 
                                                        className="delete-btn"
                                                        onClick={() => handleDelete(template)}
                                                        title="Delete template"
                                                    >
                                                        <FiTrash2 />
                                                    </button>
                                                </div>
                                            </motion.div>
                                        ))}
                                    </AnimatePresence>
                                </div>
                            )}

                            {/* Upcoming Runs */}
                            {stats?.upcomingRuns?.length > 0 && (
                                <div className="upcoming-runs">
                                    <h4><FiClock /> Upcoming Runs</h4>
                                    <div className="upcoming-list">
                                        {stats.upcomingRuns.slice(0, 5).map(run => (
                                            <div key={run._id} className="upcoming-item">
                                                <span 
                                                    className="category-dot"
                                                    style={{ backgroundColor: run.category.color }}
                                                ></span>
                                                <span className="task-title">{run.taskTitle}</span>
                                                <span className="next-time">{formatNextRun(run.nextRun)}</span>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            )}
                        </>
                    ) : (
                        <TemplateForm 
                            formData={formData}
                            setFormData={setFormData}
                            categories={categories}
                            onSubmit={handleSubmit}
                            onCancel={resetForm}
                            isEditing={!!editingTemplate}
                        />
                    )}
                </div>
            </motion.div>
        </motion.div>
    );
};

// Template Form Component
const TemplateForm = ({ formData, setFormData, categories, onSubmit, onCancel, isEditing }) => {
    const updateFormData = (path, value) => {
        setFormData(prev => {
            const newData = { ...prev };
            const keys = path.split('.');
            let current = newData;
            
            for (let i = 0; i < keys.length - 1; i++) {
                current[keys[i]] = { ...current[keys[i]] };
                current = current[keys[i]];
            }
            
            current[keys[keys.length - 1]] = value;
            return newData;
        });
    };

    const handleDayToggle = (day) => {
        const current = formData.recurrence.daysOfWeek || [];
        const newDays = current.includes(day) 
            ? current.filter(d => d !== day)
            : [...current, day].sort();
        updateFormData('recurrence.daysOfWeek', newDays);
    };

    const dayNames = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];

    return (
        <form onSubmit={onSubmit} className="template-form">
            <h3>{isEditing ? 'Edit Template' : 'New Recurring Template'}</h3>
            
            <div className="form-group">
                <label>Template Name *</label>
                <input
                    type="text"
                    value={formData.name}
                    onChange={(e) => updateFormData('name', e.target.value)}
                    placeholder="e.g., Daily Planning, Weekly Review"
                    required
                    autoFocus
                />
            </div>

            <div className="form-group">
                <label>Description</label>
                <textarea
                    value={formData.description}
                    onChange={(e) => updateFormData('description', e.target.value)}
                    placeholder="What does this template do?"
                    rows={2}
                />
            </div>

            <div className="form-group">
                <label>Category *</label>
                <select
                    value={formData.category}
                    onChange={(e) => updateFormData('category', e.target.value)}
                    required
                >
                    <option value="">Select category...</option>
                    {categories.map(cat => (
                        <option key={cat._id} value={cat._id}>
                            {cat.icon} {cat.name}
                        </option>
                    ))}
                </select>
            </div>

            <fieldset className="task-template-section">
                <legend>Task Template</legend>
                
                <div className="form-group">
                    <label>Task Title *</label>
                    <input
                        type="text"
                        value={formData.taskTemplate.title}
                        onChange={(e) => updateFormData('taskTemplate.title', e.target.value)}
                        placeholder="Task that will be created"
                        required
                    />
                </div>

                <div className="form-group">
                    <label>Task Description</label>
                    <textarea
                        value={formData.taskTemplate.description}
                        onChange={(e) => updateFormData('taskTemplate.description', e.target.value)}
                        placeholder="Details for the task"
                        rows={2}
                    />
                </div>

                <div className="form-group">
                    <label>Priority</label>
                    <select
                        value={formData.taskTemplate.priority}
                        onChange={(e) => updateFormData('taskTemplate.priority', parseInt(e.target.value))}
                    >
                        <option value={1}>🔥 High Priority</option>
                        <option value={2}>⚡ Medium Priority</option>
                        <option value={3}>📋 Low Priority</option>
                    </select>
                </div>
            </fieldset>

            <fieldset className="recurrence-section">
                <legend>Recurrence Schedule</legend>
                
                <div className="form-group">
                    <label>Frequency</label>
                    <select
                        value={formData.recurrence.type}
                        onChange={(e) => updateFormData('recurrence.type', e.target.value)}
                    >
                        <option value="daily">Daily</option>
                        <option value="weekly">Weekly</option>
                        <option value="monthly">Monthly</option>
                        <option value="custom">Custom</option>
                    </select>
                </div>

                {formData.recurrence.type === 'weekly' && (
                    <div className="form-group">
                        <label>Days of Week</label>
                        <div className="day-selector">
                            {dayNames.map((day, index) => (
                                <button
                                    key={index}
                                    type="button"
                                    className={`day-btn ${(formData.recurrence.daysOfWeek || []).includes(index) ? 'active' : ''}`}
                                    onClick={() => handleDayToggle(index)}
                                >
                                    {day}
                                </button>
                            ))}
                        </div>
                    </div>
                )}

                {formData.recurrence.type === 'monthly' && (
                    <div className="form-group">
                        <label>Day of Month</label>
                        <input
                            type="number"
                            min="1"
                            max="31"
                            value={formData.recurrence.dayOfMonth}
                            onChange={(e) => updateFormData('recurrence.dayOfMonth', parseInt(e.target.value))}
                        />
                    </div>
                )}

                {(formData.recurrence.type === 'daily' || formData.recurrence.type === 'custom') && (
                    <div className="form-group">
                        <label>Every {formData.recurrence.type === 'daily' ? 'days' : 'days'}</label>
                        <input
                            type="number"
                            min="1"
                            value={formData.recurrence.interval}
                            onChange={(e) => updateFormData('recurrence.interval', parseInt(e.target.value))}
                        />
                    </div>
                )}

                <div className="form-row">
                    <div className="form-group">
                        <label>Hour (5 AM = 5)</label>
                        <input
                            type="number"
                            min="0"
                            max="23"
                            value={formData.recurrence.time.hour}
                            onChange={(e) => updateFormData('recurrence.time.hour', parseInt(e.target.value))}
                        />
                    </div>
                    <div className="form-group">
                        <label>Minute</label>
                        <input
                            type="number"
                            min="0"
                            max="59"
                            value={formData.recurrence.time.minute}
                            onChange={(e) => updateFormData('recurrence.time.minute', parseInt(e.target.value))}
                        />
                    </div>
                </div>
            </fieldset>

            <div className="form-actions">
                <button type="button" onClick={onCancel} className="btn-secondary">
                    Cancel
                </button>
                <button type="submit" className="btn-primary">
                    <FiCheck /> {isEditing ? 'Update' : 'Create'} Template
                </button>
            </div>
        </form>
    );
};

export default TemplateManager;