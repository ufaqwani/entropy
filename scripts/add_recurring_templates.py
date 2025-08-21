#!/usr/bin/env python3
"""
ENTROPY - Smart Recurring Tasks & Templates System
Professional automation for routine workflows and recurring tasks
"""

import os
import shutil
import json
from datetime import datetime

def create_backup():
    """Create backup before adding recurring tasks"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = f"../entropy_backup_recurring_{timestamp}"
    
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
    print("🔄 ENTROPY - Smart Recurring Tasks & Templates System")
    print("=" * 60)
    print("🎯 Professional automation for routine workflows")
    print("⚡ Templates + 5 AM boundaries + Categories = Productivity")
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
    
    print("📋 Creating Template model...")
    
    # 1. Create Template model
    template_model = '''const mongoose = require('mongoose');

const templateSchema = new mongoose.Schema({
    name: {
        type: String,
        required: true,
        trim: true,
        maxLength: 100
    },
    description: {
        type: String,
        trim: true,
        maxLength: 500
    },
    category: {
        type: mongoose.Schema.Types.ObjectId,
        ref: 'Category',
        required: true
    },
    taskTemplate: {
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
            max: 3,
            default: 2
        }
    },
    recurrence: {
        type: {
            type: String,
            required: true,
            enum: ['daily', 'weekly', 'monthly', 'custom']
        },
        interval: {
            type: Number,
            default: 1,
            min: 1
        },
        daysOfWeek: [{
            type: Number,
            min: 0,
            max: 6
        }], // 0 = Sunday, 1 = Monday, etc.
        dayOfMonth: {
            type: Number,
            min: 1,
            max: 31
        },
        time: {
            hour: {
                type: Number,
                default: 5,
                min: 0,
                max: 23
            },
            minute: {
                type: Number,
                default: 0,
                min: 0,
                max: 59
            }
        }
    },
    isActive: {
        type: Boolean,
        default: true
    },
    nextRun: {
        type: Date,
        required: true
    },
    lastRun: {
        type: Date
    },
    createdTasksCount: {
        type: Number,
        default: 0
    }
}, {
    timestamps: true
});

// Index for better query performance
templateSchema.index({ isActive: 1, nextRun: 1 });
templateSchema.index({ category: 1, isActive: 1 });

// Method to calculate next run date
templateSchema.methods.calculateNextRun = function() {
    const now = new Date();
    const next = new Date();
    
    // Set to the specified time (default 5 AM for 5 AM day boundary)
    next.setHours(this.recurrence.time.hour, this.recurrence.time.minute, 0, 0);
    
    switch (this.recurrence.type) {
        case 'daily':
            if (next <= now) {
                next.setDate(next.getDate() + this.recurrence.interval);
            }
            break;
            
        case 'weekly':
            // Find next occurrence of specified days
            const targetDays = this.recurrence.daysOfWeek || [1]; // Default Monday
            let found = false;
            
            for (let i = 0; i < 14; i++) { // Check next 2 weeks
                const checkDate = new Date(next);
                checkDate.setDate(checkDate.getDate() + i);
                
                if (targetDays.includes(checkDate.getDay()) && checkDate > now) {
                    next.setDate(next.getDate() + i);
                    found = true;
                    break;
                }
            }
            
            if (!found) {
                next.setDate(next.getDate() + 7 * this.recurrence.interval);
            }
            break;
            
        case 'monthly':
            const targetDay = this.recurrence.dayOfMonth || 1;
            next.setDate(targetDay);
            
            if (next <= now) {
                next.setMonth(next.getMonth() + this.recurrence.interval);
                next.setDate(targetDay);
            }
            break;
            
        default:
            // Custom - add interval days
            if (next <= now) {
                next.setDate(next.getDate() + this.recurrence.interval);
            }
    }
    
    return next;
};

module.exports = mongoose.model('Template', templateSchema);'''
    
    update_file("backend/models/Template.js", template_model)
    
    print("🔗 Creating Template API routes...")
    
    # 2. Create Template routes
    template_routes = '''const express = require('express');
const router = express.Router();
const Template = require('../models/Template');
const Category = require('../models/Category');
const Task = require('../models/Task');

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

// Get all templates
router.get('/', async (req, res) => {
    try {
        const templates = await Template.find()
            .populate('category', 'name color icon')
            .sort({ isActive: -1, name: 1 });
        
        res.json(templates);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// Create new template
router.post('/', async (req, res) => {
    try {
        const { name, description, category, taskTemplate, recurrence } = req.body;
        
        if (!name || !category || !taskTemplate.title || !recurrence.type) {
            return res.status(400).json({ 
                error: 'Name, category, task title, and recurrence type are required' 
            });
        }
        
        // Verify category exists
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
        
        const template = new Template({
            name: name.trim(),
            description: description?.trim(),
            category,
            taskTemplate: {
                title: taskTemplate.title.trim(),
                description: taskTemplate.description?.trim(),
                priority: taskTemplate.priority || 2
            },
            recurrence
        });
        
        // Calculate initial next run
        template.nextRun = template.calculateNextRun();
        
        await template.save();
        await template.populate('category', 'name color icon');
        
        res.status(201).json(template);
    } catch (error) {
        res.status(400).json({ error: error.message });
    }
});

// Update template
router.put('/:id', async (req, res) => {
    try {
        const { id } = req.params;
        const updates = req.body;
        
        // If updating category, verify it exists
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
        
        const template = await Template.findByIdAndUpdate(id, updates, { new: true })
            .populate('category', 'name color icon');
        
        if (!template) {
            return res.status(404).json({ error: 'Template not found' });
        }
        
        // Recalculate next run if recurrence changed
        if (updates.recurrence) {
            template.nextRun = template.calculateNextRun();
            await template.save();
        }
        
        res.json(template);
    } catch (error) {
        res.status(400).json({ error: error.message });
    }
});

// Delete template
router.delete('/:id', async (req, res) => {
    try {
        const { id } = req.params;
        const template = await Template.findByIdAndDelete(id);
        
        if (!template) {
            return res.status(404).json({ error: 'Template not found' });
        }
        
        res.json({ 
            message: 'Template deleted successfully',
            deletedTemplate: template
        });
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// Toggle template active/inactive
router.patch('/:id/toggle', async (req, res) => {
    try {
        const { id } = req.params;
        const template = await Template.findById(id);
        
        if (!template) {
            return res.status(404).json({ error: 'Template not found' });
        }
        
        template.isActive = !template.isActive;
        
        if (template.isActive) {
            // Recalculate next run when reactivating
            template.nextRun = template.calculateNextRun();
        }
        
        await template.save();
        await template.populate('category', 'name color icon');
        
        res.json(template);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// Run template manually (create task now)
router.post('/:id/run', async (req, res) => {
    try {
        const { id } = req.params;
        const template = await Template.findById(id)
            .populate('category', 'name color icon');
        
        if (!template) {
            return res.status(404).json({ error: 'Template not found' });
        }
        
        if (!template.isActive) {
            return res.status(400).json({ 
                error: 'Cannot run inactive template',
                message: 'Please activate the template first'
            });
        }
        
        // Create task from template
        const { todayStart } = getDayBoundaries();
        
        const task = new Task({
            title: template.taskTemplate.title,
            description: template.taskTemplate.description,
            priority: template.taskTemplate.priority,
            category: template.category._id,
            date: todayStart
        });
        
        await task.save();
        await task.populate('category', 'name color icon');
        
        // Update template stats
        template.lastRun = new Date();
        template.createdTasksCount += 1;
        await template.save();
        
        res.json({ 
            message: 'Task created successfully from template',
            task,
            template
        });
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// Process pending templates (called by scheduler)
router.post('/process-pending', async (req, res) => {
    try {
        const now = new Date();
        
        // Find templates that should run
        const pendingTemplates = await Template.find({
            isActive: true,
            nextRun: { $lte: now }
        }).populate('category', 'name color icon');
        
        const results = [];
        
        for (const template of pendingTemplates) {
            try {
                // Check if task already exists for today
                const { todayStart, tomorrowStart } = getDayBoundaries();
                
                const existingTask = await Task.findOne({
                    title: template.taskTemplate.title,
                    category: template.category._id,
                    date: { $gte: todayStart, $lt: tomorrowStart },
                    $or: [{ deleted: { $exists: false } }, { deleted: false }]
                });
                
                if (!existingTask) {
                    // Create task from template
                    const task = new Task({
                        title: template.taskTemplate.title,
                        description: template.taskTemplate.description,
                        priority: template.taskTemplate.priority,
                        category: template.category._id,
                        date: todayStart
                    });
                    
                    await task.save();
                    results.push({
                        template: template.name,
                        task: task.title,
                        status: 'created'
                    });
                } else {
                    results.push({
                        template: template.name,
                        task: template.taskTemplate.title,
                        status: 'skipped (already exists)'
                    });
                }
                
                // Update template
                template.lastRun = now;
                template.nextRun = template.calculateNextRun();
                template.createdTasksCount += 1;
                await template.save();
                
            } catch (error) {
                console.error(`Error processing template ${template.name}:`, error);
                results.push({
                    template: template.name,
                    status: 'error',
                    error: error.message
                });
            }
        }
        
        res.json({
            message: `Processed ${pendingTemplates.length} template${pendingTemplates.length !== 1 ? 's' : ''}`,
            processedCount: pendingTemplates.length,
            results
        });
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// Get template statistics
router.get('/stats', async (req, res) => {
    try {
        const totalTemplates = await Template.countDocuments();
        const activeTemplates = await Template.countDocuments({ isActive: true });
        const inactiveTemplates = totalTemplates - activeTemplates;
        
        // Templates by category
        const categoryStats = await Template.aggregate([
            { $match: { isActive: true } },
            { 
                $lookup: {
                    from: 'categories',
                    localField: 'category',
                    foreignField: '_id',
                    as: 'categoryInfo'
                }
            },
            { $unwind: '$categoryInfo' },
            {
                $group: {
                    _id: '$category',
                    categoryName: { $first: '$categoryInfo.name' },
                    categoryIcon: { $first: '$categoryInfo.icon' },
                    categoryColor: { $first: '$categoryInfo.color' },
                    templateCount: { $sum: 1 },
                    totalTasksCreated: { $sum: '$createdTasksCount' }
                }
            },
            { $sort: { templateCount: -1 } }
        ]);
        
        // Upcoming runs (next 7 days)
        const nextWeek = new Date();
        nextWeek.setDate(nextWeek.getDate() + 7);
        
        const upcomingRuns = await Template.find({
            isActive: true,
            nextRun: { $lte: nextWeek }
        })
        .populate('category', 'name color icon')
        .sort({ nextRun: 1 })
        .limit(10);
        
        res.json({
            summary: {
                totalTemplates,
                activeTemplates,
                inactiveTemplates
            },
            categoryStats,
            upcomingRuns: upcomingRuns.map(template => ({
                _id: template._id,
                name: template.name,
                taskTitle: template.taskTemplate.title,
                category: template.category,
                nextRun: template.nextRun,
                recurrenceType: template.recurrence.type
            }))
        });
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

module.exports = router;'''
    
    update_file("backend/routes/templates.js", template_routes)
    
    print("🔧 Updating server to include template routes...")
    
    # 3. Update server.js to include template routes
    try:
        with open("backend/server.js", 'r') as f:
            server_content = f.read()
        
        # Add template routes import
        if "templateRoutes" not in server_content:
            server_content = server_content.replace(
                "const categoryRoutes = require('./routes/categories');",
                "const categoryRoutes = require('./routes/categories');\nconst templateRoutes = require('./routes/templates');"
            )
            
            # Add template routes usage
            server_content = server_content.replace(
                "app.use('/api/categories', categoryRoutes);",
                "app.use('/api/categories', categoryRoutes);\napp.use('/api/templates', templateRoutes);"
            )
        
        update_file("backend/server.js", server_content)
        
    except Exception as e:
        print(f"⚠️ Could not automatically update server.js: {e}")
    
    print("⏰ Creating scheduler service...")
    
    # 4. Create scheduler service
    scheduler_service = '''const cron = require('node-cron');
const axios = require('axios');

class TemplateScheduler {
    constructor() {
        this.isRunning = false;
    }
    
    start() {
        if (this.isRunning) {
            console.log('⏰ Template scheduler already running');
            return;
        }
        
        // Run every hour to check for pending templates
        this.job = cron.schedule('0 * * * *', async () => {
            try {
                console.log('⏰ Checking for pending templates...');
                
                const response = await axios.post('http://localhost:5000/api/templates/process-pending');
                
                if (response.data.processedCount > 0) {
                    console.log(`✅ Processed ${response.data.processedCount} template${response.data.processedCount !== 1 ? 's' : ''}`);
                    response.data.results.forEach(result => {
                        console.log(`   - ${result.template}: ${result.status}`);
                    });
                } else {
                    console.log('📋 No pending templates to process');
                }
                
            } catch (error) {
                console.error('❌ Error processing templates:', error.message);
            }
        });
        
        // Also run immediately at startup
        setTimeout(async () => {
            try {
                console.log('🚀 Processing templates at startup...');
                const response = await axios.post('http://localhost:5000/api/templates/process-pending');
                console.log(`✅ Startup processing complete: ${response.data.processedCount} template${response.data.processedCount !== 1 ? 's' : ''} processed`);
            } catch (error) {
                console.error('❌ Startup template processing failed:', error.message);
            }
        }, 5000); // Wait 5 seconds for server to be ready
        
        this.isRunning = true;
        console.log('⏰ Template scheduler started - checking every hour');
    }
    
    stop() {
        if (this.job) {
            this.job.stop();
            this.isRunning = false;
            console.log('⏰ Template scheduler stopped');
        }
    }
}

module.exports = new TemplateScheduler();'''
    
    update_file("backend/services/templateScheduler.js", scheduler_service)
    
    print("📦 Installing node-cron dependency...")
    
    # 5. Update package.json to include node-cron
    try:
        with open("backend/package.json", 'r') as f:
            package_data = json.load(f)
        
        if "node-cron" not in package_data.get("dependencies", {}):
            package_data.setdefault("dependencies", {})["node-cron"] = "^3.0.3"
            
            with open("backend/package.json", 'w') as f:
                json.dump(package_data, f, indent=2)
            
            print("✅ Added node-cron to package.json")
    except Exception as e:
        print(f"⚠️ Could not update package.json: {e}")
    
    # 6. Update server.js to start scheduler
    try:
        with open("backend/server.js", 'r') as f:
            server_content = f.read()
        
        # Add scheduler import and start
        if "templateScheduler" not in server_content:
            server_content = server_content.replace(
                "const templateRoutes = require('./routes/templates');",
                "const templateRoutes = require('./routes/templates');\nconst templateScheduler = require('./services/templateScheduler');"
            )
            
            # Start scheduler when server starts
            server_content = server_content.replace(
                "console.log(`Server running on port ${PORT}`);",
                "console.log(`Server running on port ${PORT}`);\n    \n    // Start template scheduler\n    templateScheduler.start();"
            )
        
        update_file("backend/server.js", server_content)
        
    except Exception as e:
        print(f"⚠️ Could not automatically update server.js for scheduler: {e}")
    
    print("📱 Creating Template Manager component...")
    
    # 7. Create Template Manager component
    template_manager = '''import React, { useState, useEffect } from 'react';
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

export default TemplateManager;'''
    
    update_file("frontend/src/components/TemplateManager.js", template_manager)
    
    print("🔄 Updating main App component to include templates...")
    
    # 8. Update App.js to include template management
    try:
        with open("frontend/src/App.js", 'r') as f:
            app_content = f.read()
        
        # Add TemplateManager import
        if "TemplateManager" not in app_content:
            app_content = app_content.replace(
                "import CategoryManager from './components/CategoryManager';",
                "import CategoryManager from './components/CategoryManager';\nimport TemplateManager from './components/TemplateManager';"
            )
        
        # Add state for template manager
        if "showTemplateManager" not in app_content:
            app_content = app_content.replace(
                "const [showCategoryManager, setShowCategoryManager] = useState(false);",
                "const [showCategoryManager, setShowCategoryManager] = useState(false);\n    const [showTemplateManager, setShowTemplateManager] = useState(false);"
            )
        
        # Add template refresh handler
        if "handleTemplateChange" not in app_content:
            app_content = app_content.replace(
                '''const handleCategoryChange = () => {
        // Reload tasks when categories change
        loadTasks();
    };''',
                '''const handleCategoryChange = () => {
        // Reload tasks when categories change
        loadTasks();
    };

    const handleTemplateChange = () => {
        // Reload tasks when templates run
        loadTasks();
    };'''
            )
        
        # Add Templates button to task actions
        if "🔄 Templates" not in app_content:
            app_content = app_content.replace(
                '''                                        <button 
                                            className="btn-secondary"
                                            onClick={() => setShowCategoryManager(true)}
                                        >
                                            📂 Categories
                                        </button>''',
                '''                                        <button 
                                            className="btn-secondary"
                                            onClick={() => setShowCategoryManager(true)}
                                        >
                                            📂 Categories
                                        </button>
                                        <button 
                                            className="btn-secondary"
                                            onClick={() => setShowTemplateManager(true)}
                                        >
                                            🔄 Templates
                                        </button>'''
            )
        
        # Add TemplateManager component to JSX
        if "showTemplateManager &&" not in app_content:
            app_content = app_content.replace(
                '''                        {showCategoryManager && (
                            <CategoryManager
                                isOpen={showCategoryManager}
                                onClose={() => setShowCategoryManager(false)}
                                onCategoryChange={handleCategoryChange}
                            />
                        )}''',
                '''                        {showCategoryManager && (
                            <CategoryManager
                                isOpen={showCategoryManager}
                                onClose={() => setShowCategoryManager(false)}
                                onCategoryChange={handleCategoryChange}
                            />
                        )}
                        
                        {showTemplateManager && (
                            <TemplateManager
                                isOpen={showTemplateManager}
                                onClose={() => setShowTemplateManager(false)}
                                onTemplateChange={handleTemplateChange}
                            />
                        )}'''
            )
        
        update_file("frontend/src/App.js", app_content)
        
    except Exception as e:
        print(f"⚠️ Could not automatically update App.js: {e}")
    
    print("🎨 Adding comprehensive CSS for templates...")
    
    # 9. Add CSS for template features
    template_css = '''
/* Template Management Styles */
.template-manager-overlay {
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

.template-manager-modal {
    background: var(--bg-primary);
    border: 2px solid var(--border-primary);
    border-radius: 12px;
    width: 100%;
    max-width: 800px;
    max-height: 85vh;
    overflow: hidden;
    display: flex;
    flex-direction: column;
    box-shadow: 0 8px 32px var(--shadow);
}

/* Template Stats */
.template-stats {
    display: flex;
    gap: 1rem;
    margin-bottom: 1.5rem;
    padding: 1rem;
    background: var(--bg-secondary);
    border: 1px solid var(--border-secondary);
    border-radius: 8px;
}

.stat-item {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    flex: 1;
}

.stat-icon {
    font-size: 1.5rem;
    color: var(--accent-primary);
}

.stat-number {
    display: block;
    font-family: 'Roboto Mono', monospace;
    font-size: 1.5rem;
    font-weight: 700;
    color: var(--text-primary);
}

.stat-label {
    font-family: 'Roboto Mono', monospace;
    font-size: 0.8rem;
    color: var(--text-tertiary);
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

/* Templates List */
.templates-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1.5rem;
}

.templates-header h3 {
    font-family: 'Roboto Mono', monospace;
    font-size: 1.2rem;
    font-weight: 600;
    color: var(--text-primary);
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

.loading-templates {
    text-align: center;
    padding: 3rem;
    color: var(--text-tertiary);
    font-family: 'Roboto Mono', monospace;
}

.no-templates {
    text-align: center;
    padding: 3rem;
    color: var(--text-tertiary);
}

.no-templates svg {
    color: var(--text-muted);
    margin-bottom: 1rem;
}

.no-templates h4 {
    font-family: 'Roboto Mono', monospace;
    font-size: 1.2rem;
    font-weight: 600;
    color: var(--text-primary);
    margin-bottom: 0.5rem;
}

.no-templates p {
    margin-bottom: 1.5rem;
    line-height: 1.5;
}

.templates-list {
    display: flex;
    flex-direction: column;
    gap: 1rem;
}

.template-card {
    background: var(--bg-secondary);
    border: 1px solid var(--border-secondary);
    border-radius: 8px;
    padding: 1.25rem;
    transition: all 0.3s ease;
}

.template-card:hover {
    border-color: var(--border-primary);
    box-shadow: 0 2px 8px var(--shadow);
}

.template-card.inactive {
    opacity: 0.7;
    background: var(--bg-tertiary);
}

.template-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 1rem;
}

.template-info {
    flex: 1;
}

.template-category {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin-bottom: 0.5rem;
}

.template-category .category-icon {
    width: 24px;
    height: 24px;
    border-radius: 4px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.9rem;
    color: white;
}

.template-category .category-name {
    font-family: 'Roboto Mono', monospace;
    font-size: 0.8rem;
    color: var(--text-tertiary);
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

.template-card h4 {
    font-family: 'Roboto Mono', monospace;
    font-size: 1.1rem;
    font-weight: 600;
    color: var(--text-primary);
    margin-bottom: 0.25rem;
}

.template-description {
    font-size: 0.9rem;
    color: var(--text-tertiary);
    margin: 0;
}

.template-status {
    flex-shrink: 0;
}

.status-badge {
    font-family: 'Roboto Mono', monospace;
    font-size: 0.75rem;
    font-weight: 700;
    padding: 0.25rem 0.5rem;
    border-radius: 4px;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

.status-badge.active {
    background: var(--success-bg);
    color: var(--success-text);
    border: 1px solid var(--success-border);
}

.status-badge.inactive {
    background: var(--bg-tertiary);
    color: var(--text-muted);
    border: 1px solid var(--border-tertiary);
}

.template-details {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
    margin-bottom: 1rem;
}

.detail-item {
    display: flex;
    gap: 0.5rem;
    font-family: 'Roboto Mono', monospace;
    font-size: 0.85rem;
}

.detail-item strong {
    color: var(--text-secondary);
    min-width: 80px;
    flex-shrink: 0;
}

.next-run {
    color: var(--accent-primary);
    font-weight: 600;
}

.template-actions {
    display: flex;
    gap: 0.5rem;
    justify-content: flex-end;
}

.toggle-btn,
.run-btn,
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

.toggle-btn.active {
    color: var(--success-text);
    border-color: var(--success-border);
}

.toggle-btn.active:hover {
    background: var(--success-bg);
}

.toggle-btn.inactive {
    color: var(--text-muted);
    border-color: var(--border-tertiary);
}

.toggle-btn.inactive:hover {
    background: var(--bg-tertiary);
}

.run-btn:hover {
    color: var(--accent-primary);
    border-color: var(--accent-primary);
    background: rgba(59, 130, 246, 0.1);
}

.edit-btn:hover {
    border-color: var(--border-primary);
    color: var(--text-primary);
    background: var(--bg-tertiary);
}

.delete-btn:hover {
    border-color: #ff6b6b;
    color: #ff6b6b;
    background: rgba(255, 107, 107, 0.1);
}

/* Upcoming Runs */
.upcoming-runs {
    margin-top: 1.5rem;
    padding: 1rem;
    background: var(--bg-secondary);
    border: 1px solid var(--border-secondary);
    border-radius: 8px;
}

.upcoming-runs h4 {
    font-family: 'Roboto Mono', monospace;
    font-size: 1rem;
    font-weight: 600;
    color: var(--text-primary);
    margin-bottom: 1rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

.upcoming-list {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
}

.upcoming-item {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 0.5rem;
    background: var(--bg-primary);
    border-radius: 6px;
    font-family: 'Roboto Mono', monospace;
    font-size: 0.85rem;
}

.category-dot {
    width: 12px;
    height: 12px;
    border-radius: 50%;
    flex-shrink: 0;
}

.task-title {
    flex: 1;
    color: var(--text-primary);
}

.next-time {
    color: var(--text-tertiary);
    font-weight: 600;
}

/* Template Form */
.template-form {
    background: var(--bg-secondary);
    padding: 1.5rem;
    border-radius: 8px;
    border: 1px solid var(--border-secondary);
    max-height: 70vh;
    overflow-y: auto;
}

.template-form h3 {
    font-family: 'Roboto Mono', monospace;
    font-size: 1.2rem;
    font-weight: 600;
    color: var(--text-primary);
    margin-bottom: 1.5rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

.template-form fieldset {
    border: 1px solid var(--border-secondary);
    border-radius: 6px;
    padding: 1rem;
    margin-bottom: 1rem;
}

.template-form legend {
    font-family: 'Roboto Mono', monospace;
    font-size: 0.9rem;
    font-weight: 600;
    color: var(--text-secondary);
    padding: 0 0.5rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

.task-template-section {
    background: var(--bg-tertiary);
}

.recurrence-section {
    background: var(--bg-primary);
}

.form-row {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1rem;
}

.day-selector {
    display: grid;
    grid-template-columns: repeat(7, 1fr);
    gap: 0.25rem;
    margin-top: 0.5rem;
}

.day-btn {
    background: var(--bg-primary);
    border: 1px solid var(--border-tertiary);
    padding: 0.5rem 0.25rem;
    border-radius: 4px;
    cursor: pointer;
    font-family: 'Roboto Mono', monospace;
    font-size: 0.8rem;
    font-weight: 600;
    color: var(--text-tertiary);
    transition: all 0.3s ease;
}

.day-btn:hover {
    border-color: var(--border-primary);
    color: var(--text-primary);
}

.day-btn.active {
    background: var(--accent-primary);
    border-color: var(--accent-primary);
    color: white;
}

/* Mobile responsive */
@media (max-width: 768px) {
    .template-manager-modal {
        margin: 0;
        max-height: 95vh;
        border-radius: 12px 12px 0 0;
    }
    
    .template-stats {
        flex-direction: column;
        gap: 0.75rem;
    }
    
    .template-header {
        flex-direction: column;
        align-items: stretch;
        gap: 1rem;
    }
    
    .template-actions {
        justify-content: center;
    }
    
    .form-row {
        grid-template-columns: 1fr;
    }
    
    .day-selector {
        grid-template-columns: repeat(4, 1fr);
    }
    
    .upcoming-item {
        flex-direction: column;
        align-items: stretch;
        text-align: center;
    }
}

@media (max-width: 480px) {
    .template-form {
        padding: 1rem;
    }
    
    .day-selector {
        grid-template-columns: repeat(3, 1fr);
    }
    
    .template-actions {
        flex-wrap: wrap;
        gap: 0.5rem;
    }
    
    .template-actions button {
        flex: 1;
        min-width: calc(50% - 0.25rem);
    }
}'''
    
    # Append to existing CSS
    with open("frontend/src/styles/App.css", 'a') as f:
        f.write(template_css)
    
    print("✅ Added comprehensive template CSS")
    
    # 10. Create installation script for node-cron
    install_script = '''#!/bin/bash
echo "📦 Installing node-cron dependency..."

cd backend
npm install node-cron@^3.0.3

if [ $? -eq 0 ]; then
    echo "✅ node-cron installed successfully"
else
    echo "❌ Failed to install node-cron"
    echo "Please run manually: cd backend && npm install node-cron"
fi

cd ..'''
    
    with open("install_cron.sh", 'w') as f:
        f.write(install_script)
    os.chmod("install_cron.sh", 0o755)
    
    # 11. Create restart script
    restart_script = f'''#!/bin/bash
echo "🔄 Restarting ENTROPY with Smart Recurring Templates..."
echo "Backup created: {backup_dir}"
echo ""

# Install dependencies first
echo "📦 Installing dependencies..."
./install_cron.sh

# Kill existing processes
pkill -f "node.*server.js" || true
pkill -f "react-scripts" || true

# Wait a moment
sleep 2

echo "✅ Smart Recurring Templates System Implemented:"
echo "  🔄 Create unlimited recurring task templates"
echo "  ⏰ Automatic task generation at 5 AM boundaries"
echo "  📅 Daily, weekly, monthly, and custom schedules"
echo "  🎯 Category integration for organized automation"
echo "  📊 Template statistics and upcoming runs preview"
echo "  ⚡ Manual template execution and toggle control"
echo ""
echo "🎯 Getting Started:"
echo "  1. Click 'Templates' button to create your first template"
echo "  2. Set up Daily Planning, Weekly Reviews, etc."
echo "  3. Templates automatically create tasks at scheduled times"
echo "  4. Check 'Upcoming Runs' to see what's scheduled"
echo ""
echo "🛡️  Backup & Restore:"
echo "  📦 Backup created: {backup_dir}"
echo "  🔄 To restore: python3 ../restore_backup.py {backup_dir}"
echo ""

# Start the application
./start.sh'''
    
    with open("restart_templates.sh", 'w') as f:
        f.write(restart_script)
    os.chmod("restart_templates.sh", 0o755)
    
    print(f"\n🎉 Smart Recurring Templates System Complete!")
    print("=" * 55)
    print("✅ Backend: Template model, CRUD APIs, and scheduler")
    print("✅ Database: Recurring task automation system")
    print("✅ Frontend: Professional template management UI")
    print("✅ Scheduler: Hourly checks for pending templates")
    print("✅ Integration: Works with categories and 5 AM boundaries")
    print("✅ Mobile: Responsive design for all devices")
    
    print(f"\n📦 BACKUP CREATED: {backup_dir}")
    print(f"🔄 Restore command: python3 ../restore_backup.py {backup_dir}")
    
    print("\n🔄 PROFESSIONAL AUTOMATION FEATURES:")
    print("• Create templates for daily, weekly, monthly routines")
    print("• Automatic task generation at your 5 AM day boundary")
    print("• Category integration for organized workflows")
    print("• Template statistics and upcoming runs preview")
    print("• Manual template execution and activation controls")
    print("• Duplicate prevention (won't create if task exists)")
    
    print("\n🎯 PERFECT FOR YOUR WORKFLOW:")
    print("• Daily Planning template (creates planning task at 5 AM)")
    print("• Weekly Review template (every Monday morning)")
    print("• Monthly Goals template (1st of each month)")
    print("• Custom routines (every 2 days, specific days, etc.)")
    
    print("\n🚀 To start with templates:")
    print("./restart_templates.sh")
    
    print("\n⚡ Your ENTROPY is now a professional automation powerhouse! ⚡")

if __name__ == "__main__":
    main()
