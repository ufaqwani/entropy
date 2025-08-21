import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { FiPlus, FiEdit2, FiTrash2, FiFolder, FiX, FiCheck } from 'react-icons/fi';
import axios from 'axios';

const CategoryManager = ({ isOpen, onClose, onCategoryChange }) => {
    const [categories, setCategories] = useState([]);
    const [showForm, setShowForm] = useState(false);
    const [editingCategory, setEditingCategory] = useState(null);
    const [formData, setFormData] = useState({
        name: '',
        description: '',
        color: '#3b82f6',
        icon: '📁'
    });
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        if (isOpen) {
            loadCategories();
        }
    }, [isOpen]);

    const loadCategories = async () => {
        try {
            setLoading(true);
            const response = await axios.get('/api/categories');
            setCategories(response.data);
        } catch (error) {
            console.error('Error loading categories:', error);
        } finally {
            setLoading(false);
        }
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        
        if (!formData.name.trim()) return;
        
        try {
            if (editingCategory) {
                const response = await axios.put(`/api/categories/${editingCategory._id}`, formData);
                setCategories(prev => prev.map(cat => 
                    cat._id === editingCategory._id ? response.data : cat
                ));
            } else {
                const response = await axios.post('/api/categories', formData);
                setCategories(prev => [...prev, response.data]);
            }
            
            resetForm();
            onCategoryChange?.();
        } catch (error) {
            console.error('Error saving category:', error);
            alert(error.response?.data?.message || 'Failed to save category');
        }
    };

    const handleEdit = (category) => {
        setEditingCategory(category);
        setFormData({
            name: category.name,
            description: category.description || '',
            color: category.color,
            icon: category.icon
        });
        setShowForm(true);
    };

    const handleDelete = async (category) => {
        if (category.taskCount > 0) {
            alert(`Cannot delete "${category.name}" because it has ${category.taskCount} task${category.taskCount !== 1 ? 's' : ''}. Please move or delete the tasks first.`);
            return;
        }
        
        if (window.confirm(`Delete category "${category.name}"?`)) {
            try {
                await axios.delete(`/api/categories/${category._id}`);
                setCategories(prev => prev.filter(cat => cat._id !== category._id));
                onCategoryChange?.();
            } catch (error) {
                console.error('Error deleting category:', error);
                alert('Failed to delete category');
            }
        }
    };

    const resetForm = () => {
        setFormData({
            name: '',
            description: '',
            color: '#3b82f6',
            icon: '📁'
        });
        setEditingCategory(null);
        setShowForm(false);
    };

    const commonIcons = ['📁', '💼', '🏠', '🎯', '💡', '🔧', '📚', '🎨', '💪', '🌟', '⚡', '🔥'];

    if (!isOpen) return null;

    return (
        <motion.div
            className="category-manager-overlay"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
        >
            <motion.div
                className="category-manager-modal"
                initial={{ scale: 0.9, y: 20 }}
                animate={{ scale: 1, y: 0 }}
                exit={{ scale: 0.9, y: 20 }}
            >
                <div className="modal-header">
                    <h2>📂 Manage Categories</h2>
                    <button className="close-btn" onClick={onClose}>
                        <FiX />
                    </button>
                </div>

                <div className="modal-content">
                    {!showForm ? (
                        <>
                            <div className="categories-header">
                                <h3>Your Categories</h3>
                                <button 
                                    className="btn-primary small"
                                    onClick={() => setShowForm(true)}
                                >
                                    <FiPlus /> New Category
                                </button>
                            </div>

                            {loading ? (
                                <div className="loading-categories">Loading...</div>
                            ) : categories.length === 0 ? (
                                <div className="no-categories">
                                    <FiFolder size={48} />
                                    <h4>No categories yet</h4>
                                    <p>Create your first category to start organizing tasks</p>
                                    <button 
                                        className="btn-primary"
                                        onClick={() => setShowForm(true)}
                                    >
                                        <FiPlus /> Create Category
                                    </button>
                                </div>
                            ) : (
                                <div className="categories-grid">
                                    <AnimatePresence>
                                        {categories.map((category) => (
                                            <motion.div
                                                key={category._id}
                                                className="category-card"
                                                layout
                                                initial={{ opacity: 0, scale: 0.9 }}
                                                animate={{ opacity: 1, scale: 1 }}
                                                exit={{ opacity: 0, scale: 0.9 }}
                                            >
                                                <div className="category-header">
                                                    <div 
                                                        className="category-icon"
                                                        style={{ backgroundColor: category.color }}
                                                    >
                                                        {category.icon}
                                                    </div>
                                                    <div className="category-info">
                                                        <h4>{category.name}</h4>
                                                        <p>{category.description || 'No description'}</p>
                                                        <span className="task-count">
                                                            {category.taskCount} task{category.taskCount !== 1 ? 's' : ''}
                                                        </span>
                                                    </div>
                                                </div>
                                                
                                                <div className="category-actions">
                                                    <button 
                                                        className="edit-btn"
                                                        onClick={() => handleEdit(category)}
                                                        title="Edit category"
                                                    >
                                                        <FiEdit2 />
                                                    </button>
                                                    <button 
                                                        className="delete-btn"
                                                        onClick={() => handleDelete(category)}
                                                        title="Delete category"
                                                        disabled={category.taskCount > 0}
                                                    >
                                                        <FiTrash2 />
                                                    </button>
                                                </div>
                                            </motion.div>
                                        ))}
                                    </AnimatePresence>
                                </div>
                            )}
                        </>
                    ) : (
                        <form onSubmit={handleSubmit} className="category-form">
                            <h3>{editingCategory ? 'Edit Category' : 'New Category'}</h3>
                            
                            <div className="form-group">
                                <label>Category Name *</label>
                                <input
                                    type="text"
                                    value={formData.name}
                                    onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
                                    placeholder="e.g., Work, Personal, Health"
                                    maxLength={50}
                                    required
                                    autoFocus
                                />
                            </div>

                            <div className="form-group">
                                <label>Description</label>
                                <textarea
                                    value={formData.description}
                                    onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
                                    placeholder="Optional description for this category"
                                    maxLength={200}
                                    rows={3}
                                />
                            </div>

                            <div className="form-row">
                                <div className="form-group">
                                    <label>Color</label>
                                    <input
                                        type="color"
                                        value={formData.color}
                                        onChange={(e) => setFormData(prev => ({ ...prev, color: e.target.value }))}
                                        className="color-input"
                                    />
                                </div>

                                <div className="form-group">
                                    <label>Icon</label>
                                    <div className="icon-selector">
                                        <input
                                            type="text"
                                            value={formData.icon}
                                            onChange={(e) => setFormData(prev => ({ ...prev, icon: e.target.value }))}
                                            className="icon-input"
                                            maxLength={2}
                                        />
                                        <div className="icon-suggestions">
                                            {commonIcons.map(icon => (
                                                <button
                                                    key={icon}
                                                    type="button"
                                                    className={`icon-btn ${formData.icon === icon ? 'active' : ''}`}
                                                    onClick={() => setFormData(prev => ({ ...prev, icon }))}
                                                >
                                                    {icon}
                                                </button>
                                            ))}
                                        </div>
                                    </div>
                                </div>
                            </div>

                            <div className="form-actions">
                                <button type="button" onClick={resetForm} className="btn-secondary">
                                    Cancel
                                </button>
                                <button type="submit" className="btn-primary">
                                    <FiCheck /> {editingCategory ? 'Update' : 'Create'} Category
                                </button>
                            </div>
                        </form>
                    )}
                </div>
            </motion.div>
        </motion.div>
    );
};

export default CategoryManager;