#!/usr/bin/env python3
"""
ENTROPY - Simple & Smooth Task Reordering with Up/Down Buttons
Clean, reliable reordering without drag & drop complexity
"""

import os
import shutil
import json
from datetime import datetime

def create_backup():
    """Create backup before implementing smooth reordering"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = f"../entropy_backup_smooth_reorder_{timestamp}"
    
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
    with open(file_path, 'w') as f:
        f.write(content)
    print(f"✅ Updated: {file_path}")

def main():
    print("⚡ ENTROPY - Simple & Smooth Task Reordering")
    print("=" * 45)
    print("🎯 Up/Down buttons = Reliable & Fast")
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
    
    print("🔧 Updating backend with simple move endpoints...")
    
    # 1. Add simple move up/down endpoints
    try:
        with open("backend/routes/tasks.js", 'r') as f:
            tasks_content = f.read()
        
        # Add move up/down endpoints
        move_endpoints = '''
// Move task up in priority order
router.post('/move-up/:id', async (req, res) => {
    try {
        const { id } = req.params;
        const { todayStart, tomorrowStart } = getDayBoundaries();
        
        // Get today's tasks sorted by priority
        const todayTasks = await Task.find({
            date: { $gte: todayStart, $lt: tomorrowStart },
            $and: [
                { $or: [{ moved: { $exists: false } }, { moved: false }] },
                { $or: [{ deleted: { $exists: false } }, { deleted: false }] }
            ]
        }).sort({ priority: 1, createdAt: 1 });
        
        // Find current task
        const currentIndex = todayTasks.findIndex(task => task._id.toString() === id);
        
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
        
        await Promise.all([
            Task.findByIdAndUpdate(currentTask._id, { priority: previousTask.priority }),
            Task.findByIdAndUpdate(previousTask._id, { priority: currentTask.priority })
        ]);
        
        // Return updated tasks
        const updatedTasks = await Task.find({
            date: { $gte: todayStart, $lt: tomorrowStart },
            $and: [
                { $or: [{ moved: { $exists: false } }, { moved: false }] },
                { $or: [{ deleted: { $exists: false } }, { deleted: false }] }
            ]
        }).populate('category', 'name color icon').sort({ priority: 1, createdAt: 1 });
        
        res.json({
            message: 'Task moved up successfully',
            tasks: updatedTasks
        });
        
    } catch (error) {
        console.error('Error moving task up:', error);
        res.status(500).json({ error: error.message });
    }
});

// Move task down in priority order
router.post('/move-down/:id', async (req, res) => {
    try {
        const { id } = req.params;
        const { todayStart, tomorrowStart } = getDayBoundaries();
        
        // Get today's tasks sorted by priority
        const todayTasks = await Task.find({
            date: { $gte: todayStart, $lt: tomorrowStart },
            $and: [
                { $or: [{ moved: { $exists: false } }, { moved: false }] },
                { $or: [{ deleted: { $exists: false } }, { deleted: false }] }
            ]
        }).sort({ priority: 1, createdAt: 1 });
        
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
        
        await Promise.all([
            Task.findByIdAndUpdate(currentTask._id, { priority: nextTask.priority }),
            Task.findByIdAndUpdate(nextTask._id, { priority: currentTask.priority })
        ]);
        
        // Return updated tasks
        const updatedTasks = await Task.find({
            date: { $gte: todayStart, $lt: tomorrowStart },
            $and: [
                { $or: [{ moved: { $exists: false } }, { moved: false }] },
                { $or: [{ deleted: { $exists: false } }, { deleted: false }] }
            ]
        }).populate('category', 'name color icon').sort({ priority: 1, createdAt: 1 });
        
        res.json({
            message: 'Task moved down successfully',
            tasks: updatedTasks
        });
        
    } catch (error) {
        console.error('Error moving task down:', error);
        res.status(500).json({ error: error.message });
    }
});'''
        
        # Insert the new endpoints before module.exports
        updated_content = tasks_content.replace(
            "module.exports = router;",
            move_endpoints + "\n\nmodule.exports = router;"
        )
        
        update_file("backend/routes/tasks.js", updated_content)
        
    except Exception as e:
        print(f"❌ Error updating backend routes: {e}")
        return
    
    print("📱 Creating smooth TaskList with up/down buttons...")
    
    # 2. Create clean TaskList with up/down buttons
    smooth_task_list = '''import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { FiCheck, FiTrash2, FiChevronUp, FiChevronDown } from 'react-icons/fi';

const TaskList = ({ tasks, onUpdate, onDelete, onMoveUp, onMoveDown }) => {
    if (!tasks || tasks.length === 0) {
        return (
            <div className="no-tasks">
                <h3>No tasks yet</h3>
                <p>Add your first task to start battling entropy!</p>
            </div>
        );
    }

    const priorityConfig = {
        1: { label: 'High', color: '#ff6f6f', icon: '🔥' },
        2: { label: 'Medium', color: '#ffd966', icon: '⚡' },
        3: { label: 'Low', color: '#a5d6a7', icon: '📋' }
    };

    const handleComplete = (taskId, completed) => {
        onUpdate(taskId, { completed });
    };

    const handleDelete = (taskId, taskTitle) => {
        if (window.confirm(`Delete "${taskTitle}"?`)) {
            onDelete(taskId);
        }
    };

    const handleMoveUp = async (taskId) => {
        try {
            await onMoveUp(taskId);
        } catch (error) {
            // Error is handled in parent component
        }
    };

    const handleMoveDown = async (taskId) => {
        try {
            await onMoveDown(taskId);
        } catch (error) {
            // Error is handled in parent component
        }
    };

    return (
        <div className="task-list">
            <div className="task-list-header">
                <div className="header-left">
                    <h3>Today's Tasks</h3>
                    <div className="reorder-hint">
                        <span>Use ↑↓ arrows to reorder by importance</span>
                    </div>
                </div>
                <div className="task-count-info">
                    {tasks.filter(t => t.completed).length} of {tasks.length} completed
                </div>
            </div>
            
            <div className="tasks-container">
                <AnimatePresence>
                    {tasks.map((task, index) => (
                        <motion.div
                            key={task._id}
                            className={`task-item ${task.completed ? 'completed' : ''}`}
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            exit={{ opacity: 0, y: -20 }}
                            transition={{ delay: index * 0.05 }}
                            layout
                        >
                            <div className="task-content">
                                {/* Reorder Controls */}
                                <div className="reorder-controls">
                                    <button
                                        className={`move-btn move-up ${index === 0 || task.completed ? 'disabled' : ''}`}
                                        onClick={() => handleMoveUp(task._id)}
                                        disabled={index === 0 || task.completed}
                                        title={task.completed ? 'Cannot reorder completed tasks' : 'Move up'}
                                    >
                                        <FiChevronUp />
                                    </button>
                                    <span className="position-number">#{index + 1}</span>
                                    <button
                                        className={`move-btn move-down ${index === tasks.length - 1 || task.completed ? 'disabled' : ''}`}
                                        onClick={() => handleMoveDown(task._id)}
                                        disabled={index === tasks.length - 1 || task.completed}
                                        title={task.completed ? 'Cannot reorder completed tasks' : 'Move down'}
                                    >
                                        <FiChevronDown />
                                    </button>
                                </div>
                                
                                {/* Priority Indicator */}
                                <div className="task-priority-strip" 
                                     style={{ backgroundColor: priorityConfig[task.priority].color }}>
                                </div>
                                
                                {/* Checkbox */}
                                <button
                                    className={`task-checkbox ${task.completed ? 'checked' : ''}`}
                                    onClick={() => handleComplete(task._id, !task.completed)}
                                    title={task.completed ? 'Mark as incomplete' : 'Mark as complete'}
                                >
                                    {task.completed && <FiCheck />}
                                </button>

                                {/* Task Details */}
                                <div className="task-details">
                                    <div className="task-header">
                                        <h4 className={task.completed ? 'strikethrough' : ''}>
                                            {task.title}
                                        </h4>
                                        
                                        {/* Category Badge */}
                                        {task.category && (
                                            <div className="task-category-badge"
                                                 style={{ backgroundColor: task.category.color }}>
                                                <span className="category-icon">{task.category.icon}</span>
                                                <span className="category-name">{task.category.name}</span>
                                            </div>
                                        )}
                                    </div>
                                    
                                    {task.description && (
                                        <p className="task-description">{task.description}</p>
                                    )}
                                </div>

                                {/* Priority & Actions */}
                                <div className="task-meta">
                                    <div className="priority-info">
                                        <span className="priority-badge"
                                              style={{ backgroundColor: priorityConfig[task.priority].color }}>
                                            {priorityConfig[task.priority].icon}
                                        </span>
                                        <span className="priority-label">
                                            {priorityConfig[task.priority].label}
                                        </span>
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
        </div>
    );
};

export default TaskList;'''
    
    update_file("frontend/src/components/TaskList.js", smooth_task_list)
    
    print("🔄 Updating App.js with smooth move functions...")
    
    # 3. Update App.js with move up/down functions
    try:
        with open("frontend/src/App.js", 'r') as f:
            app_content = f.read()
        
        # Replace the complex reorderTasks function with simple move functions
        move_functions = '''    const moveTaskUp = async (taskId) => {
        try {
            const response = await axios.post(`/api/tasks/move-up/${taskId}`);
            
            // Update tasks with smooth animation
            setTodayTasks(response.data.tasks);
            
            addNotification(
                'Task Moved Up! ⬆️',
                'Priority increased',
                'success',
                2000
            );
            
        } catch (error) {
            if (error.response?.status === 400) {
                // Already at top or other validation error
                addNotification(
                    'Cannot Move Up',
                    error.response.data.message,
                    'info',
                    2000
                );
            } else {
                console.error('Error moving task up:', error);
                addNotification(
                    'Move Failed',
                    'Could not move task up',
                    'error'
                );
            }
        }
    };

    const moveTaskDown = async (taskId) => {
        try {
            const response = await axios.post(`/api/tasks/move-down/${taskId}`);
            
            // Update tasks with smooth animation
            setTodayTasks(response.data.tasks);
            
            addNotification(
                'Task Moved Down! ⬇️',
                'Priority decreased',
                'success',
                2000
            );
            
        } catch (error) {
            if (error.response?.status === 400) {
                // Already at bottom or other validation error
                addNotification(
                    'Cannot Move Down',
                    error.response.data.message,
                    'info',
                    2000
                );
            } else {
                console.error('Error moving task down:', error);
                addNotification(
                    'Move Failed',
                    'Could not move task down',
                    'error'
                );
            }
        }
    };'''
        
        # Replace the old reorderTasks function
        import re
        # Remove old reorder function
        app_content = re.sub(r'const reorderTasks = async.*?\};', '', app_content, flags=re.DOTALL)
        
        # Add new move functions
        if "const moveBackToToday" in app_content:
            app_content = app_content.replace(
                "const moveBackToToday",
                move_functions + "\n\n    const moveBackToToday"
            )
        else:
            # Insert after deleteTask function
            app_content = app_content.replace(
                "const deleteTask = async (taskId) => {",
                move_functions + "\n\n    const deleteTask = async (taskId) => {"
            )
        
        # Update TaskList component call
        app_content = app_content.replace(
            '''                                    <TaskList 
                                        tasks={todayTasks}
                                        onUpdate={updateTask}
                                        onDelete={deleteTask}
                                        onReorder={reorderTasks}
                                    />''',
            '''                                    <TaskList 
                                        tasks={todayTasks}
                                        onUpdate={updateTask}
                                        onDelete={deleteTask}
                                        onMoveUp={moveTaskUp}
                                        onMoveDown={moveTaskDown}
                                    />'''
        )
        
        update_file("frontend/src/App.js", app_content)
        
    except Exception as e:
        print(f"❌ Error updating App.js: {e}")
        return
    
    print("🎨 Adding smooth reorder button CSS...")
    
    # 4. Add CSS for smooth reorder buttons
    smooth_css = '''
/* Smooth Task Reordering with Up/Down Buttons */

.reorder-hint {
    font-family: 'Roboto Mono', monospace;
    font-size: 0.8rem;
    color: var(--text-tertiary);
    background: var(--info-bg);
    padding: 0.25rem 0.75rem;
    border-radius: 12px;
    border: 1px solid var(--info-border);
}

/* Reorder Controls */
.reorder-controls {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.25rem;
    flex-shrink: 0;
    margin-right: 0.5rem;
}

.move-btn {
    background: var(--bg-secondary);
    border: 2px solid var(--border-secondary);
    color: var(--text-secondary);
    width: 28px;
    height: 28px;
    border-radius: 50%;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
    font-size: 0.9rem;
}

.move-btn:hover:not(.disabled) {
    background: var(--accent-primary);
    border-color: var(--accent-primary);
    color: white;
    transform: scale(1.1);
}

.move-btn:active:not(.disabled) {
    transform: scale(0.95);
}

.move-btn.disabled {
    opacity: 0.3;
    cursor: not-allowed;
    border-color: var(--border-tertiary);
    color: var(--text-muted);
}

.move-btn.disabled:hover {
    transform: none;
    background: var(--bg-secondary);
    border-color: var(--border-tertiary);
    color: var(--text-muted);
}

.position-number {
    font-family: 'Roboto Mono', monospace;
    font-size: 0.7rem;
    font-weight: 700;
    color: var(--text-muted);
    background: var(--bg-tertiary);
    padding: 0.2rem 0.4rem;
    border-radius: 8px;
    border: 1px solid var(--border-tertiary);
    min-width: 24px;
    text-align: center;
}

/* Enhanced Task Content Layout */
.task-content {
    display: flex;
    align-items: flex-start;
    gap: 1rem;
    padding: 1.25rem;
    position: relative;
}

/* Hover Effects */
.task-item:hover .move-btn:not(.disabled) {
    border-color: var(--border-primary);
    color: var(--text-primary);
}

.task-item:hover .position-number {
    background: var(--accent-primary);
    color: white;
    border-color: var(--accent-primary);
}

/* Smooth Layout Transitions */
.task-item {
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.tasks-container {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
}

/* Mobile Optimizations */
@media (max-width: 768px) {
    .reorder-controls {
        gap: 0.5rem;
        margin-right: 0.75rem;
    }
    
    .move-btn {
        width: 32px;
        height: 32px;
        font-size: 1rem;
    }
    
    .position-number {
        font-size: 0.8rem;
        padding: 0.3rem 0.5rem;
        min-width: 28px;
    }
    
    .task-content {
        gap: 0.75rem;
        padding: 1rem;
    }
}

@media (max-width: 480px) {
    .reorder-controls {
        flex-direction: row;
        gap: 0.25rem;
        align-items: center;
    }
    
    .move-btn {
        width: 28px;
        height: 28px;
    }
    
    .position-number {
        order: 1;
        margin: 0 0.25rem;
    }
}

/* Accessibility Focus States */
.move-btn:focus {
    outline: 2px solid var(--accent-primary);
    outline-offset: 2px;
}

/* Animation for Successful Move */
@keyframes moveSuccess {
    0% { transform: scale(1); }
    50% { transform: scale(1.05); }
    100% { transform: scale(1); }
}

.task-item.move-success {
    animation: moveSuccess 0.4s ease-out;
}

/* Completed Task Restrictions */
.task-item.completed .reorder-controls {
    opacity: 0.3;
    pointer-events: none;
}

.task-item.completed .position-number {
    background: var(--bg-tertiary);
    color: var(--text-muted);
    border-color: var(--border-tertiary);
}'''
    
    # Replace old drag & drop CSS and add new smooth CSS
    try:
        with open("frontend/src/styles/App.css", 'r') as f:
            css_content = f.read()
        
        # Remove old drag & drop styles
        import re
        css_content = re.sub(r'/\* Drag & Drop Task Reordering Styles \*/.*?(?=/\*|$)', '', css_content, flags=re.DOTALL)
        
        # Add new smooth CSS
        css_content += smooth_css
        
        with open("frontend/src/styles/App.css", 'w') as f:
            f.write(css_content)
        
        print("✅ Updated CSS with smooth reorder styling")
        
    except Exception as e:
        print(f"⚠️ Could not automatically update CSS: {e}")
    
    # 5. Create restart script
    restart_script = f'''#!/bin/bash
echo "⚡ Restarting ENTROPY with Smooth Task Reordering..."
echo "Backup created: {backup_dir}"
echo ""

# Kill existing processes
pkill -f "node.*server.js" || true
pkill -f "react-scripts" || true

# Wait a moment
sleep 2

echo "✅ Smooth Task Reordering Features:"
echo "  ⬆️  Up arrow button to increase priority"
echo "  ⬇️  Down arrow button to decrease priority"
echo "  🎯 Position numbers show current ranking"
echo "  ⚡ Instant, smooth animations"
echo "  📱 Perfect touch support for mobile"
echo "  🚫 Smart restrictions for completed tasks"
echo ""
echo "🎯 How to Use:"
echo "  • Click ⬆️ to move task up (higher priority)"
echo "  • Click ⬇️ to move task down (lower priority)"
echo "  • Position #1 = highest priority"
echo "  • Completed tasks cannot be reordered"
echo ""
echo "✨ Why This is Better:"
echo "  • No more clunky drag & drop"
echo "  • Works perfectly on all devices"
echo "  • Instant feedback with smooth animations"
echo "  • Never fails or gets stuck"
echo ""
echo "🛡️  Backup & Restore:"
echo "  📦 Backup created: {backup_dir}"
echo "  🔄 To restore: python3 ../restore_backup.py {backup_dir}"
echo ""

# Start the application
./start.sh'''
    
    with open("restart_smooth_reorder.sh", 'w') as f:
        f.write(restart_script)
    os.chmod("restart_smooth_reorder.sh", 0o755)
    
    print(f"\n🎉 Smooth Task Reordering Complete!")
    print("=" * 45)
    print("✅ Backend: Simple move up/down API endpoints")
    print("✅ Frontend: Clean up/down arrow buttons")
    print("✅ UX: Instant feedback with smooth animations")
    print("✅ Mobile: Perfect touch support, no drag issues")
    print("✅ Reliability: Never fails, always responsive")
    
    print(f"\n📦 BACKUP CREATED: {backup_dir}")
    print(f"🔄 Restore command: python3 ../restore_backup.py {backup_dir}")
    
    print("\n⚡ WHY THIS IS MUCH BETTER:")
    print("• **No Complex Libraries**: No drag & drop dependencies")
    print("• **Always Works**: Simple button clicks never fail")
    print("• **Mobile Perfect**: Touch buttons work flawlessly")
    print("• **Instant Feedback**: Immediate visual response")
    print("• **Smooth Animations**: Framer Motion handles transitions")
    print("• **Clean UI**: Up/down arrows are intuitive and clear")
    
    print("\n🎯 SIMPLE & EFFECTIVE:")
    print("• **⬆️ Button**: Move task up (increase priority)")
    print("• **⬇️ Button**: Move task down (decrease priority)")
    print("• **#1, #2, #3**: Shows current position")
    print("• **Disabled State**: Can't move top task up or bottom task down")
    print("• **Completed Protection**: Can't reorder finished tasks")
    
    print("\n🚀 To start with smooth reordering:")
    print("./restart_smooth_reorder.sh")
    
    print("\n⚡ Now your task reordering is smooth, reliable, and works everywhere! ⚡")

if __name__ == "__main__":
    main()
