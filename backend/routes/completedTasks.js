const express = require('express');
const router = express.Router();
const Task = require('../models/Task');

// Get completed tasks with completion timestamps (history)
router.get('/completed/history', async (req, res) => {
    try {
        const days = parseInt(req.query.days) || 30; // default 30 days
        const startDate = new Date();
        startDate.setDate(startDate.getDate() - days);
        startDate.setHours(0, 0, 0, 0);

        const completedTasks = await Task.find({
            completed: true,
            completedAt: { $gte: startDate }
        }).sort({ completedAt: -1 });

        // Group by date for better organization
        const groupedTasks = completedTasks.reduce((acc, task) => {
            const date = task.completedAt ? 
                task.completedAt.toISOString().split('T')[0] : 
                task.createdAt.toISOString().split('T');
            
            if (!acc[date]) {
                acc[date] = [];
            }
            acc[date].push(task);
            return acc;
        }, {});

        res.json({
            tasks: completedTasks,
            grouped: groupedTasks,
            totalCount: completedTasks.length
        });
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// Get completion stats
router.get('/completed/stats', async (req, res) => {
    try {
        const days = parseInt(req.query.days) || 30;
        const startDate = new Date();
        startDate.setDate(startDate.getDate() - days);
        startDate.setHours(0, 0, 0, 0);

        const completedTasks = await Task.find({
            completed: true,
            completedAt: { $gte: startDate }
        });

        const stats = {
            totalCompleted: completedTasks.length,
            avgPerDay: (completedTasks.length / days).toFixed(1),
            byPriority: {
                high: completedTasks.filter(t => t.priority === 1).length,
                medium: completedTasks.filter(t => t.priority === 2).length,
                low: completedTasks.filter(t => t.priority === 3).length
            }
        };

        res.json(stats);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

module.exports = router;