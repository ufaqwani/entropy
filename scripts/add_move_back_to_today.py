#!/usr/bin/env python3
"""
ENTROPY - Add Move Back to Today Functionality
Allows moving tomorrow's tasks back to today for flexible workflow
"""

import os
import shutil
import json
from datetime import datetime

def create_backup():
    """Create backup before adding move-back functionality"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = f"../entropy_backup_move_back_{timestamp}"
    
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
    print("⬅️  ENTROPY - Add Move Back to Today Functionality")
    print("=" * 50)
    print("🔄 Flexible task movement: Tomorrow → Today")
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
    
    print("🔧 Adding move-back-to-today endpoint to backend...")
    
    # 1. Update tasks.js to add move-back-to-today endpoint
    try:
        with open("backend/routes/tasks.js", 'r') as f:
            tasks_content = f.read()
        
        # Add the new endpoint before the module.exports line
        move_back_endpoint = '''
// Move task from tomorrow back to today
router.post('/move-back-to-today/:id', async (req, res) => {
    try {
        const { id } = req.params;
        const { todayStart, tomorrowStart } = getDayBoundaries();
        
        // Find the task to move back
        const task = await Task.findById(id).populate('category', 'name color icon');
        
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
        
        // Check if a similar task already exists in today's list
        const existingTodayTask = await Task.findOne({
            title: task.title,
            category: task.category._id,
            date: { $gte: todayStart, $lt: tomorrowStart },
            $or: [{ deleted: { $exists: false } }, { deleted: false }],
            _id: { $ne: id }
        });
        
        if (existingTodayTask) {
            return res.status(409).json({
                error: 'Duplicate task exists',
                message: `A similar task "${task.title}" already exists in today's list`,
                existingTask: existingTodayTask
            });
        }
        
        // Move the task back to today
        task.date = todayStart;
        await task.save();
        
        // If this task was originally moved from today (has originalTaskId), 
        // we need to clean up the original moved task
        if (task.originalTaskId) {
            try {
                await Task.findByIdAndDelete(task.originalTaskId);
            } catch (error) {
                // Original task might already be deleted, that's okay
                console.log('Original moved task not found or already deleted');
            }
            
            // Clear the originalTaskId since it's now back to today
            task.originalTaskId = undefined;
            await task.save();
        }
        
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
});'''
        
        # Insert the new endpoint before module.exports
        updated_content = tasks_content.replace(
            "module.exports = router;",
            move_back_endpoint + "\n\nmodule.exports = router;"
        )
        
        update_file("backend/routes/tasks.js", updated_content)
        
    except Exception as e:
        print(f"❌ Error updating backend routes: {e}")
        return
    
    print("📱 Updating TomorrowTasks component with move-back functionality...")
    
    # 2. Update TomorrowTasks component to include move-back button
    updated_tomorrow_tasks = '''import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { FiClock, FiArrowRight, FiArrowLeft, FiCalendar, FiTrash2, FiCheck } from 'react-icons/fi';

const TomorrowTasks = ({ tasks, onUpdate, onDelete, onMoveBack }) => {
    if (!tasks || tasks.length === 0) {
        return (
            <div className="tomorrow-empty">
                <FiCalendar className="empty-icon" />
                <h4>No tasks for tomorrow</h4>
                <p>Tasks moved from today will appear here</p>
            </div>
        );
    }

    const priorityConfig = {
        1: { label: 'High', color: '#ff6f6f' },
        2: { label: 'Medium', color: '#ffd966' },
        3: { label: 'Low', color: '#a5d6a7' }
    };

    const handleDelete = (taskId, taskTitle) => {
        if (window.confirm(`Delete "${taskTitle}" from tomorrow's tasks?`)) {
            onDelete(taskId);
        }
    };

    const handleComplete = (taskId, updates) => {
        onUpdate(taskId, updates);
    };

    const handleMoveBack = (taskId, taskTitle) => {
        if (window.confirm(`Move "${taskTitle}" back to today's tasks?`)) {
            onMoveBack(taskId);
        }
    };

    return (
        <div className="tomorrow-tasks">
            <div className="tomorrow-header">
                <FiArrowRight className="tomorrow-icon" />
                <h3>Tomorrow's Tasks</h3>
                <span className="task-count">{tasks.length}</span>
            </div>
            
            <div className="tomorrow-list">
                <AnimatePresence>
                    {tasks.map((task, index) => (
                        <motion.div
                            key={task._id}
                            initial={{ opacity: 0, x: 20 }}
                            animate={{ opacity: 1, x: 0 }}
                            exit={{ opacity: 0, x: -20 }}
                            transition={{ delay: index * 0.05 }}
                            className={`tomorrow-task-item ${task.completed ? 'completed' : ''}`}
                        >
                            <div className="task-preview">
                                <div 
                                    className="priority-indicator"
                                    style={{ backgroundColor: priorityConfig[task.priority].color }}
                                ></div>
                                
                                <button
                                    className={`task-checkbox ${task.completed ? 'checked' : ''}`}
                                    onClick={() => handleComplete(task._id, { completed: !task.completed })}
                                    title={task.completed ? 'Mark as incomplete' : 'Mark as complete'}
                                >
                                    {task.completed && <FiCheck />}
                                </button>
                                
                                <div className="task-content">
                                    <h5 className={task.completed ? 'strikethrough' : ''}>{task.title}</h5>
                                    {task.description && (
                                        <p className="task-description">{task.description}</p>
                                    )}
                                    {task.category && (
                                        <div className="task-category-info">
                                            <span 
                                                className="category-badge"
                                                style={{ backgroundColor: task.category.color }}
                                            >
                                                {task.category.icon} {task.category.name}
                                            </span>
                                        </div>
                                    )}
                                </div>
                                
                                <div className="task-meta">
                                    <span className="priority-label">
                                        {priorityConfig[task.priority].label}
                                    </span>
                                    <div className="task-actions">
                                        <button
                                            className="move-back-btn"
                                            onClick={() => handleMoveBack(task._id, task.title)}
                                            title={`Move "${task.title}" back to today`}
                                        >
                                            <FiArrowLeft />
                                        </button>
                                        <FiClock className="time-icon" title="Scheduled for tomorrow" />
                                        <button
                                            className="delete-btn"
                                            onClick={() => handleDelete(task._id, task.title)}
                                            title={`Delete "${task.title}"`}
                                        >
                                            <FiTrash2 />
                                        </button>
                                    </div>
                                </div>
                            </div>
                        </motion.div>
                    ))}
                </AnimatePresence>
            </div>
            
            <div className="tomorrow-footer">
                <p className="tomorrow-note">
                    💡 These tasks will become today's tasks tomorrow
                </p>
                <p className="move-back-hint">
                    ⬅️ Changed your mind? Use the arrow button to move tasks back to today
                </p>
            </div>
        </div>
    );
};

export default TomorrowTasks;'''
    
    update_file("frontend/src/components/TomorrowTasks.js", updated_tomorrow_tasks)
    
    print("🔄 Updating main App component to handle move-back functionality...")
    
    # 3. Update App.js to handle move-back functionality
    try:
        with open("frontend/src/App.js", 'r') as f:
            app_content = f.read()
        
        # Add moveBackToToday function
        move_back_function = '''    const moveBackToToday = async (taskId) => {
        try {
            const response = await axios.post(`/api/tasks/move-back-to-today/${taskId}`);
            
            // Remove task from tomorrow's state
            setTomorrowTasks(prev => prev.filter(task => task._id !== taskId));
            
            // Add task to today's state
            const movedTask = response.data.task;
            setTodayTasks(prev => [...prev, movedTask]);
            
            addNotification(
                'Task Moved Back! ⬅️',
                `"${movedTask.title}" moved back to today's tasks`,
                'success',
                4000
            );
            
        } catch (error) {
            console.error('Error moving task back to today:', error);
            
            if (error.response?.status === 409) {
                addNotification(
                    'Duplicate Task Detected! ⚠️',
                    error.response.data.message,
                    'warning',
                    6000
                );
            } else {
                addNotification(
                    'Move Back Failed',
                    'Could not move task back to today. Please try again.',
                    'error'
                );
            }
        }
    };'''
        
        # Find a good place to insert the function (after moveUncompletedTasks)
        app_content = app_content.replace(
            "    };",
            "    };\n\n" + move_back_function,
            1  # Replace only the first occurrence
        )
        
        # Update TomorrowTasks component call to include onMoveBack prop
        app_content = app_content.replace(
            '''                                    <TomorrowTasks 
                                        tasks={tomorrowTasks}
                                        onUpdate={updateTask}
                                        onDelete={deleteTask}
                                    />''',
            '''                                    <TomorrowTasks 
                                        tasks={tomorrowTasks}
                                        onUpdate={updateTask}
                                        onDelete={deleteTask}
                                        onMoveBack={moveBackToToday}
                                    />'''
        )
        
        update_file("frontend/src/App.js", app_content)
        
    except Exception as e:
        print(f"❌ Error updating App.js: {e}")
        return
    
    print("🎨 Adding CSS for move-back functionality...")
    
    # 4. Add CSS for the new move-back button and styling
    move_back_css = '''
/* Move Back to Today Functionality */
.move-back-btn {
    background: transparent;
    border: none;
    color: var(--text-muted);
    cursor: pointer;
    padding: 0.25rem;
    border-radius: 4px;
    transition: all 0.3s ease;
    font-size: 0.9rem;
}

.move-back-btn:hover {
    color: var(--accent-primary);
    background: rgba(59, 130, 246, 0.1);
    transform: translateX(-2px);
}

.move-back-btn:active {
    transform: translateX(-1px);
}

.tomorrow-footer .move-back-hint {
    font-family: 'Roboto Mono', monospace;
    font-size: 0.75rem;
    color: var(--text-muted);
    text-align: center;
    margin: 0.5rem 0 0 0;
    padding: 0.5rem;
    background: var(--info-bg);
    border: 1px solid var(--info-border);
    border-radius: 6px;
}

.task-category-info {
    margin-top: 0.5rem;
}

.category-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.25rem;
    padding: 0.2rem 0.5rem;
    border-radius: 4px;
    font-family: 'Roboto Mono', monospace;
    font-size: 0.7rem;
    font-weight: 600;
    color: white;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

/* Enhanced task actions layout */
.tomorrow-task-item .task-actions {
    display: flex;
    align-items: center;
    gap: 0.25rem;
}

/* Animation for move-back button */
@keyframes moveBack {
    0% { transform: translateX(0); }
    50% { transform: translateX(-3px); }
    100% { transform: translateX(0); }
}

.move-back-btn:hover {
    animation: moveBack 0.6s ease-in-out;
}

/* Mobile improvements */
@media (max-width: 768px) {
    .tomorrow-task-item .task-actions {
        flex-direction: column;
        gap: 0.5rem;
        align-items: center;
    }
    
    .move-back-btn,
    .delete-btn {
        padding: 0.5rem;
        font-size: 1rem;
    }
    
    .tomorrow-footer .move-back-hint {
        font-size: 0.7rem;
        padding: 0.75rem;
    }
}

/* Notification enhancement for move-back */
.notification.success .notification-icon {
    animation: pulse 2s infinite;
}

@keyframes pulse {
    0% { transform: scale(1); }
    50% { transform: scale(1.1); }
    100% { transform: scale(1); }
}'''
    
    # Append to existing CSS
    with open("frontend/src/styles/App.css", 'a') as f:
        f.write(move_back_css)
    
    print("✅ Added move-back CSS styling")
    
    # 5. Create restart script
    restart_script = f'''#!/bin/bash
echo "⬅️  Restarting ENTROPY with Move Back to Today..."
echo "Backup created: {backup_dir}"
echo ""

# Kill existing processes
pkill -f "node.*server.js" || true
pkill -f "react-scripts" || true

# Wait a moment
sleep 2

echo "✅ Move Back to Today Functionality Added:"
echo "  ⬅️  Move tomorrow tasks back to today with one click"
echo "  🔍 Duplicate detection prevents task conflicts"
echo "  ⚡ Instant state updates in both sections"
echo "  🎨 Visual feedback with animations and notifications"
echo "  📱 Mobile-optimized controls and layout"
echo ""
echo "🔄 How to Use:"
echo "  1. Find a task in Tomorrow's section"
echo "  2. Click the ⬅️ arrow button next to it"
echo "  3. Task instantly moves back to Today's list"
echo "  4. Complete it today or move it back to tomorrow again"
echo ""
echo "🛡️  Backup & Restore:"
echo "  📦 Backup created: {backup_dir}"
echo "  🔄 To restore: python3 ../restore_backup.py {backup_dir}"
echo ""

# Start the application
./start.sh'''
    
    with open("restart_move_back.sh", 'w') as f:
        f.write(restart_script)
    os.chmod("restart_move_back.sh", 0o755)
    
    print(f"\n🎉 Move Back to Today Functionality Complete!")
    print("=" * 50)
    print("✅ Backend: New endpoint for moving tasks back to today")
    print("✅ Frontend: Move-back button in tomorrow tasks")
    print("✅ State Management: Proper task movement between lists")
    print("✅ Duplicate Prevention: Warns if similar task exists")
    print("✅ User Experience: Visual feedback and animations")
    print("✅ Mobile Support: Touch-friendly controls")
    
    print(f"\n📦 BACKUP CREATED: {backup_dir}")
    print(f"🔄 Restore command: python3 ../restore_backup.py {backup_dir}")
    
    print("\n⬅️ FLEXIBLE WORKFLOW FEATURES:")
    print("• Move tasks from tomorrow back to today instantly")
    print("• Duplicate detection prevents task conflicts")
    print("• Visual move-back button with hover animations")
    print("• Smart cleanup of original moved tasks")
    print("• Success notifications with task details")
    
    print("\n🔄 PERFECT FOR REAL WORKFLOWS:")
    print("• Moved a task but realized you can do it today?")
    print("• Priority changed and need it done now?")
    print("• Found extra time and want to tackle tomorrow's tasks?")
    print("• Just click the ⬅️ arrow and it's back in today!")
    
    print("\n🚀 To start with move-back functionality:")
    print("./restart_move_back.sh")
    
    print("\n⚡ Your ENTROPY now supports flexible task movement! ⚡")

if __name__ == "__main__":
    main()
