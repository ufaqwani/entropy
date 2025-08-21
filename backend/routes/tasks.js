const express = require('express');
const router = express.Router();
const auth = require('../middleware/auth');
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
router.get('/today', auth, async (req, res) => {
    try {
        const { todayStart, tomorrowStart, dayAfterTomorrowStart } = getDayBoundaries();
        
        // Get today's tasks with category information
        const todayTasks = await Task.find({
            user: req.user.id,
            date: { $gte: todayStart, $lt: tomorrowStart },
            $and: [
                { $or: [{ moved: { $exists: false } }, { moved: false }] },
                { $or: [{ deleted: { $exists: false } }, { deleted: false }] }
            ]
        })
        .populate('category', 'name color icon')
        .sort({ priority: 1, _id: 1 });
        
        // Get tomorrow's tasks with category information
        const tomorrowTasks = await Task.find({
            user: req.user.id,
            date: { $gte: tomorrowStart, $lt: dayAfterTomorrowStart },
            $or: [{ deleted: { $exists: false } }, { deleted: false }]
        })
        .populate('category', 'name color icon')
        .sort({ priority: 1, _id: 1 });
        
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
router.post('/', auth, async (req, res) => {
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
            user: req.user.id,
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
            user: req.user.id,
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
router.put('/:id', auth, async (req, res) => {
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
        
        const task = await Task.findOneAndUpdate({ _id: id, user: req.user.id }, updates, { new: true })
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
router.delete('/:id', auth, async (req, res) => {
    try {
        const { id } = req.params;
        
        const taskToDelete = await Task.findOne({ _id: id, user: req.user.id }).populate('category', 'name color icon');
        if (!taskToDelete) {
            return res.status(404).json({ error: 'Task not found' });
        }
        
        const { todayStart, tomorrowStart, dayAfterTomorrowStart } = getDayBoundaries();
        
        const isTomorrowTask = taskToDelete.date >= tomorrowStart && taskToDelete.date < dayAfterTomorrowStart;
        
        if (isTomorrowTask) {
            const relatedMovedTask = await Task.findOne({
                user: req.user.id,
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
router.post('/move-to-tomorrow', auth, async (req, res) => {
    try {
        const { todayStart, tomorrowStart } = getDayBoundaries();
        
        const uncompletedTasks = await Task.find({
            user: req.user.id,
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
                user: req.user.id,
                title: task.title,
                category: task.category._id,
                date: { $gte: tomorrowStart, $lt: dayAfterTomorrowStart },
                $or: [{ deleted: { $exists: false } }, { deleted: false }]
            });
            
            if (!existingTomorrowTask) {
                const newTask = new Task({
                    user: req.user.id,
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
router.get('/day-info', auth, async (req, res) => {
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


// Move task from tomorrow back to today - FIXED VERSION
router.post('/move-back-to-today/:id', auth, async (req, res) => {
    try {
        const { id } = req.params;
        const { todayStart, tomorrowStart } = getDayBoundaries();
        
        // Find the task to move back
        const task = await Task.findOne({ _id: id, user: req.user.id }).populate('category', 'name color icon');
        
        if (!task) {
            return res.status(404).json({ error: 'Task not found' });
        }
        
        // Verify it's currently a tomorrow task
        const dayAfterTomorrow = new Date(tomorrowStart);
        dayAfterTomorrow.setDate(dayAfterTomorrow.getDate() + 1);
        
        const isTomorrowTask = task.date >= tomorrowStart && task.date < dayAfterTomorrow;
        
        if (!isTomorrowTask) {
            return res.status(400).json({ 
                error: 'Invalid operation',
                message: 'This task is not scheduled for tomorrow'
            });
        }
        
        // CRITICAL FIX: Delete any existing tasks with same title in today's period
        // This includes moved tasks that are hidden from view
        await Task.deleteMany({
            user: req.user.id,
            title: task.title,
            category: task.category._id,
            date: { $gte: todayStart, $lt: tomorrowStart },
            _id: { $ne: id } // Don't delete the current task
        });
        
        // Move the task back to today
        task.date = todayStart;
        task.originalTaskId = undefined; // Clear any reference
        await task.save();
        
        res.json({
            message: 'Task moved back to today successfully',
            task: task,
            movedFrom: 'tomorrow',
            movedTo: 'today'
        });
        
    } catch (error) {
        console.error('Error moving task back to today:', error);
        res.status(500).json({ error: error.message });
    }
});



// Reorder tasks and auto-update priorities
router.post('/reorder-tasks', auth, async (req, res) => {
    try {
        const { orderedTaskIds } = req.body;
        
        if (!orderedTaskIds || !Array.isArray(orderedTaskIds)) {
            return res.status(400).json({ 
                error: 'Invalid input',
                message: 'orderedTaskIds must be an array'
            });
        }
        
        if (orderedTaskIds.length === 0) {
            return res.status(400).json({ 
                error: 'Empty array',
                message: 'orderedTaskIds cannot be empty'
            });
        }
        
        // Validate all task IDs exist
        const tasks = await Task.find({ _id: { $in: orderedTaskIds }, user: req.user.id });
        
        if (tasks.length !== orderedTaskIds.length) {
            return res.status(400).json({ 
                error: 'Invalid task IDs',
                message: 'Some task IDs do not exist' 
            });
        }
        
        // Update priorities based on position (1 = highest priority)
        const updatePromises = orderedTaskIds.map((taskId, index) => {
            const newPriority = index + 1; // Position 0 -> Priority 1 (highest)
            return Task.findByIdAndUpdate(taskId, { 
                priority: Math.min(newPriority, 3) // Cap at 3 (low priority)
            });
        });
        
        await Promise.all(updatePromises);
        
        // Fetch updated tasks to return
        const updatedTasks = await Task.find({ _id: { $in: orderedTaskIds }, user: req.user.id })
            .populate('category', 'name color icon')
            .sort({ priority: 1, _id: 1 });
        
        res.json({
            message: 'Task order updated successfully',
            updatedTasks,
            newPriorities: orderedTaskIds.map((id, index) => ({
                taskId: id,
                newPriority: Math.min(index + 1, 3)
            }))
        });
        
    } catch (error) {
        console.error('Error reordering tasks:', error);
        res.status(500).json({ error: error.message });
    }
});


// Move task up in priority
router.post('/move-task-up/:id', auth, async (req, res) => {
    try {
        const { id } = req.params;
        const { todayStart, tomorrowStart } = getDayBoundaries();
        
        console.log(`[Backend] Move Up: Task ID ${id}`);

        // Get today's tasks
        const todayTasks = await Task.find({
            user: req.user.id,
            date: { $gte: todayStart, $lt: tomorrowStart },
            $and: [
                { $or: [{ moved: { $exists: false } }, { moved: false }] },
                { $or: [{ deleted: { $exists: false } }, { deleted: false }] }
            ]
        }).sort({ priority: 1, _id: 1 });
        
        console.log('[Backend] Tasks before move (Move Up):', todayTasks.map(t => ({ id: t._id, title: t.title, priority: t.priority })));

        // Find current task
        const currentIndex = todayTasks.findIndex(task => task._id.toString() === id);
        
        console.log('[Backend] Current Index (Move Up):', currentIndex);

        if (currentIndex === -1) {
            return res.status(404).json({ error: 'Task not found' });
        }
        
        if (currentIndex === 0) {
            return res.status(400).json({ 
                error: 'Already at top',
                message: 'Task is already the highest priority'
            });
        }
        
        // Swap with previous task
        const currentTask = todayTasks[currentIndex];
        const previousTask = todayTasks[currentIndex - 1];
        
        console.log(`[Backend] Swapping (Move Up): Current Task ${currentTask.title} (P${currentTask.priority}) with Previous Task ${previousTask.title} (P${previousTask.priority})`);

        await Promise.all([
            Task.findByIdAndUpdate(currentTask._id, { priority: previousTask.priority }),
            Task.findByIdAndUpdate(previousTask._id, { priority: currentTask.priority })
        ]);
        
        console.log(`[Backend] Priorities updated (Move Up): ${currentTask.title} to P${previousTask.priority}, ${previousTask.title} to P${currentTask.priority}`);

        // Return updated tasks
        const updatedTasks = await Task.find({
            user: req.user.id,
            date: { $gte: todayStart, $lt: tomorrowStart },
            $and: [
                { $or: [{ moved: { $exists: false } }, { moved: false }] },
                { $or: [{ deleted: { $exists: false } }, { deleted: false }] }
            ]
        }).populate('category', 'name color icon').sort({ priority: 1, _id: 1 });
        
        console.log('[Backend] Tasks after move and re-fetch (Move Up):', updatedTasks.map(t => ({ id: t._id, title: t.title, priority: t.priority })));

        res.json({
            message: 'Task moved up successfully',
            tasks: updatedTasks
        });
        
    } catch (error) {
        console.error('Error moving task up:', error);
        res.status(500).json({ error: error.message });
    }
});


// Move task down in priority
router.post('/move-task-down/:id', auth, async (req, res) => {
    try {
        const { id } = req.params;
        const { todayStart, tomorrowStart } = getDayBoundaries();
        
        console.log(`[Backend] Move Down: Task ID ${id}`);

        // Get today's tasks
        const todayTasks = await Task.find({
            user: req.user.id,
            date: { $gte: todayStart, $lt: tomorrowStart },
            $and: [
                { $or: [{ moved: { $exists: false } }, { moved: false }] },
                { $or: [{ deleted: { $exists:false } }, { deleted: false }] }
            ]
        }).sort({ priority: 1, _id: 1 });
        
        console.log('[Backend] Tasks before move:', todayTasks.map(t => ({ id: t._id, title: t.title, priority: t.priority })));

        // Find current task
        const currentIndex = todayTasks.findIndex(task => task._id.toString() === id);
        
        if (currentIndex === -1) {
            return res.status(404).json({ error: 'Task not found' });
        }
        
        if (currentIndex === todayTasks.length - 1) {
            return res.status(400).json({ 
                error: 'Already at bottom',
                message: 'Task is already the lowest priority'
            });
        }
        
        // Swap with next task
        const currentTask = todayTasks[currentIndex];
        const nextTask = todayTasks[currentIndex + 1];
        
        console.log(`[Backend] Swapping: Current Task ${currentTask.title} (P${currentTask.priority}) with Next Task ${nextTask.title} (P${nextTask.priority})`);

        await Promise.all([
            Task.findByIdAndUpdate(currentTask._id, { priority: nextTask.priority }),
            Task.findByIdAndUpdate(nextTask._id, { priority: currentTask.priority })
        ]);
        
        console.log(`[Backend] Priorities updated: ${currentTask.title} to P${nextTask.priority}, ${nextTask.title} to P${currentTask.priority}`);

        // Return updated tasks
        const updatedTasks = await Task.find({
            user: req.user.id,
            date: { $gte: todayStart, $lt: tomorrowStart },
            $and: [
                { $or: [{ moved: { $exists: false } }, { moved: false }] },
                { $or: [{ deleted: { $exists: false } }, { deleted: false }] }
            ]
        }).populate('category', 'name color icon').sort({ priority: 1, _id: 1 });
        
        console.log('[Backend] Tasks after move and re-fetch:', updatedTasks.map(t => ({ id: t._id, title: t.title, priority: t.priority })));

        res.json({
            message: 'Task moved down successfully',
            tasks: updatedTasks
        });
        
    } catch (error) {
        console.error('Error moving task down:', error);
        res.status(500).json({ error: error.message });
    }
});

module.exports = router;
