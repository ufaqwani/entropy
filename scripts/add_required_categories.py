#!/usr/bin/env python3
"""
ENTROPY - Add Required Task Categories/Groups System
Professional task organization with user-defined categories
"""

import os
import shutil
import json
from datetime import datetime

def create_backup():
    """Create backup before adding categories"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = f"../entropy_backup_categories_{timestamp}"
    
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
    # Ensure directory exists
    os.makedirs(os.path.dirname(file_path) if os.path.dirname(file_path) else '.', exist_ok=True)
    with open(file_path, 'w') as f:
        f.write(content)
    print(f"✅ Updated: {file_path}")

def main():
    print("📂 ENTROPY - Add Required Task Categories System")
    print("=" * 50)
    print("🎯 Professional task organization with user-defined groups")
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
    
    print("🗃️ Creating Category model...")
    
    # 1. Create Category model
    category_model = '''const mongoose = require('mongoose');

const categorySchema = new mongoose.Schema({
    name: {
        type: String,
        required: true,
        trim: true,
        maxLength: 50,
        unique: true
    },
    description: {
        type: String,
        trim: true,
        maxLength: 200
    },
    color: {
        type: String,
        default: '#000000',
        match: /^#[0-9A-F]{6}$/i
    },
    icon: {
        type: String,
        trim: true,
        maxLength: 50,
        default: '📁'
    },
    isActive: {
        type: Boolean,
        default: true
    }
}, {
    timestamps: true
});

// Index for better query performance
categorySchema.index({ name: 1, isActive: 1 });

module.exports = mongoose.model('Category', categorySchema);'''
    
    update_file("backend/models/Category.js", category_model)
    
    print("🔄 Updating Task model to include category...")
    
    # 2. Update Task model to include category reference
    updated_task_model = '''const mongoose = require('mongoose');

const taskSchema = new mongoose.Schema({
    title: {
        type: String,
        required: true,
        trim: true,
        maxLength: 200
    },
    description: {
        type: String,
        trim: true,
        maxLength: 1000
    },
    priority: {
        type: Number,
        required: true,
        min: 1,
        max: 3
    },
    category: {
        type: mongoose.Schema.Types.ObjectId,
        ref: 'Category',
        required: true // REQUIRED: Every task must have a category
    },
    completed: {
        type: Boolean,
        default: false
    },
    date: {
        type: Date,
        default: Date.now
    },
    completedAt: {
        type: Date
    },
    moved: {
        type: Boolean,
        default: false
    },
    deleted: {
        type: Boolean,
        default: false
    },
    originalTaskId: {
        type: mongoose.Schema.Types.ObjectId,
        ref: 'Task'
    }
}, {
    timestamps: true
});

// Index for better query performance
taskSchema.index({ date: 1, completed: 1, moved: 1, deleted: 1, category: 1 });

module.exports = mongoose.model('Task', taskSchema);'''
    
    update_file("backend/models/Task.js", updated_task_model)
    
    print("🔗 Creating Category API routes...")
    
    # 3. Create Category routes
    category_routes = '''const express = require('express');
const router = express.Router();
const Category = require('../models/Category');
const Task = require('../models/Task');

// Get all active categories
router.get('/', async (req, res) => {
    try {
        const categories = await Category.find({ isActive: true })
            .sort({ name: 1 });
        
        // Count tasks in each category
        const categoriesWithCounts = await Promise.all(
            categories.map(async (category) => {
                const taskCount = await Task.countDocuments({ 
                    category: category._id,
                    $or: [{ deleted: { $exists: false } }, { deleted: false }]
                });
                return {
                    ...category.toObject(),
                    taskCount
                };
            })
        );
        
        res.json(categoriesWithCounts);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// Create new category
router.post('/', async (req, res) => {
    try {
        const { name, description, color, icon } = req.body;
        
        if (!name || !name.trim()) {
            return res.status(400).json({ error: 'Category name is required' });
        }
        
        // Check for duplicate names (case-insensitive)
        const existingCategory = await Category.findOne({
            name: { $regex: new RegExp(`^${name.trim()}$`, 'i') },
            isActive: true
        });
        
        if (existingCategory) {
            return res.status(409).json({ 
                error: 'Category name already exists',
                message: `A category named "${name.trim()}" already exists`
            });
        }
        
        const category = new Category({
            name: name.trim(),
            description: description?.trim(),
            color: color || '#000000',
            icon: icon || '📁'
        });
        
        await category.save();
        res.status(201).json(category);
    } catch (error) {
        if (error.code === 11000) {
            res.status(409).json({ error: 'Category name must be unique' });
        } else {
            res.status(400).json({ error: error.message });
        }
    }
});

// Update category
router.put('/:id', async (req, res) => {
    try {
        const { id } = req.params;
        const updates = req.body;
        
        // If updating name, check for duplicates
        if (updates.name) {
            const existingCategory = await Category.findOne({
                _id: { $ne: id },
                name: { $regex: new RegExp(`^${updates.name.trim()}$`, 'i') },
                isActive: true
            });
            
            if (existingCategory) {
                return res.status(409).json({ 
                    error: 'Category name already exists',
                    message: `A category named "${updates.name.trim()}" already exists`
                });
            }
            
            updates.name = updates.name.trim();
        }
        
        const category = await Category.findByIdAndUpdate(id, updates, { new: true });
        
        if (!category) {
            return res.status(404).json({ error: 'Category not found' });
        }
        
        res.json(category);
    } catch (error) {
        res.status(400).json({ error: error.message });
    }
});

// Delete category (soft delete - mark as inactive)
router.delete('/:id', async (req, res) => {
    try {
        const { id } = req.params;
        
        // Check if category has tasks
        const taskCount = await Task.countDocuments({ 
            category: id,
            $or: [{ deleted: { $exists: false } }, { deleted: false }]
        });
        
        if (taskCount > 0) {
            return res.status(400).json({ 
                error: 'Cannot delete category with tasks',
                message: `This category has ${taskCount} task${taskCount !== 1 ? 's' : ''}. Please move or delete the tasks first.`,
                taskCount
            });
        }
        
        // Soft delete (mark as inactive)
        const category = await Category.findByIdAndUpdate(
            id, 
            { isActive: false }, 
            { new: true }
        );
        
        if (!category) {
            return res.status(404).json({ error: 'Category not found' });
        }
        
        res.json({ 
            message: 'Category deleted successfully',
            deletedCategory: category
        });
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// Get category statistics
router.get('/stats', async (req, res) => {
    try {
        const categories = await Category.find({ isActive: true });
        
        const stats = await Promise.all(
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
                
                return {
                    categoryId: category._id,
                    categoryName: category.name,
                    totalTasks,
                    completedTasks,
                    completionRate: totalTasks === 0 ? 0 : Math.round((completedTasks / totalTasks) * 100)
                };
            })
        );
        
        res.json(stats);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

module.exports = router;'''
    
    update_file("backend/routes/categories.js", category_routes)
    
    print("🔄 Updating Task routes to handle categories...")
    
    # 4. Update Task routes to include category handling
    updated_tasks_route = '''const express = require('express');
const router = express.Router();
const Task = require('../models/Task');
const Category = require('../models/Category');

// Helper function to get day boundaries starting at 5 AM
function getDayBoundaries(referenceDate = new Date()) {
    const current = new Date(referenceDate);
    
    const todayStart = new Date(current);
    todayStart.setHours(5, 0, 0, 0);
    
    if (current.getHours() < 5) {
        todayStart.setDate(todayStart.getDate() - 1);
    }
    
    const tomorrowStart = new Date(todayStart);
    tomorrowStart.setDate(tomorrowStart.getDate() + 1);
    
    const dayAfterTomorrowStart = new Date(tomorrowStart);
    dayAfterTomorrowStart.setDate(dayAfterTomorrowStart.getDate() + 1);
    
    return {
        todayStart,
        tomorrowStart,
        dayAfterTomorrowStart
    };
}

// Get today's and tomorrow's tasks with categories - ENHANCED VERSION
router.get('/today', async (req, res) => {
    try {
        const { todayStart, tomorrowStart, dayAfterTomorrowStart } = getDayBoundaries();
        
        // Get today's tasks with category information
        const todayTasks = await Task.find({
            date: { $gte: todayStart, $lt: tomorrowStart },
            $and: [
                { $or: [{ moved: { $exists: false } }, { moved: false }] },
                { $or: [{ deleted: { $exists: false } }, { deleted: false }] }
            ]
        })
        .populate('category', 'name color icon')
        .sort({ category: 1, priority: 1, createdAt: 1 });
        
        // Get tomorrow's tasks with category information
        const tomorrowTasks = await Task.find({
            date: { $gte: tomorrowStart, $lt: dayAfterTomorrowStart },
            $or: [{ deleted: { $exists: false } }, { deleted: false }]
        })
        .populate('category', 'name color icon')
        .sort({ category: 1, priority: 1, createdAt: 1 });
        
        res.json({
            today: todayTasks,
            tomorrow: tomorrowTasks,
            todayCount: todayTasks.length,
            tomorrowCount: tomorrowTasks.length,
            boundaries: {
                todayStart: todayStart.toISOString(),
                tomorrowStart: tomorrowStart.toISOString(),
                currentTime: new Date().toISOString()
            }
        });
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// Create new task - REQUIRES CATEGORY
router.post('/', async (req, res) => {
    try {
        const { title, description, priority, category, date } = req.body;
        
        if (!title || !priority || !category) {
            return res.status(400).json({ 
                error: 'Title, priority, and category are required',
                missing: {
                    title: !title,
                    priority: !priority,
                    category: !category
                }
            });
        }
        
        // Verify category exists and is active
        const categoryDoc = await Category.findOne({ 
            _id: category, 
            isActive: true 
        });
        
        if (!categoryDoc) {
            return res.status(400).json({ 
                error: 'Invalid category',
                message: 'Selected category does not exist or is inactive'
            });
        }
        
        // If no date provided, use current "day" boundary
        let taskDate;
        if (date) {
            taskDate = new Date(date);
        } else {
            const { todayStart } = getDayBoundaries();
            taskDate = todayStart;
        }
        
        const task = new Task({
            title: title.trim(),
            description: description?.trim(),
            priority,
            category,
            date: taskDate
        });
        
        await task.save();
        
        // Populate category info before returning
        await task.populate('category', 'name color icon');
        
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
        
        // If updating category, verify it exists and is active
        if (updates.category) {
            const categoryDoc = await Category.findOne({ 
                _id: updates.category, 
                isActive: true 
            });
            
            if (!categoryDoc) {
                return res.status(400).json({ 
                    error: 'Invalid category',
                    message: 'Selected category does not exist or is inactive'
                });
            }
        }
        
        const task = await Task.findByIdAndUpdate(id, updates, { new: true })
            .populate('category', 'name color icon');
        
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
        
        const taskToDelete = await Task.findById(id).populate('category', 'name color icon');
        if (!taskToDelete) {
            return res.status(404).json({ error: 'Task not found' });
        }
        
        const { todayStart, tomorrowStart, dayAfterTomorrowStart } = getDayBoundaries();
        
        const isTomorrowTask = taskToDelete.date >= tomorrowStart && taskToDelete.date < dayAfterTomorrowStart;
        
        if (isTomorrowTask) {
            const relatedMovedTask = await Task.findOne({
                title: taskToDelete.title,
                description: taskToDelete.description,
                priority: taskToDelete.priority,
                category: taskToDelete.category._id,
                date: { $gte: todayStart, $lt: tomorrowStart },
                moved: true
            });
            
            if (relatedMovedTask) {
                await Task.findByIdAndDelete(relatedMovedTask._id);
            }
        }
        
        await Task.findByIdAndDelete(id);
        
        res.json({ 
            message: 'Task deleted successfully',
            deletedTask: taskToDelete,
            isTomorrowTask: isTomorrowTask
        });
        
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// Move uncompleted tasks to tomorrow
router.post('/move-to-tomorrow', async (req, res) => {
    try {
        const { todayStart, tomorrowStart } = getDayBoundaries();
        
        const uncompletedTasks = await Task.find({
            date: { $gte: todayStart, $lt: tomorrowStart },
            completed: false,
            $and: [
                { $or: [{ moved: { $exists: false } }, { moved: false }] },
                { $or: [{ deleted: { $exists: false } }, { deleted: false }] }
            ]
        }).populate('category', 'name color icon');
        
        if (uncompletedTasks.length === 0) {
            return res.json({ 
                movedCount: 0, 
                message: 'No uncompleted tasks to move',
                tasks: [],
                movedTaskIds: []
            });
        }
        
        const movedTaskIds = [];
        const newTomorrowTasks = [];
        
        for (let task of uncompletedTasks) {
            const dayAfterTomorrowStart = new Date(tomorrowStart);
            dayAfterTomorrowStart.setDate(dayAfterTomorrowStart.getDate() + 1);
            
            const existingTomorrowTask = await Task.findOne({
                title: task.title,
                category: task.category._id,
                date: { $gte: tomorrowStart, $lt: dayAfterTomorrowStart },
                $or: [{ deleted: { $exists: false } }, { deleted: false }]
            });
            
            if (!existingTomorrowTask) {
                const newTask = new Task({
                    title: task.title,
                    description: task.description,
                    priority: task.priority,
                    category: task.category._id,
                    date: tomorrowStart,
                    originalTaskId: task._id
                });
                
                await newTask.save();
                await newTask.populate('category', 'name color icon');
                newTomorrowTasks.push(newTask);
            }
            
            await Task.findByIdAndUpdate(task._id, { moved: true });
            movedTaskIds.push(task._id);
        }
        
        const message = `Successfully moved ${newTomorrowTasks.length} task${newTomorrowTasks.length !== 1 ? 's' : ''} to tomorrow`;
        
        res.json({ 
            movedCount: newTomorrowTasks.length,
            message: message,
            tasks: newTomorrowTasks,
            movedTaskIds: movedTaskIds
        });
        
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// Get day boundary info
router.get('/day-info', async (req, res) => {
    try {
        const { todayStart, tomorrowStart, dayAfterTomorrowStart } = getDayBoundaries();
        const now = new Date();
        
        res.json({
            currentTime: now.toISOString(),
            boundaries: {
                todayStart: todayStart.toISOString(),
                tomorrowStart: tomorrowStart.toISOString(),
                dayAfterTomorrowStart: dayAfterTomorrowStart.toISOString()
            }
        });
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

module.exports = router;'''
    
    update_file("backend/routes/tasks.js", updated_tasks_route)
    
    print("🔧 Updating server to include category routes...")
    
    # 5. Update server.js to include category routes
    try:
        with open("backend/server.js", 'r') as f:
            server_content = f.read()
        
        # Add category routes import
        if "categoryRoutes" not in server_content:
            server_content = server_content.replace(
                "const completedTasksRoutes = require('./routes/completedTasks');",
                "const completedTasksRoutes = require('./routes/completedTasks');\nconst categoryRoutes = require('./routes/categories');"
            )
            
            # Add category routes usage
            server_content = server_content.replace(
                "app.use('/api/tasks', completedTasksRoutes);",
                "app.use('/api/tasks', completedTasksRoutes);\napp.use('/api/categories', categoryRoutes);"
            )
        
        update_file("backend/server.js", server_content)
        
    except Exception as e:
        print(f"⚠️ Could not automatically update server.js: {e}")
    
    print("📱 Creating Category Management component...")
    
    # 6. Create Category Management component
    category_manager = '''import React, { useState, useEffect } from 'react';
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

export default CategoryManager;'''
    
    update_file("frontend/src/components/CategoryManager.js", category_manager)
    
    print("📝 Updating TaskForm to require category selection...")
    
    # 7. Update TaskForm to include required category selection
    updated_task_form = '''import React, { useState, useEffect } from 'react';
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
                    `A similar task already exists. Do you want to create this task anyway?\\n\\nExisting: "${duplicateWarning.existingTask?.title}"\\nNew: "${formData.title}"`
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

export default TaskForm;'''
    
    update_file("frontend/src/components/TaskForm.js", updated_task_form)
    
    print("🎨 Updating TaskList to display categories...")
    
    # 8. Update TaskList to show category information
    updated_task_list = '''import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { FiCheck, FiTrash2 } from 'react-icons/fi';

const TaskList = ({ tasks, onUpdate, onDelete }) => {
    if (!tasks || tasks.length === 0) {
        return (
            <div className="no-tasks">
                <h3>No tasks yet</h3>
                <p>Add your first task to start battling entropy!</p>
            </div>
        );
    }

    const priorityConfig = {
        1: { label: 'High', color: '#ff6f6f' },
        2: { label: 'Medium', color: '#ffd966' },
        3: { label: 'Low', color: '#a5d6a7' }
    };

    const handleComplete = (taskId, completed) => {
        onUpdate(taskId, { completed });
    };

    const handleDelete = (taskId, taskTitle) => {
        if (window.confirm(`Delete "${taskTitle}"?`)) {
            onDelete(taskId);
        }
    };

    // Group tasks by category
    const groupedTasks = tasks.reduce((groups, task) => {
        const categoryName = task.category?.name || 'Uncategorized';
        if (!groups[categoryName]) {
            groups[categoryName] = {
                category: task.category,
                tasks: []
            };
        }
        groups[categoryName].tasks.push(task);
        return groups;
    }, {});

    return (
        <div className="task-list">
            <AnimatePresence>
                {Object.entries(groupedTasks).map(([categoryName, group]) => (
                    <motion.div
                        key={categoryName}
                        className="category-group"
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: -20 }}
                        transition={{ duration: 0.3 }}
                    >
                        <div className="category-group-header">
                            <div className="category-info">
                                {group.category && (
                                    <>
                                        <span 
                                            className="category-icon"
                                            style={{ backgroundColor: group.category.color }}
                                        >
                                            {group.category.icon}
                                        </span>
                                        <span className="category-name">{categoryName}</span>
                                    </>
                                )}
                                {!group.category && (
                                    <>
                                        <span className="category-icon uncategorized">📁</span>
                                        <span className="category-name">Uncategorized</span>
                                    </>
                                )}
                            </div>
                            <span className="task-count">
                                {group.tasks.length} task{group.tasks.length !== 1 ? 's' : ''}
                            </span>
                        </div>

                        <div className="category-tasks">
                            <AnimatePresence>
                                {group.tasks.map((task, index) => (
                                    <motion.div
                                        key={task._id}
                                        className={`task-item ${task.completed ? 'completed' : ''}`}
                                        initial={{ opacity: 0, x: -20 }}
                                        animate={{ opacity: 1, x: 0 }}
                                        exit={{ opacity: 0, x: 20 }}
                                        transition={{ delay: index * 0.05 }}
                                        whileHover={{ scale: 1.01 }}
                                    >
                                        <div className="task-content">
                                            <button
                                                className={`task-checkbox ${task.completed ? 'checked' : ''}`}
                                                onClick={() => handleComplete(task._id, !task.completed)}
                                                title={task.completed ? 'Mark as incomplete' : 'Mark as complete'}
                                            >
                                                {task.completed && <FiCheck />}
                                            </button>

                                            <div className="task-info">
                                                <h4 className={task.completed ? 'strikethrough' : ''}>
                                                    {task.title}
                                                </h4>
                                                {task.description && (
                                                    <p className="task-description">{task.description}</p>
                                                )}
                                            </div>

                                            <div className="task-meta">
                                                <div 
                                                    className="priority-badge"
                                                    style={{ backgroundColor: priorityConfig[task.priority].color }}
                                                >
                                                    {priorityConfig[task.priority].label}
                                                </div>
                                                
                                                <button
                                                    className="delete-btn"
                                                    onClick={() => handleDelete(task._id, task.title)}
                                                    title={`Delete "${task.title}"`}
                                                >
                                                    <FiTrash2 />
                                                </button>
                                            </div>
                                        </div>
                                    </motion.div>
                                ))}
                            </AnimatePresence>
                        </div>
                    </motion.div>
                ))}
            </AnimatePresence>
        </div>
    );
};

export default TaskList;'''
    
    update_file("frontend/src/components/TaskList.js", updated_task_list)
    
    print("🔄 Updating main App component to include category management...")
    
    # 9. Update App.js to include category management
    try:
        with open("frontend/src/App.js", 'r') as f:
            app_content = f.read()
        
        # Add CategoryManager import
        if "CategoryManager" not in app_content:
            app_content = app_content.replace(
                "import DayBoundaryInfo from './components/DayBoundaryInfo';",
                "import DayBoundaryInfo from './components/DayBoundaryInfo';\nimport CategoryManager from './components/CategoryManager';"
            )
        
        # Add state for category manager
        if "showCategoryManager" not in app_content:
            app_content = app_content.replace(
                "const [loading, setLoading] = useState(true);",
                "const [loading, setLoading] = useState(true);\n    const [showCategoryManager, setShowCategoryManager] = useState(false);"
            )
        
        # Add category refresh handler
        if "handleCategoryChange" not in app_content:
            app_content = app_content.replace(
                "const { notifications, addNotification, removeNotification } = useNotifications();",
                '''const { notifications, addNotification, removeNotification } = useNotifications();

    const handleCategoryChange = () => {
        // Reload tasks when categories change
        loadTasks();
    };'''
            )
        
        # Add Categories button to task actions
        if "Categories" not in app_content:
            app_content = app_content.replace(
                '''                                        <button 
                                            className="btn-primary"
                                            onClick={() => setShowTaskForm(true)}
                                            disabled={todayTasks.length >= 5}
                                        >
                                            + Add Task {todayTasks.length >= 3 && '(Not Recommended)'}
                                        </button>''',
                '''                                        <button 
                                            className="btn-secondary"
                                            onClick={() => setShowCategoryManager(true)}
                                        >
                                            📂 Categories
                                        </button>
                                        <button 
                                            className="btn-primary"
                                            onClick={() => setShowTaskForm(true)}
                                            disabled={todayTasks.length >= 5}
                                        >
                                            + Add Task {todayTasks.length >= 3 && '(Not Recommended)'}
                                        </button>'''
            )
        
        # Add CategoryManager component to JSX
        if "showCategoryManager &&" not in app_content:
            app_content = app_content.replace(
                '''                        {showTaskForm && (
                            <TaskForm 
                                onSubmit={addTask}
                                onCancel={() => setShowTaskForm(false)}
                            />
                        )}''',
                '''                        {showTaskForm && (
                            <TaskForm 
                                onSubmit={addTask}
                                onCancel={() => setShowTaskForm(false)}
                            />
                        )}
                        
                        {showCategoryManager && (
                            <CategoryManager
                                isOpen={showCategoryManager}
                                onClose={() => setShowCategoryManager(false)}
                                onCategoryChange={handleCategoryChange}
                            />
                        )}'''
            )
        
        update_file("frontend/src/App.js", app_content)
        
    except Exception as e:
        print(f"⚠️ Could not automatically update App.js: {e}")
    
    print("🎨 Adding comprehensive CSS for categories...")
    
    # 10. Add CSS for category features
    category_css = '''
/* Category Management Styles */
.category-manager-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: var(--overlay);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 2000;
    padding: 1rem;
    backdrop-filter: blur(10px);
}

.category-manager-modal {
    background: var(--bg-primary);
    border: 2px solid var(--border-primary);
    border-radius: 12px;
    width: 100%;
    max-width: 700px;
    max-height: 80vh;
    overflow: hidden;
    display: flex;
    flex-direction: column;
    box-shadow: 0 8px 32px var(--shadow);
}

.modal-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1.5rem;
    border-bottom: 1px solid var(--border-secondary);
}

.modal-header h2 {
    font-family: 'Roboto Mono', monospace;
    font-size: 1.4rem;
    font-weight: 700;
    color: var(--text-primary);
    letter-spacing: 0.05em;
    text-transform: uppercase;
}

.close-btn {
    background: transparent;
    border: none;
    color: var(--text-tertiary);
    cursor: pointer;
    padding: 0.5rem;
    border-radius: 6px;
    transition: all 0.3s ease;
    font-size: 1.2rem;
}

.close-btn:hover {
    color: var(--text-primary);
    background: var(--bg-secondary);
}

.modal-content {
    flex: 1;
    overflow-y: auto;
    padding: 1.5rem;
}

.categories-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1.5rem;
}

.categories-header h3 {
    font-family: 'Roboto Mono', monospace;
    font-size: 1.2rem;
    font-weight: 600;
    color: var(--text-primary);
}

.btn-primary.small {
    padding: 0.5rem 1rem;
    font-size: 0.8rem;
}

.loading-categories {
    text-align: center;
    padding: 3rem;
    color: var(--text-tertiary);
    font-family: 'Roboto Mono', monospace;
}

.no-categories {
    text-align: center;
    padding: 3rem;
    color: var(--text-tertiary);
}

.no-categories svg {
    color: var(--text-muted);
    margin-bottom: 1rem;
}

.no-categories h4 {
    font-family: 'Roboto Mono', monospace;
    font-size: 1.2rem;
    font-weight: 600;
    color: var(--text-primary);
    margin-bottom: 0.5rem;
}

.no-categories p {
    margin-bottom: 1.5rem;
    line-height: 1.5;
}

.categories-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    gap: 1rem;
}

.category-card {
    background: var(--bg-secondary);
    border: 1px solid var(--border-secondary);
    border-radius: 8px;
    padding: 1rem;
    transition: all 0.3s ease;
}

.category-card:hover {
    border-color: var(--border-primary);
    box-shadow: 0 2px 8px var(--shadow);
}

.category-header {
    display: flex;
    align-items: center;
    gap: 1rem;
    margin-bottom: 1rem;
}

.category-icon {
    width: 40px;
    height: 40px;
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.2rem;
    color: white;
    flex-shrink: 0;
}

.category-info {
    flex: 1;
    min-width: 0;
}

.category-info h4 {
    font-family: 'Roboto Mono', monospace;
    font-size: 1rem;
    font-weight: 600;
    color: var(--text-primary);
    margin-bottom: 0.25rem;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

.category-info p {
    font-size: 0.85rem;
    color: var(--text-tertiary);
    margin-bottom: 0.5rem;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

.task-count {
    font-family: 'Roboto Mono', monospace;
    font-size: 0.75rem;
    color: var(--text-muted);
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

.category-actions {
    display: flex;
    gap: 0.5rem;
}

.edit-btn,
.delete-btn {
    background: transparent;
    border: 1px solid var(--border-tertiary);
    color: var(--text-tertiary);
    padding: 0.5rem;
    border-radius: 6px;
    cursor: pointer;
    transition: all 0.3s ease;
    font-size: 0.9rem;
}

.edit-btn:hover {
    border-color: var(--border-primary);
    color: var(--text-primary);
    background: var(--bg-tertiary);
}

.delete-btn:hover:not(:disabled) {
    border-color: #ff6b6b;
    color: #ff6b6b;
    background: rgba(255, 107, 107, 0.1);
}

.delete-btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
}

/* Category Form Styles */
.category-form {
    background: var(--bg-secondary);
    padding: 1.5rem;
    border-radius: 8px;
    border: 1px solid var(--border-secondary);
}

.category-form h3 {
    font-family: 'Roboto Mono', monospace;
    font-size: 1.2rem;
    font-weight: 600;
    color: var(--text-primary);
    margin-bottom: 1.5rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

.form-row {
    display: grid;
    grid-template-columns: 1fr 2fr;
    gap: 1rem;
}

.color-input {
    width: 100%;
    height: 40px;
    border: 2px solid var(--border-secondary);
    border-radius: 6px;
    cursor: pointer;
    background: var(--bg-primary);
}

.icon-selector {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
}

.icon-input {
    text-align: center;
    font-size: 1.2rem;
}

.icon-suggestions {
    display: grid;
    grid-template-columns: repeat(6, 1fr);
    gap: 0.25rem;
}

.icon-btn {
    background: var(--bg-primary);
    border: 1px solid var(--border-tertiary);
    padding: 0.5rem;
    border-radius: 4px;
    cursor: pointer;
    font-size: 1rem;
    transition: all 0.3s ease;
}

.icon-btn:hover,
.icon-btn.active {
    border-color: var(--border-primary);
    background: var(--bg-tertiary);
}

/* Task Form Category Styles */
.category-select {
    position: relative;
    background: var(--bg-primary);
    border: 2px solid var(--border-secondary);
    padding: 0.8rem;
    border-radius: 8px;
    font-family: 'Roboto Mono', monospace;
    transition: border-color 0.3s ease;
}

.category-select:focus {
    border-color: var(--accent-primary);
}

.category-select.has-selection {
    border-color: var(--success-border);
}

.selected-category-preview {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin-top: 0.5rem;
    padding: 0.5rem;
    background: var(--success-bg);
    border: 1px solid var(--success-border);
    border-radius: 6px;
}

.category-color {
    width: 16px;
    height: 16px;
    border-radius: 3px;
    flex-shrink: 0;
}

.category-name {
    font-family: 'Roboto Mono', monospace;
    font-size: 0.85rem;
    font-weight: 600;
    color: var(--success-text);
}

.no-categories-message {
    text-align: center;
    padding: 2rem;
}

.no-categories-message svg {
    color: var(--text-muted);
    margin-bottom: 1rem;
}

.no-categories-message h3 {
    font-family: 'Roboto Mono', monospace;
    font-size: 1.3rem;
    font-weight: 600;
    color: var(--text-primary);
    margin-bottom: 1rem;
}

.no-categories-message p {
    color: var(--text-tertiary);
    margin-bottom: 0.5rem;
    line-height: 1.5;
}

/* Task List Category Grouping */
.category-group {
    margin-bottom: 2rem;
}

.category-group-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.75rem 1rem;
    background: var(--bg-secondary);
    border: 1px solid var(--border-secondary);
    border-radius: 8px 8px 0 0;
    margin-bottom: 0;
}

.category-info {
    display: flex;
    align-items: center;
    gap: 0.75rem;
}

.category-group .category-icon {
    width: 28px;
    height: 28px;
    border-radius: 6px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1rem;
    color: white;
    flex-shrink: 0;
}

.category-group .category-icon.uncategorized {
    background: var(--text-muted);
}

.category-group .category-name {
    font-family: 'Roboto Mono', monospace;
    font-size: 1rem;
    font-weight: 600;
    color: var(--text-primary);
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

.category-group .task-count {
    font-family: 'Roboto Mono', monospace;
    font-size: 0.75rem;
    color: var(--text-muted);
    background: var(--bg-tertiary);
    padding: 0.25rem 0.5rem;
    border-radius: 4px;
    font-weight: 600;
    text-transform: uppercase;
}

.category-tasks {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
    padding: 1rem;
    background: var(--bg-primary);
    border: 1px solid var(--border-secondary);
    border-top: none;
    border-radius: 0 0 8px 8px;
}

.category-tasks .task-item {
    margin: 0;
    border-radius: 6px;
}

/* Mobile responsive */
@media (max-width: 768px) {
    .category-manager-modal {
        margin: 0;
        max-height: 90vh;
        border-radius: 12px 12px 0 0;
    }
    
    .categories-grid {
        grid-template-columns: 1fr;
    }
    
    .form-row {
        grid-template-columns: 1fr;
    }
    
    .icon-suggestions {
        grid-template-columns: repeat(8, 1fr);
    }
    
    .category-group-header {
        flex-direction: column;
        align-items: stretch;
        gap: 0.5rem;
    }
    
    .category-info {
        justify-content: center;
    }
    
    .categories-header {
        flex-direction: column;
        align-items: stretch;
        gap: 1rem;
    }
}

@media (max-width: 480px) {
    .modal-content {
        padding: 1rem;
    }
    
    .category-form {
        padding: 1rem;
    }
    
    .icon-suggestions {
        grid-template-columns: repeat(6, 1fr);
    }
}'''
    
    # Append to existing CSS
    with open("frontend/src/styles/App.css", 'a') as f:
        f.write(category_css)
    
    print("✅ Added comprehensive category CSS")
    
    # 11. Create restart script
    restart_script = f'''#!/bin/bash
echo "📂 Restarting ENTROPY with Required Categories System..."
echo "Backup created: {backup_dir}"
echo ""

# Kill existing processes
pkill -f "node.*server.js" || true
pkill -f "react-scripts" || true

# Wait a moment
sleep 2

echo "✅ Professional Category System Implemented:"
echo "  📂 Create unlimited custom categories"
echo "  🎯 Every task MUST have a category (enforced)"
echo "  🎨 Visual organization with colors and icons"
echo "  📊 Task grouping by category in lists"
echo "  🗑️  Safe category deletion (prevents data loss)"
echo ""
echo "🎯 Getting Started:"
echo "  1. Click 'Categories' button to create your first category"
echo "  2. Add tasks - category selection is required"
echo "  3. Tasks are automatically grouped by category"
echo ""
echo "🛡️  Backup & Restore:"
echo "  📦 Backup created: {backup_dir}"
echo "  🔄 To restore: python3 ../restore_backup.py {backup_dir}"
echo ""

# Start the application
./start.sh'''
    
    with open("restart_categories.sh", 'w') as f:
        f.write(restart_script)
    os.chmod("restart_categories.sh", 0o755)
    
    print(f"\n🎉 Required Categories System Implementation Complete!")
    print("=" * 60)
    print("✅ Backend: Category model and CRUD APIs created")
    print("✅ Database: Tasks now require category assignment")
    print("✅ Frontend: Professional category management UI")
    print("✅ Task Form: Category selection enforced (required)")
    print("✅ Task Display: Organized by category groups")
    print("✅ Safety: Prevents category deletion with tasks")
    
    print(f"\n📦 BACKUP CREATED: {backup_dir}")
    print(f"🔄 Restore command: python3 ../restore_backup.py {backup_dir}")
    
    print("\n🎯 PROFESSIONAL FEATURES ADDED:")
    print("• No default categories - user creates their own")
    print("• Cannot create tasks without assigning category")
    print("• Visual organization with colors and icons")
    print("• Tasks grouped by category in lists")
    print("• Category statistics and task counts")
    print("• Safe deletion prevents data loss")
    
    print("\n📂 HOW TO USE:")
    print("1. Click 'Categories' button in task actions")
    print("2. Create your first category (e.g., Work, Personal)")
    print("3. Try to add a task - category selection required")
    print("4. Tasks automatically group by category")
    
    print("\n🚀 To start with categories:")
    print("./restart_categories.sh")
    
    print("\n⚡ Your ENTROPY is now professionally organized! ⚡")

if __name__ == "__main__":
    main()
