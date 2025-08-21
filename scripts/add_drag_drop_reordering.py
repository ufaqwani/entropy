#!/usr/bin/env python3
"""
ENTROPY - Add Drag & Drop Task Reordering with Auto Priority Update
Manual task reordering with automatic priority assignment
"""

import os
import shutil
import json
from datetime import datetime

def create_backup():
    """Create backup before adding reorder functionality"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = f"../entropy_backup_reorder_{timestamp}"
    
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
    print("🔄 ENTROPY - Add Drag & Drop Task Reordering")
    print("=" * 50)
    print("🎯 Manual reordering + Auto priority updates")
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
    
    print("🔧 Adding reorder API endpoint to backend...")
    
    # 1. Add reorder endpoint to backend tasks.js
    try:
        with open("backend/routes/tasks.js", 'r') as f:
            tasks_content = f.read()
        
        # Add the reorder endpoint before module.exports
        reorder_endpoint = '''
// Reorder tasks and auto-update priorities
router.post('/reorder', async (req, res) => {
    try {
        const { orderedTaskIds } = req.body;
        
        if (!Array.isArray(orderedTaskIds) || orderedTaskIds.length === 0) {
            return res.status(400).json({ 
                error: 'Invalid data',
                message: 'orderedTaskIds must be a non-empty array' 
            });
        }
        
        // Validate all task IDs exist
        const tasks = await Task.find({ _id: { $in: orderedTaskIds } });
        
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
        const updatedTasks = await Task.find({ _id: { $in: orderedTaskIds } })
            .populate('category', 'name color icon')
            .sort({ priority: 1 });
        
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
});'''
        
        # Insert the new endpoint before module.exports
        updated_content = tasks_content.replace(
            "module.exports = router;",
            reorder_endpoint + "\n\nmodule.exports = router;"
        )
        
        update_file("backend/routes/tasks.js", updated_content)
        
    except Exception as e:
        print(f"❌ Error updating backend routes: {e}")
        return
    
    print("📦 Installing react-beautiful-dnd for drag & drop...")
    
    # 2. Update frontend package.json to include react-beautiful-dnd
    try:
        with open("frontend/package.json", 'r') as f:
            package_data = json.load(f)
        
        if "react-beautiful-dnd" not in package_data.get("dependencies", {}):
            package_data.setdefault("dependencies", {})["react-beautiful-dnd"] = "^13.1.1"
            package_data.setdefault("dependencies", {})["@hello-pangea/dnd"] = "^16.3.0"
            
            with open("frontend/package.json", 'w') as f:
                json.dump(package_data, f, indent=2)
            
            print("✅ Added drag & drop dependencies to package.json")
    except Exception as e:
        print(f"⚠️ Could not update package.json: {e}")
    
    print("📱 Creating enhanced TaskList with drag & drop...")
    
    # 3. Create enhanced TaskList component with drag & drop
    enhanced_task_list = '''import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { FiCheck, FiTrash2, FiMove, FiFlag } from 'react-icons/fi';
import { DragDropContext, Droppable, Draggable } from '@hello-pangea/dnd';
import axios from 'axios';

const TaskList = ({ tasks, onUpdate, onDelete, onReorder }) => {
    const [isDragging, setIsDragging] = useState(false);

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

    const handleDragStart = () => {
        setIsDragging(true);
    };

    const handleDragEnd = async (result) => {
        setIsDragging(false);
        
        if (!result.destination) {
            return; // Dropped outside the list
        }

        if (result.source.index === result.destination.index) {
            return; // No change in position
        }

        // Reorder the tasks array
        const reorderedTasks = Array.from(tasks);
        const [removed] = reorderedTasks.splice(result.source.index, 1);
        reorderedTasks.splice(result.destination.index, 0, removed);

        // Get the new order of task IDs
        const orderedTaskIds = reorderedTasks.map(task => task._id);

        try {
            // Call the parent reorder function
            await onReorder(orderedTaskIds);
        } catch (error) {
            console.error('Error reordering tasks:', error);
            // You might want to show an error notification here
        }
    };

    return (
        <div className="task-list">
            <div className="task-list-header">
                <div className="header-left">
                    <h3>Today's Tasks</h3>
                    <div className="reorder-hint">
                        <FiMove className="move-icon" />
                        <span>Drag to reorder by importance</span>
                    </div>
                </div>
                <div className="task-count-info">
                    {tasks.filter(t => t.completed).length} of {tasks.length} completed
                </div>
            </div>
            
            <DragDropContext onDragStart={handleDragStart} onDragEnd={handleDragEnd}>
                <Droppable droppableId="task-list">
                    {(provided, snapshot) => (
                        <div
                            className={`tasks-container ${snapshot.isDraggingOver ? 'drag-over' : ''} ${isDragging ? 'dragging' : ''}`}
                            {...provided.droppableProps}
                            ref={provided.innerRef}
                        >
                            <AnimatePresence>
                                {tasks.map((task, index) => (
                                    <Draggable
                                        key={task._id}
                                        draggableId={task._id}
                                        index={index}
                                        isDragDisabled={task.completed}
                                    >
                                        {(provided, snapshot) => (
                                            <motion.div
                                                ref={provided.innerRef}
                                                {...provided.draggableProps}
                                                className={`task-item ${task.completed ? 'completed' : ''} ${snapshot.isDragging ? 'dragging' : ''}`}
                                                initial={{ opacity: 0, y: 20 }}
                                                animate={{ opacity: 1, y: 0 }}
                                                exit={{ opacity: 0, y: -20 }}
                                                transition={{ delay: index * 0.05 }}
                                                layout
                                            >
                                                <div className="task-content">
                                                    {/* Drag Handle */}
                                                    <div 
                                                        className={`drag-handle ${task.completed ? 'disabled' : ''}`}
                                                        {...provided.dragHandleProps}
                                                        title={task.completed ? 'Cannot reorder completed tasks' : 'Drag to reorder'}
                                                    >
                                                        <FiMove />
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
                                                            <span className="position-indicator">
                                                                #{index + 1}
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
                                        )}
                                    </Draggable>
                                ))}
                            </AnimatePresence>
                            {provided.placeholder}
                        </div>
                    )}
                </Droppable>
            </DragDropContext>
        </div>
    );
};

export default TaskList;'''
    
    update_file("frontend/src/components/TaskList.js", enhanced_task_list)
    
    print("🔄 Updating App.js to handle task reordering...")
    
    # 4. Update App.js to handle reordering
    try:
        with open("frontend/src/App.js", 'r') as f:
            app_content = f.read()
        
        # Add reorderTasks function
        reorder_function = '''    const reorderTasks = async (orderedTaskIds) => {
        try {
            const response = await axios.post('/api/tasks/reorder', {
                orderedTaskIds
            });
            
            // Update today's tasks with new priorities
            const updatedTasks = response.data.updatedTasks;
            setTodayTasks(updatedTasks);
            
            addNotification(
                'Tasks Reordered! 🔄',
                'Priorities updated based on your arrangement',
                'success',
                3000
            );
            
        } catch (error) {
            console.error('Error reordering tasks:', error);
            addNotification(
                'Reorder Failed',
                'Could not update task order. Please try again.',
                'error'
            );
        }
    };'''
        
        # Find a good place to insert the function (after other task functions)
        if "const moveBackToToday" in app_content:
            app_content = app_content.replace(
                "    };",
                "    };\n\n" + reorder_function,
                1  # Replace only the first occurrence after moveBackToToday
            )
        else:
            # Insert after deleteTask function
            app_content = app_content.replace(
                "const deleteTask = async (taskId) => {",
                reorder_function + "\n\n    const deleteTask = async (taskId) => {"
            )
        
        # Update TaskList component call to include onReorder prop
        app_content = app_content.replace(
            '''                                    <TaskList 
                                        tasks={todayTasks}
                                        onUpdate={updateTask}
                                        onDelete={deleteTask}
                                    />''',
            '''                                    <TaskList 
                                        tasks={todayTasks}
                                        onUpdate={updateTask}
                                        onDelete={deleteTask}
                                        onReorder={reorderTasks}
                                    />'''
        )
        
        update_file("frontend/src/App.js", app_content)
        
    except Exception as e:
        print(f"❌ Error updating App.js: {e}")
        return
    
    print("🎨 Adding drag & drop CSS styling...")
    
    # 5. Add CSS for drag & drop functionality
    drag_drop_css = '''
/* Drag & Drop Task Reordering Styles */

.task-list-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 1.5rem;
    padding-bottom: 1rem;
    border-bottom: 1px solid var(--border-secondary);
}

.header-left {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
}

.header-left h3 {
    font-family: 'Roboto Mono', monospace;
    font-size: 1.3rem;
    font-weight: 700;
    color: var(--text-primary);
    margin: 0;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

.reorder-hint {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-family: 'Roboto Mono', monospace;
    font-size: 0.8rem;
    color: var(--text-tertiary);
    background: var(--info-bg);
    padding: 0.25rem 0.75rem;
    border-radius: 12px;
    border: 1px solid var(--info-border);
}

.move-icon {
    font-size: 0.9rem;
    color: var(--text-muted);
}

/* Drag Handle */
.drag-handle {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 24px;
    height: 24px;
    color: var(--text-muted);
    cursor: grab;
    border-radius: 4px;
    transition: all 0.2s ease;
    flex-shrink: 0;
}

.drag-handle:hover {
    background: var(--bg-secondary);
    color: var(--text-secondary);
    transform: scale(1.1);
}

.drag-handle:active {
    cursor: grabbing;
}

.drag-handle.disabled {
    opacity: 0.3;
    cursor: not-allowed;
}

.drag-handle.disabled:hover {
    background: transparent;
    transform: none;
}

/* Dragging States */
.tasks-container.dragging {
    background: var(--bg-tertiary);
    border-radius: 8px;
    padding: 0.5rem;
}

.tasks-container.drag-over {
    background: var(--success-bg);
    border: 2px dashed var(--success-border);
}

.task-item.dragging {
    transform: rotate(2deg);
    box-shadow: 0 8px 16px var(--shadow);
    border-color: var(--accent-primary);
    background: var(--bg-primary);
    z-index: 1000;
}

.task-item.dragging .task-content {
    opacity: 0.9;
}

/* Position Indicator */
.position-indicator {
    font-family: 'Roboto Mono', monospace;
    font-size: 0.7rem;
    font-weight: 700;
    color: var(--text-muted);
    background: var(--bg-tertiary);
    padding: 0.2rem 0.4rem;
    border-radius: 4px;
    text-align: center;
    border: 1px solid var(--border-tertiary);
}

/* Enhanced Task Content Layout for Drag Handle */
.task-content {
    display: flex;
    align-items: flex-start;
    gap: 0.75rem;
    padding: 1.25rem;
    position: relative;
}

/* Enhanced Priority Info */
.priority-info {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.5rem;
}

/* Drag Feedback Animations */
@keyframes dragEnter {
    0% { transform: scale(1); }
    50% { transform: scale(1.02); }
    100% { transform: scale(1); }
}

.tasks-container.drag-over {
    animation: dragEnter 0.3s ease-in-out;
}

/* Mobile Drag & Drop */
@media (max-width: 768px) {
    .reorder-hint {
        font-size: 0.7rem;
        padding: 0.2rem 0.5rem;
    }
    
    .drag-handle {
        width: 32px;
        height: 32px;
    }
    
    .task-content {
        gap: 0.5rem;
        padding: 1rem;
    }
    
    .header-left {
        gap: 0.75rem;
    }
    
    .task-list-header {
        flex-direction: column;
        align-items: stretch;
        gap: 1rem;
    }
}

@media (max-width: 480px) {
    .reorder-hint span {
        display: none;
    }
    
    .reorder-hint {
        padding: 0.25rem;
        border-radius: 50%;
    }
    
    .drag-handle {
        width: 28px;
        height: 28px;
    }
}

/* Accessibility */
.drag-handle:focus {
    outline: 2px solid var(--accent-primary);
    outline-offset: 2px;
}

/* Completed Task Restrictions */
.task-item.completed .drag-handle {
    opacity: 0.3;
    cursor: not-allowed;
}

.task-item.completed .drag-handle:hover {
    transform: none;
    background: transparent;
}

/* Smooth Transitions */
.task-item {
    transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

.task-item:not(.dragging) {
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}

/* Drop Zone Indicators */
.tasks-container {
    min-height: 100px;
    transition: all 0.3s ease;
}

.tasks-container:empty::before {
    content: "Drop tasks here to reorder";
    display: flex;
    align-items: center;
    justify-content: center;
    height: 100px;
    color: var(--text-muted);
    font-family: 'Roboto Mono', monospace;
    font-style: italic;
}'''
    
    # Append to existing CSS
    with open("frontend/src/styles/App.css", 'a') as f:
        f.write(drag_drop_css)
    
    print("✅ Added drag & drop CSS styling")
    
    # 6. Create installation script for dependencies
    install_script = '''#!/bin/bash
echo "📦 Installing drag & drop dependencies..."

cd frontend
npm install @hello-pangea/dnd@^16.3.0

if [ $? -eq 0 ]; then
    echo "✅ Drag & drop dependencies installed successfully"
else
    echo "❌ Failed to install dependencies"
    echo "Please run manually: cd frontend && npm install @hello-pangea/dnd"
fi

cd ..'''
    
    with open("install_dnd.sh", 'w') as f:
        f.write(install_script)
    os.chmod("install_dnd.sh", 0o755)
    
    # 7. Create restart script
    restart_script = f'''#!/bin/bash
echo "🔄 Restarting ENTROPY with Drag & Drop Reordering..."
echo "Backup created: {backup_dir}"
echo ""

# Install dependencies first
echo "📦 Installing drag & drop dependencies..."
./install_dnd.sh

# Kill existing processes
pkill -f "node.*server.js" || true
pkill -f "react-scripts" || true

# Wait a moment
sleep 2

echo "✅ Drag & Drop Task Reordering Features:"
echo "  🔄 Drag tasks to reorder by importance"
echo "  🎯 Automatic priority updates based on position"
echo "  📍 Position indicators (#1, #2, #3)"
echo "  🚫 Completed tasks cannot be reordered"
echo "  📱 Mobile-friendly touch drag support"
echo ""
echo "🎯 How to Use:"
echo "  1. Grab the ⋮⋮ handle next to any task"
echo "  2. Drag it up or down to reorder"
echo "  3. Drop it in the new position"
echo "  4. Priority automatically updates (top = high priority)"
echo ""
echo "🛡️  Backup & Restore:"
echo "  📦 Backup created: {backup_dir}"
echo "  🔄 To restore: python3 ../restore_backup.py {backup_dir}"
echo ""

# Start the application
./start.sh'''
    
    with open("restart_reorder.sh", 'w') as f:
        f.write(restart_script)
    os.chmod("restart_reorder.sh", 0o755)
    
    print(f"\n🎉 Drag & Drop Task Reordering Complete!")
    print("=" * 50)
    print("✅ Backend: API endpoint for reordering with auto priority update")
    print("✅ Frontend: Drag & drop with react-beautiful-dnd library")
    print("✅ UI: Visual drag handles and position indicators")
    print("✅ Logic: Position 1 = High priority, Position 2 = Medium, etc.")
    print("✅ UX: Smooth animations and visual feedback")
    print("✅ Mobile: Touch-friendly drag support")
    
    print(f"\n📦 BACKUP CREATED: {backup_dir}")
    print(f"🔄 Restore command: python3 ../restore_backup.py {backup_dir}")
    
    print("\n🔄 SMART REORDERING FEATURES:")
    print("• **Drag Handle**: Grab the ⋮⋮ icon to drag tasks")
    print("• **Auto Priority**: Position 1 = High, Position 2 = Medium, Position 3 = Low")
    print("• **Visual Feedback**: Position indicators show current ranking")
    print("• **Smart Restrictions**: Completed tasks cannot be reordered")
    print("• **Instant Updates**: Changes saved immediately to database")
    
    print("\n🎯 PERFECT FOR YOUR WORKFLOW:")
    print("• Drag your most important task to the top")
    print("• App automatically assigns it High priority")
    print("• Reorder tasks based on your intuitive importance")
    print("• Position #1 = what you'll tackle first")
    
    print("\n📱 MOBILE-OPTIMIZED:")
    print("• Touch-friendly drag handles")
    print("• Visual drag feedback")
    print("• Responsive design for all screen sizes")
    
    print("\n🚀 To start with drag & drop reordering:")
    print("./restart_reorder.sh")
    
    print("\n⚡ Now you have complete control over your task sequence! ⚡")

if __name__ == "__main__":
    main()
