const express = require('express');
const router = express.Router();
const auth = require('../middleware/auth');
const Category = require('../models/Category');
const Task = require('../models/Task');

// Get all active categories
router.get('/', auth, async (req, res) => {
    try {
        const categories = await Category.find({ user: req.user.id, isActive: true })
            .sort({ name: 1 });
        
        // Count tasks in each category
        const categoriesWithCounts = await Promise.all(
            categories.map(async (category) => {
                const taskCount = await Task.countDocuments({ 
                    user: req.user.id,
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
router.post('/', auth, async (req, res) => {
    try {
        const { name, description, color, icon } = req.body;
        
        if (!name || !name.trim()) {
            return res.status(400).json({ error: 'Category name is required' });
        }
        
        // Check for duplicate names (case-insensitive)
        const existingCategory = await Category.findOne({
            user: req.user.id,
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
            user: req.user.id,
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
router.put('/:id', auth, async (req, res) => {
    try {
        const { id } = req.params;
        const updates = req.body;
        
        // If updating name, check for duplicates
        if (updates.name) {
            const existingCategory = await Category.findOne({
                user: req.user.id,
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
        
        const category = await Category.findOneAndUpdate({ _id: id, user: req.user.id }, updates, { new: true });
        
        if (!category) {
            return res.status(404).json({ error: 'Category not found' });
        }
        
        res.json(category);
    } catch (error) {
        res.status(400).json({ error: error.message });
    }
});

// Delete category (soft delete - mark as inactive)
router.delete('/:id', auth, async (req, res) => {
    try {
        const { id } = req.params;
        
        // Check if category has tasks
        const taskCount = await Task.countDocuments({ 
            user: req.user.id,
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
        const category = await Category.findOneAndUpdate(
            { _id: id, user: req.user.id }, 
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
router.get('/stats', auth, async (req, res) => {
    try {
        const categories = await Category.find({ user: req.user.id, isActive: true });
        
        const stats = await Promise.all(
            categories.map(async (category) => {
                const totalTasks = await Task.countDocuments({ 
                    user: req.user.id,
                    category: category._id,
                    $or: [{ deleted: { $exists: false } }, { deleted: false }]
                });
                
                const completedTasks = await Task.countDocuments({ 
                    user: req.user.id,
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

module.exports = router;
