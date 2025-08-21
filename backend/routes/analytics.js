const express = require('express');
const router = express.Router();
const auth = require('../middleware/auth');
const Task = require('../models/Task');
const Category = require('../models/Category');

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

// Get comprehensive analytics overview
router.get('/overview', auth, async (req, res) => {
    try {
        const now = new Date();
        const { todayStart } = getDayBoundaries(now);
        
        // Calculate date ranges
        const weekStart = new Date(todayStart);
        weekStart.setDate(weekStart.getDate() - 7);
        
        const monthStart = new Date(todayStart);
        monthStart.setDate(monthStart.getDate() - 30);
        
        // Total statistics
        const totalTasks = await Task.countDocuments({
            user: req.user.id,
            $or: [{ deleted: { $exists: false } }, { deleted: false }]
        });
        
        const totalCompleted = await Task.countDocuments({
            user: req.user.id,
            completed: true,
            $or: [{ deleted: { $exists: false } }, { deleted: false }]
        });
        
        // Today's stats
        const todayTasks = await Task.countDocuments({
            user: req.user.id,
            date: { $gte: todayStart },
            $or: [{ deleted: { $exists: false } }, { deleted: false }]
        });
        
        const todayCompleted = await Task.countDocuments({
            user: req.user.id,
            date: { $gte: todayStart },
            completed: true,
            $or: [{ deleted: { $exists: false } }, { deleted: false }]
        });
        
        // Weekly stats
        const weeklyTasks = await Task.countDocuments({
            user: req.user.id,
            date: { $gte: weekStart },
            $or: [{ deleted: { $exists: false } }, { deleted: false }]
        });
        
        const weeklyCompleted = await Task.countDocuments({
            user: req.user.id,
            date: { $gte: weekStart },
            completed: true,
            $or: [{ deleted: { $exists: false } }, { deleted: false }]
        });
        
        // Monthly stats
        const monthlyTasks = await Task.countDocuments({
            user: req.user.id,
            date: { $gte: monthStart },
            $or: [{ deleted: { $exists: false } }, { deleted: false }]
        });
        
        const monthlyCompleted = await Task.countDocuments({
            user: req.user.id,
            date: { $gte: monthStart },
            completed: true,
            $or: [{ deleted: { $exists: false } }, { deleted: false }]
        });
        
        // Calculate completion rates
        const todayCompletionRate = todayTasks === 0 ? 0 : Math.round((todayCompleted / todayTasks) * 100);
        const weeklyCompletionRate = weeklyTasks === 0 ? 0 : Math.round((weeklyCompleted / weeklyTasks) * 100);
        const monthlyCompletionRate = monthlyTasks === 0 ? 0 : Math.round((monthlyCompleted / monthlyTasks) * 100);
        const overallCompletionRate = totalTasks === 0 ? 0 : Math.round((totalCompleted / totalTasks) * 100);
        
        res.json({
            overview: {
                totalTasks,
                totalCompleted,
                overallCompletionRate
            },
            periods: {
                today: {
                    tasks: todayTasks,
                    completed: todayCompleted,
                    completionRate: todayCompletionRate
                },
                weekly: {
                    tasks: weeklyTasks,
                    completed: weeklyCompleted,
                    completionRate: weeklyCompletionRate
                },
                monthly: {
                    tasks: monthlyTasks,
                    completed: monthlyCompleted,
                    completionRate: monthlyCompletionRate
                }
            }
        });
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// Get category breakdown analytics
router.get('/categories', auth, async (req, res) => {
    try {
        const categories = await Category.find({ user: req.user.id, isActive: true });
        
        const categoryStats = await Promise.all(
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
                
                const pendingTasks = totalTasks - completedTasks;
                const completionRate = totalTasks === 0 ? 0 : Math.round((completedTasks / totalTasks) * 100);
                
                // Priority breakdown
                const priorityBreakdown = await Task.aggregate([
                    {
                        $match: {
                            user: req.user.id,
                            category: category._id,
                            $or: [{ deleted: { $exists: false } }, { deleted: false }]
                        }
                    },
                    {
                        $group: {
                            _id: '$priority',
                            total: { $sum: 1 },
                            completed: { 
                                $sum: { $cond: ['$completed', 1, 0] } 
                            }
                        }
                    },
                    { $sort: { _id: 1 } }
                ]);
                
                return {
                    categoryId: category._id,
                    categoryName: category.name,
                    categoryColor: category.color,
                    categoryIcon: category.icon,
                    totalTasks,
                    completedTasks,
                    pendingTasks,
                    completionRate,
                    priorityBreakdown
                };
            })
        );
        
        // Sort by total tasks descending
        categoryStats.sort((a, b) => b.totalTasks - a.totalTasks);
        
        res.json(categoryStats);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// Get daily trends (last 7 days)
router.get('/trends/daily', auth, async (req, res) => {
    try {
        const trends = [];
        const today = new Date();
        
        for (let i = 6; i >= 0; i--) {
            const date = new Date(today);
            date.setDate(date.getDate() - i);
            
            const { todayStart, tomorrowStart } = getDayBoundaries(date);
            
            const tasksCreated = await Task.countDocuments({
                user: req.user.id,
                date: { $gte: todayStart, $lt: tomorrowStart },
                $or: [{ deleted: { $exists: false } }, { deleted: false }]
            });
            
            const tasksCompleted = await Task.countDocuments({
                user: req.user.id,
                date: { $gte: todayStart, $lt: tomorrowStart },
                completed: true,
                $or: [{ deleted: { $exists: false } }, { deleted: false }]
            });
            
            const completionRate = tasksCreated === 0 ? 0 : Math.round((tasksCompleted / tasksCreated) * 100);
            
            trends.push({
                date: todayStart.toISOString().split('T')[0],
                dateLabel: todayStart.toLocaleDateString('en-US', { 
                    month: 'short', 
                    day: 'numeric' 
                }),
                tasksCreated,
                tasksCompleted,
                completionRate
            });
        }
        
        res.json(trends);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// Get productivity patterns
router.get('/patterns', auth, async (req, res) => {
    try {
        const now = new Date();
        const monthStart = new Date(now);
        monthStart.setDate(monthStart.getDate() - 30);
        
        // Priority distribution
        const priorityStats = await Task.aggregate([
            {
                $match: {
                    user: req.user.id,
                    date: { $gte: monthStart },
                    $or: [{ deleted: { $exists: false } }, { deleted: false }]
                }
            },
            {
                $group: {
                    _id: '$priority',
                    total: { $sum: 1 },
                    completed: { 
                        $sum: { $cond: ['$completed', 1, 0] } 
                    }
                }
            },
            { $sort: { _id: 1 } }
        ]);
        
        const priorityLabels = { 1: 'High', 2: 'Medium', 3: 'Low' };
        const priorityColors = { 1: '#ff6b6b', 2: '#ffd93d', 3: '#6bcf7f' };
        
        const priorityData = priorityStats.map(stat => ({
            priority: stat._id,
            label: priorityLabels[stat._id] || 'Unknown',
            color: priorityColors[stat._id] || '#gray',
            total: stat.total,
            completed: stat.completed,
            completionRate: stat.total === 0 ? 0 : Math.round((stat.completed / stat.total) * 100)
        }));
        
        // Completion streaks
        const recentCompletions = await Task.find({
            user: req.user.id,
            completed: true,
            completedAt: { $exists: true },
            $or: [{ deleted: { $exists: false } }, { deleted: false }]
        })
        .sort({ completedAt: -1 })
        .limit(100)
        .select('completedAt');
        
        const streakData = calculateCompletionStreaks(recentCompletions);
        
        // Most productive categories
        const productiveCategories = await Task.aggregate([
            {
                $match: {
                    user: req.user.id,
                    date: { $gte: monthStart },
                    completed: true,
                    $or: [{ deleted: { $exists: false } }, { deleted: false }]
                }
            },
            {
                $group: {
                    _id: '$category',
                    completedCount: { $sum: 1 }
                }
            },
            {
                $lookup: {
                    from: 'categories',
                    localField: '_id',
                    foreignField: '_id',
                    as: 'category'
                }
            },
            { $unwind: '$category' },
            {
                $project: {
                    categoryName: '$category.name',
                    categoryIcon: '$category.icon',
                    categoryColor: '$category.color',
                    completedCount: 1
                }
            },
            { $sort: { completedCount: -1 } },
            { $limit: 5 }
        ]);
        
        res.json({
            priorityDistribution: priorityData,
            completionStreaks: streakData,
            productiveCategories
        });
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// Helper function to calculate completion streaks
function calculateCompletionStreaks(completions) {
    if (!completions || completions.length === 0) {
        return {
            currentStreak: 0,
            longestStreak: 0,
            totalCompletions: 0
        };
    }
    
    const dates = completions.map(c => {
        const date = new Date(c.completedAt);
        return date.toISOString().split('T')[0];
    });
    
    const uniqueDates = [...new Set(dates)].sort().reverse();
    
    let currentStreak = 0;
    let longestStreak = 0;
    let tempStreak = 1;
    
    const today = new Date().toISOString().split('T')[0];
    
    // Calculate current streak
    if (uniqueDates[0] === today) {
        currentStreak = 1;
        for (let i = 1; i < uniqueDates.length; i++) {
            const prevDate = new Date(uniqueDates[i-1]);
            const currDate = new Date(uniqueDates[i]);
            const diffTime = Math.abs(prevDate - currDate);
            const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
            
            if (diffDays === 1) {
                currentStreak++;
            } else {
                break;
            }
        }
    }
    
    // Calculate longest streak
    for (let i = 1; i < uniqueDates.length; i++) {
        const prevDate = new Date(uniqueDates[i-1]);
        const currDate = new Date(uniqueDates[i]);
        const diffTime = Math.abs(prevDate - currDate);
        const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
        
        if (diffDays === 1) {
            tempStreak++;
        } else {
            longestStreak = Math.max(longestStreak, tempStreak);
            tempStreak = 1;
        }
    }
    
    longestStreak = Math.max(longestStreak, tempStreak);
    
    return {
        currentStreak,
        longestStreak,
        totalCompletions: completions.length,
        uniqueDays: uniqueDates.length
    };
}

module.exports = router;
