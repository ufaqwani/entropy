const express = require('express');
const router = express.Router();
const auth = require('../middleware/auth');
const Template = require('../models/Template');
const Category = require('../models/Category');
const Task = require('../models/Task');
const mongoose = require('mongoose');

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
router.get('/', auth, async (req, res) => {
    try {
        const templates = await Template.find({ user: req.user.id })
            .populate('category', 'name color icon')
            .sort({ isActive: -1, name: 1 });
        
        res.json(templates);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// Create new template
router.post('/', auth, async (req, res) => {
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
            user: req.user.id,
            isActive: true 
        });
        
        if (!categoryDoc) {
            return res.status(400).json({ 
                error: 'Invalid category',
                message: 'Selected category does not exist or is inactive'
            });
        }
        
        const template = new Template({
            user: req.user.id,
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
router.put('/:id', auth, async (req, res) => {
    try {
        const { id } = req.params;
        const updates = req.body;
        
        // If updating category, verify it exists
        if (updates.category) {
            const categoryDoc = await Category.findOne({ 
                _id: updates.category, 
                user: req.user.id,
                isActive: true 
            });
            
            if (!categoryDoc) {
                return res.status(400).json({ 
                    error: 'Invalid category',
                    message: 'Selected category does not exist or is inactive'
                });
            }
        }
        
        const template = await Template.findOneAndUpdate({ _id: id, user: req.user.id }, updates, { new: true })
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
router.delete('/:id', auth, async (req, res) => {
    try {
        const { id } = req.params;
        const template = await Template.findOneAndDelete({ _id: id, user: req.user.id });
        
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
router.patch('/:id/toggle', auth, async (req, res) => {
    try {
        const { id } = req.params;
        const template = await Template.findOne({ _id: id, user: req.user.id });
        
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
router.post('/:id/run', auth, async (req, res) => {
    try {
        const { id } = req.params;
        const template = await Template.findOne({ _id: id, user: req.user.id })
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
            user: req.user.id,
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
router.post('/process-pending', auth, async (req, res) => {
    try {
        const now = new Date();
        
        // Find templates that should run
        const pendingTemplates = await Template.find({
            user: req.user.id,
            isActive: true,
            nextRun: { $lte: now }
        }).populate('category', 'name color icon');
        
        const results = [];
        
        for (const template of pendingTemplates) {
            try {
                // Check if task already exists for today
                const { todayStart, tomorrowStart } = getDayBoundaries();
                
                const existingTask = await Task.findOne({
                    user: req.user.id,
                    title: template.taskTemplate.title,
                    category: template.category._id,
                    date: { $gte: todayStart, $lt: tomorrowStart },
                    $or: [{ deleted: { $exists: false } }, { deleted: false }]
                });
                
                if (!existingTask) {
                    // Create task from template
                    const task = new Task({
                        user: req.user.id,
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
router.get('/stats', auth, async (req, res) => {
    try {
        const totalTemplates = await Template.countDocuments({ user: req.user.id });
        const activeTemplates = await Template.countDocuments({ user: req.user.id, isActive: true });
        const inactiveTemplates = totalTemplates - activeTemplates;
        
        // Templates by category
        const categoryStats = await Template.aggregate([
            { $match: { user: new mongoose.Types.ObjectId(req.user.id), isActive: true } },
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
            user: req.user.id,
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

module.exports = router;
