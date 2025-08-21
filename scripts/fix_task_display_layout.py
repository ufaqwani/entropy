#!/usr/bin/env python3
"""
ENTROPY - Fix Task Display (Priority Order with Category Badges)
Show tasks in priority order with category badges, not grouped sections
"""

import os
import shutil
import json
from datetime import datetime

def create_backup():
    """Create backup before fixing task display"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = f"../entropy_backup_task_display_fix_{timestamp}"
    
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
    print("📋 ENTROPY - Fix Task Display Layout")
    print("=" * 40)
    print("🎯 Priority order + category badges = Clean & organized")
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
    
    print("📱 Updating TaskList component for clean priority-based display...")
    
    # 1. Update TaskList component to show tasks in priority order with category badges
    updated_task_list = '''import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { FiCheck, FiTrash2, FiFlag } from 'react-icons/fi';

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

    // FIXED: Sort by priority first, then by creation date (no grouping)
    const sortedTasks = [...tasks].sort((a, b) => {
        // Priority 1 (High) comes first, then 2 (Medium), then 3 (Low)
        if (a.priority !== b.priority) {
            return a.priority - b.priority;
        }
        // If same priority, sort by creation date (newest first)
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
                                        
                                        {/* Category Badge - Compact & Clean */}
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
    
    update_file("frontend/src/components/TaskList.js", updated_task_list)
    
    print("🎨 Adding clean task display CSS...")
    
    # 2. Add CSS for the new clean task layout
    clean_task_css = '''
/* Clean Task List Layout - Priority Order with Category Badges */

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

/* Enhanced Task Item Layout */
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

/* Priority Strip - Left Border */
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

/* Task Details Section */
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

/* Category Badge - Compact Design */
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

/* Task Meta Section */
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
}

/* Animation Improvements */
.task-item {
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.task-item:hover .task-category-badge {
    transform: scale(1.05);
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
}

.task-item:hover .priority-badge {
    transform: scale(1.1);
    box-shadow: 0 3px 6px rgba(0, 0, 0, 0.3);
}

.task-checkbox,
.delete-btn,
.task-category-badge,
.priority-badge {
    transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
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
}'''
    
    # Remove the old category grouping CSS and add new CSS
    try:
        with open("frontend/src/styles/App.css", 'r') as f:
            css_content = f.read()
        
        # Remove old category grouping styles
        import re
        css_content = re.sub(r'/\* Task List Category Grouping \*/.*?(?=/\*|$)', '', css_content, flags=re.DOTALL)
        css_content = re.sub(r'\.category-group.*?(?=\.|$)', '', css_content, flags=re.DOTALL | re.MULTILINE)
        
        # Add new clean task styles
        css_content += clean_task_css
        
        with open("frontend/src/styles/App.css", 'w') as f:
            f.write(css_content)
        
        print("✅ Updated CSS with clean task layout")
        
    except Exception as e:
        print(f"⚠️ Could not automatically update CSS: {e}")
        # Create the CSS file separately
        with open("clean_task_styles.css", 'w') as f:
            f.write(clean_task_css)
        print("📄 Created clean_task_styles.css - manually add to App.css")
    
    # 3. Create restart script
    restart_script = f'''#!/bin/bash
echo "📋 Restarting ENTROPY with Clean Task Display..."
echo "Backup created: {backup_dir}"
echo ""

# Kill existing processes
pkill -f "node.*server.js" || true
pkill -f "react-scripts" || true

# Wait a moment
sleep 2

echo "✅ Clean Task Display Features:"
echo "  📊 Tasks sorted by priority (High → Medium → Low)"
echo "  🏷️  Category badges within each task"
echo "  📱 Clean, compact layout that saves space"
echo "  🎨 Priority indicators and visual cues"
echo "  💫 Smooth hover animations and interactions"
echo ""
echo "🎯 Task Display Improvements:"
echo "  • No more category grouping sections"
echo "  • Priority-first sorting for better focus"
echo "  • Compact category badges with icons"
echo "  • Left border priority strips"
echo "  • Enhanced mobile responsive design"
echo ""
echo "🛡️  Backup & Restore:"
echo "  📦 Backup created: {backup_dir}"
echo "  🔄 To restore: python3 ../restore_backup.py {backup_dir}"
echo ""

# Start the application
./start.sh'''
    
    with open("restart_clean_tasks.sh", 'w') as f:
        f.write(restart_script)
    os.chmod("restart_clean_tasks.sh", 0o755)
    
    print(f"\n🎉 Clean Task Display Layout Complete!")
    print("=" * 45)
    print("✅ Task List: Priority-based sorting (High → Medium → Low)")
    print("✅ Category Display: Compact badges with icons & colors")
    print("✅ Visual Hierarchy: Priority strips, badges, and indicators")
    print("✅ Space Efficient: No more bulky category sections")
    print("✅ Mobile Optimized: Responsive design for all devices")
    
    print(f"\n📦 BACKUP CREATED: {backup_dir}")
    print(f"🔄 Restore command: python3 ../restore_backup.py {backup_dir}")
    
    print("\n🎯 NEW TASK DISPLAY FEATURES:")
    print("• **Priority Order**: High priority tasks appear first")
    print("• **Category Badges**: Compact colored badges with category icon")
    print("• **Priority Strips**: Left border color indicates priority")
    print("• **Clean Layout**: One task after another, no grouping")
    print("• **Visual Cues**: Priority badges, hover effects, animations")
    
    print("\n📱 PERFECT MOBILE EXPERIENCE:")
    print("• Responsive design adapts to small screens")
    print("• Touch-friendly buttons and interactions")
    print("• Compact category badges for mobile viewing")
    print("• Optimized spacing and typography")
    
    print("\n🚀 To start with clean task display:")
    print("./restart_clean_tasks.sh")
    
    print("\n⚡ Your tasks now display in perfect priority order with category info! ⚡")

if __name__ == "__main__":
    main()
