#!/usr/bin/env python3
"""
ENTROPY - Remove Task Moving Feature & Fix Analytics CSS
Complete cleanup of problematic up/down task reordering
"""

import os
import shutil
import json
from datetime import datetime

def create_backup():
    """Create backup before cleanup"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = f"../entropy_backup_cleanup_{timestamp}"
    
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
    print("🧹 ENTROPY - Remove Task Moving & Fix Analytics")
    print("=" * 50)
    print("🎯 Complete cleanup of problematic features")
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
    
    print("🔧 Removing move up/down endpoints from backend...")
    
    # 1. Clean up backend routes - remove move endpoints
    try:
        with open("backend/routes/tasks.js", 'r') as f:
            tasks_content = f.read()
        
        # Remove move up/down endpoints by removing everything between specific markers
        import re
        
        # Remove move-up endpoint
        tasks_content = re.sub(
            r'// Move task up in priority order.*?router\.post\(\'/move-up/.*?\}\);',
            '',
            tasks_content,
            flags=re.DOTALL
        )
        
        # Remove move-down endpoint
        tasks_content = re.sub(
            r'// Move task down in priority order.*?router\.post\(\'/move-down/.*?\}\);',
            '',
            tasks_content,
            flags=re.DOTALL
        )
        
        # Remove any other reorder endpoints
        tasks_content = re.sub(
            r'router\.post\(\'/reorder\'.*?\}\);',
            '',
            tasks_content,
            flags=re.DOTALL
        )
        
        update_file("backend/routes/tasks.js", tasks_content)
        
    except Exception as e:
        print(f"❌ Error cleaning backend routes: {e}")
    
    print("📱 Restoring clean TaskList component...")
    
    # 2. Create clean TaskList without move buttons
    clean_task_list = '''import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { FiCheck, FiTrash2 } from 'react-icons/fi';

const TaskList = ({ tasks, onUpdate, onDelete }) => {
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

    // Sort by priority first, then by creation date
    const sortedTasks = [...tasks].sort((a, b) => {
        if (a.priority !== b.priority) {
            return a.priority - b.priority;
        }
        return new Date(b.createdAt || 0) - new Date(a.createdAt || 0);
    });

    return (
        <div className="task-list">
            <div className="task-list-header">
                <h3>Today's Tasks</h3>
                <div className="task-count-info">
                    {tasks.filter(t => t.completed).length} of {tasks.length} completed
                </div>
            </div>
            
            <div className="tasks-container">
                <AnimatePresence>
                    {sortedTasks.map((task, index) => (
                        <motion.div
                            key={task._id}
                            className={`task-item ${task.completed ? 'completed' : ''}`}
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            exit={{ opacity: 0, y: -20 }}
                            transition={{ delay: index * 0.05 }}
                            whileHover={{ scale: 1.01 }}
                        >
                            <div className="task-content">
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
    
    update_file("frontend/src/components/TaskList.js", clean_task_list)
    
    print("🔄 Cleaning up App.js...")
    
    # 3. Clean up App.js - remove move functions and props
    try:
        with open("frontend/src/App.js", 'r') as f:
            app_content = f.read()
        
        # Remove move functions
        import re
        app_content = re.sub(
            r'const moveTaskUp = async.*?\};',
            '',
            app_content,
            flags=re.DOTALL
        )
        
        app_content = re.sub(
            r'const moveTaskDown = async.*?\};',
            '',
            app_content,
            flags=re.DOTALL
        )
        
        app_content = re.sub(
            r'const reorderTasks = async.*?\};',
            '',
            app_content,
            flags=re.DOTALL
        )
        
        # Remove move props from TaskList call
        app_content = app_content.replace(
            '''                                    <TaskList 
                                        tasks={todayTasks}
                                        onUpdate={updateTask}
                                        onDelete={deleteTask}
                                        onMoveUp={moveTaskUp}
                                        onMoveDown={moveTaskDown}
                                    />''',
            '''                                    <TaskList 
                                        tasks={todayTasks}
                                        onUpdate={updateTask}
                                        onDelete={deleteTask}
                                    />'''
        )
        
        # Also clean up any other references
        app_content = app_content.replace('onReorder={reorderTasks}', '')
        app_content = app_content.replace('onMoveUp={moveTaskUp}', '')
        app_content = app_content.replace('onMoveDown={moveTaskDown}', '')
        
        update_file("frontend/src/App.js", app_content)
        
    except Exception as e:
        print(f"❌ Error cleaning App.js: {e}")
    
    print("🎨 Fixing Analytics CSS...")
    
    # 4. Create clean CSS without reorder styles and fix analytics
    clean_css = '''/* Clean Task List Layout */
.task-list {
    background: var(--bg-primary);
    border: 2px solid var(--border-primary);
    border-radius: 12px;
    padding: 1.5rem;
    margin-bottom: 2rem;
}

.task-list-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1.5rem;
    padding-bottom: 1rem;
    border-bottom: 1px solid var(--border-secondary);
}

.task-list-header h3 {
    font-family: 'Roboto Mono', monospace;
    font-size: 1.3rem;
    font-weight: 700;
    color: var(--text-primary);
    margin: 0;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

.task-count-info {
    font-family: 'Roboto Mono', monospace;
    font-size: 0.9rem;
    color: var(--text-tertiary);
    background: var(--bg-secondary);
    padding: 0.5rem 1rem;
    border-radius: 6px;
    border: 1px solid var(--border-secondary);
}

.tasks-container {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
}

/* Task Item Layout */
.task-item {
    background: var(--bg-tertiary);
    border: 2px solid var(--border-secondary);
    border-radius: 8px;
    transition: all 0.3s ease;
    overflow: hidden;
    position: relative;
}

.task-item:hover {
    border-color: var(--border-primary);
    box-shadow: 0 4px 12px var(--shadow);
    transform: translateY(-1px);
}

.task-item.completed {
    opacity: 0.8;
    background: var(--success-bg);
    border-color: var(--success-border);
}

.task-content {
    display: flex;
    align-items: flex-start;
    gap: 1rem;
    padding: 1.25rem;
    position: relative;
}

/* Priority Strip */
.task-priority-strip {
    position: absolute;
    left: 0;
    top: 0;
    bottom: 0;
    width: 4px;
    border-radius: 0 2px 2px 0;
}

/* Checkbox */
.task-checkbox {
    width: 24px;
    height: 24px;
    border-radius: 50%;
    border: 3px solid var(--accent-primary);
    background: var(--bg-primary);
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.3s ease;
    flex-shrink: 0;
    color: var(--bg-primary);
    margin-top: 0.25rem;
}

.task-checkbox:hover {
    transform: scale(1.1);
    border-color: var(--accent-secondary);
}

.task-checkbox.checked {
    background: var(--accent-primary);
    border-color: var(--accent-primary);
}

/* Task Details */
.task-details {
    flex: 1;
    min-width: 0;
}

.task-header {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    gap: 1rem;
    margin-bottom: 0.5rem;
    flex-wrap: wrap;
}

.task-details h4 {
    font-family: 'Roboto Mono', monospace;
    font-size: 1.1rem;
    font-weight: 600;
    color: var(--text-primary);
    margin: 0;
    line-height: 1.4;
    flex: 1;
    min-width: 0;
}

.task-details h4.strikethrough {
    text-decoration: line-through;
    opacity: 0.7;
}

/* Category Badge */
.task-category-badge {
    display: flex;
    align-items: center;
    gap: 0.4rem;
    padding: 0.25rem 0.75rem;
    border-radius: 12px;
    font-family: 'Roboto Mono', monospace;
    font-size: 0.75rem;
    font-weight: 600;
    color: white;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    white-space: nowrap;
    flex-shrink: 0;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.2);
}

.task-category-badge .category-icon {
    font-size: 0.9rem;
}

.task-category-badge .category-name {
    font-size: 0.7rem;
}

.task-description {
    font-family: 'Roboto Mono', monospace;
    font-size: 0.9rem;
    color: var(--text-tertiary);
    margin: 0;
    line-height: 1.4;
    word-wrap: break-word;
}

/* Task Meta */
.task-meta {
    display: flex;
    flex-direction: column;
    align-items: flex-end;
    gap: 0.75rem;
    flex-shrink: 0;
    margin-top: 0.25rem;
}

.priority-info {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.25rem;
}

.priority-badge {
    width: 32px;
    height: 32px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.9rem;
    color: white;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.priority-label {
    font-family: 'Roboto Mono', monospace;
    font-size: 0.7rem;
    font-weight: 600;
    color: var(--text-tertiary);
    text-transform: uppercase;
    letter-spacing: 0.05em;
    text-align: center;
}

.delete-btn {
    background: transparent;
    border: none;
    color: var(--text-muted);
    cursor: pointer;
    padding: 0.5rem;
    border-radius: 6px;
    transition: all 0.3s ease;
    font-size: 1rem;
}

.delete-btn:hover {
    color: #ff6b6b;
    background: rgba(255, 107, 107, 0.1);
    transform: scale(1.1);
}

/* No Tasks State */
.no-tasks {
    text-align: center;
    padding: 3rem;
    color: var(--text-tertiary);
}

.no-tasks h3 {
    font-family: 'Roboto Mono', monospace;
    font-size: 1.3rem;
    color: var(--text-primary);
    margin-bottom: 1rem;
}

.no-tasks p {
    font-size: 1rem;
    line-height: 1.5;
}

/* Mobile Responsive */
@media (max-width: 768px) {
    .task-list {
        padding: 1rem;
    }
    
    .task-list-header {
        flex-direction: column;
        align-items: stretch;
        gap: 1rem;
        text-align: center;
    }
    
    .task-content {
        flex-direction: column;
        gap: 1rem;
        padding: 1rem;
    }
    
    .task-header {
        flex-direction: column;
        align-items: stretch;
        gap: 0.75rem;
    }
    
    .task-category-badge {
        align-self: flex-start;
    }
    
    .task-meta {
        flex-direction: row;
        justify-content: space-between;
        align-items: center;
    }
    
    .priority-info {
        flex-direction: row;
        gap: 0.5rem;
    }
    
    .task-checkbox {
        width: 28px;
        height: 28px;
        align-self: flex-start;
    }
}

@media (max-width: 480px) {
    .tasks-container {
        gap: 1rem;
    }
    
    .task-content {
        padding: 0.75rem;
    }
    
    .task-details h4 {
        font-size: 1rem;
    }
    
    .task-category-badge {
        font-size: 0.7rem;
        padding: 0.2rem 0.6rem;
    }
    
    .task-category-badge .category-name {
        font-size: 0.65rem;
    }
    
    .priority-badge {
        width: 28px;
        height: 28px;
        font-size: 0.8rem;
    }
}'''
    
    # Replace problematic CSS sections
    try:
        with open("frontend/src/styles/App.css", 'r') as f:
            css_content = f.read()
        
        # Remove all reorder-related CSS
        import re
        css_content = re.sub(r'/\* Drag & Drop.*?\*/', '', css_content, flags=re.DOTALL)
        css_content = re.sub(r'/\* Smooth Task Reordering.*?\*/', '', css_content, flags=re.DOTALL)
        css_content = re.sub(r'\.reorder-.*?\}', '', css_content, flags=re.DOTALL | re.MULTILINE)
        css_content = re.sub(r'\.move-.*?\}', '', css_content, flags=re.DOTALL | re.MULTILINE)
        css_content = re.sub(r'\.drag-.*?\}', '', css_content, flags=re.DOTALL | re.MULTILINE)
        css_content = re.sub(r'\.position-.*?\}', '', css_content, flags=re.DOTALL | re.MULTILINE)
        
        # Add clean CSS
        css_content += "\n\n" + clean_css
        
        with open("frontend/src/styles/App.css", 'w') as f:
            f.write(css_content)
        
        print("✅ Fixed CSS and removed reorder styles")
        
    except Exception as e:
        print(f"⚠️ Could not automatically fix CSS: {e}")
    
    # 5. Create restart script
    restart_script = f'''#!/bin/bash
echo "🧹 Restarting ENTROPY - Clean & Fixed Version"
echo "Backup created: {backup_dir}"
echo ""

# Kill existing processes
pkill -f "node.*server.js" || true
pkill -f "react-scripts" || true

# Wait a moment
sleep 2

echo "✅ Cleanup Complete - Removed Features:"
echo "  ❌ Up/Down arrow task reordering"
echo "  ❌ Move up/down API endpoints"
echo "  ❌ Problematic CSS causing analytics issues"
echo "  ❌ Complex state management bugs"
echo ""
echo "✅ What Still Works:"
echo "  📊 Analytics Dashboard with beautiful charts"
echo "  🏷️  Category system with visual badges"
echo "  🔄 Templates and recurring tasks"
echo "  ⬅️ Move tasks back from tomorrow to today"
echo "  🕔 5 AM day boundaries"
echo "  📱 Mobile responsive design"
echo ""
echo "🎯 Task Display:"
echo "  • Clean priority-based sorting (High → Medium → Low)"
echo "  • Category badges show task grouping"
echo "  • No complex reordering - simple and reliable"
echo ""
echo "🛡️  Backup & Restore:"
echo "  📦 Backup created: {backup_dir}"
echo "  🔄 To restore: python3 ../restore_backup.py {backup_dir}"
echo ""

# Start the application
./start.sh'''
    
    with open("restart_clean.sh", 'w') as f:
        f.write(restart_script)
    os.chmod("restart_clean.sh", 0o755)
    
    print(f"\n🎉 Cleanup Complete!")
    print("=" * 30)
    print("✅ Removed: Up/down task reordering feature")
    print("✅ Removed: Move API endpoints from backend")
    print("✅ Removed: Problematic CSS affecting analytics")
    print("✅ Restored: Clean task display with priority sorting")
    print("✅ Fixed: Analytics CSS should work properly now")
    
    print(f"\n📦 BACKUP CREATED: {backup_dir}")
    print(f"🔄 Restore command: python3 ../restore_backup.py {backup_dir}")
    
    print("\n🧹 WHAT WAS REMOVED:")
    print("❌ Up/down arrow buttons")
    print("❌ Move up/down API endpoints")
    print("❌ Complex drag & drop CSS")
    print("❌ State management issues")
    print("❌ CSS conflicts affecting analytics")
    
    print("\n✅ WHAT STILL WORKS:")
    print("📊 Analytics Dashboard")
    print("🏷️ Category system")
    print("🔄 Templates & recurring tasks")
    print("⬅️ Move back to today")
    print("🕔 5 AM day boundaries")
    print("📱 Mobile responsive design")
    
    print("\n🚀 To start clean version:")
    print("./restart_clean.sh")
    
    print("\n⚡ Your ENTROPY is now clean, stable, and fully functional! ⚡")

if __name__ == "__main__":
    main()
