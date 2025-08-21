const express = require('express');
const router = express.Router();
const auth = require('../middleware/auth');
const Progress = require('../models/Progress');
const Task = require('../models/Task');

// Submit daily audit
router.post('/audit', auth, async (req, res) => {
    try {
        const { date, success } = req.body;
        const auditDate = new Date(date);
        auditDate.setHours(0, 0, 0, 0);
        
        // Get task statistics for the day
        const nextDay = new Date(auditDate);
        nextDay.setDate(nextDay.getDate() + 1);
        
        const totalTasks = await Task.countDocuments({
            user: req.user.id,
            date: { $gte: auditDate, $lt: nextDay }
        });
        
        const completedTasks = await Task.countDocuments({
            user: req.user.id,
            date: { $gte: auditDate, $lt: nextDay },
            completed: true
        });
        
        const completionRate = totalTasks > 0 ? Math.round((completedTasks / totalTasks) * 100) : 0;
        
        // Create or update progress record
        const progress = await Progress.findOneAndUpdate(
            { user: req.user.id, date: auditDate },
            {
                success,
                totalTasks,
                completedTasks,
                completionRate
            },
            { upsert: true, new: true }
        );
        
        res.json(progress);
    } catch (error) {
        res.status(400).json({ error: error.message });
    }
});

// Get progress history
router.get('/history', auth, async (req, res) => {
    try {
        const { days = 30 } = req.query;
        const startDate = new Date();
        startDate.setDate(startDate.getDate() - parseInt(days));
        startDate.setHours(0, 0, 0, 0);
        
        const progress = await Progress.find({
            user: req.user.id,
            date: { $gte: startDate }
        }).sort({ date: -1 });
        
        res.json(progress);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// Get today's progress
router.get('/today', auth, async (req, res) => {
    try {
        const today = new Date();
        today.setHours(0, 0, 0, 0);
        const tomorrow = new Date(today);
        tomorrow.setDate(tomorrow.getDate() + 1);
        
        // Get tasks for today
        const totalTasks = await Task.countDocuments({
            user: req.user.id,
            date: { $gte: today, $lt: tomorrow }
        });
        
        const completedTasks = await Task.countDocuments({
            user: req.user.id,
            date: { $gte: today, $lt: tomorrow },
            completed: true
        });
        
        const completionRate = totalTasks > 0 ? Math.round((completedTasks / totalTasks) * 100) : 0;
        
        // Check if progress record exists
        const existingProgress = await Progress.findOne({ user: req.user.id, date: today });
        
        res.json({
            totalTasks,
            completedTasks,
            completionRate,
            hasAudit: !!existingProgress,
            success: existingProgress ? existingProgress.success : null
        });
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

module.exports = router;
