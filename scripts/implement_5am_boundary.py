#!/usr/bin/env python3
"""
ENTROPY - Implement 5 AM Day Boundary
Redefines "today" and "tomorrow" to start at 5 AM instead of midnight
"""

import os
import shutil
import json
from datetime import datetime

def create_backup():
    """Create backup before implementing 5 AM boundary"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = f"../entropy_backup_5am_boundary_{timestamp}"
    
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
    print("🕔 ENTROPY - Implement 5 AM Day Boundary")
    print("=" * 45)
    print("📅 Today: 5 AM today → 5 AM tomorrow")
    print("📅 Tomorrow: 5 AM tomorrow → 5 AM day after")
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
    
    print("🔧 Implementing 5 AM day boundary in backend...")
    
    # 1. Update backend with 5 AM day boundary logic
    enhanced_tasks_route = '''const express = require('express');
const router = express.Router();
const Task = require('../models/Task');

// Helper function to get day boundaries starting at 5 AM
function getDayBoundaries(referenceDate = new Date()) {
    const current = new Date(referenceDate);
    
    // Calculate "today" start (5 AM of current date or previous date if before 5 AM)
    const todayStart = new Date(current);
    todayStart.setHours(5, 0, 0, 0);
    
    // If current time is before 5 AM, "today" actually started yesterday at 5 AM
    if (current.getHours() < 5) {
        todayStart.setDate(todayStart.getDate() - 1);
    }
    
    // "Tomorrow" starts 24 hours after "today" starts
    const tomorrowStart = new Date(todayStart);
    tomorrowStart.setDate(tomorrowStart.getDate() + 1);
    
    // Day after tomorrow starts 24 hours after tomorrow
    const dayAfterTomorrowStart = new Date(tomorrowStart);
    dayAfterTomorrowStart.setDate(dayAfterTomorrowStart.getDate() + 1);
    
    return {
        todayStart,
        tomorrowStart,
        dayAfterTomorrowStart
    };
}

// Get today's and tomorrow's tasks - 5 AM BOUNDARY VERSION
router.get('/today', async (req, res) => {
    try {
        const { todayStart, tomorrowStart, dayAfterTomorrowStart } = getDayBoundaries();
        
        console.log(`📅 Day boundaries: Today (${todayStart.toISOString()}) → Tomorrow (${tomorrowStart.toISOString()})`);
        
        // Get today's tasks (5 AM today → 5 AM tomorrow, exclude moved/deleted)
        const todayTasks = await Task.find({
            date: { $gte: todayStart, $lt: tomorrowStart },
            $and: [
                { $or: [{ moved: { $exists: false } }, { moved: false }] },
                { $or: [{ deleted: { $exists: false } }, { deleted: false }] }
            ]
        }).sort({ priority: 1, createdAt: 1 });
        
        // Get tomorrow's tasks (5 AM tomorrow → 5 AM day after, exclude deleted)
        const tomorrowTasks = await Task.find({
            date: { $gte: tomorrowStart, $lt: dayAfterTomorrowStart },
            $or: [{ deleted: { $exists: false } }, { deleted: false }]
        }).sort({ priority: 1, createdAt: 1 });
        
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

// Create new task - 5 AM BOUNDARY VERSION
router.post('/', async (req, res) => {
    try {
        const { title, description, priority, date } = req.body;
        
        if (!title || !priority) {
            return res.status(400).json({ error: 'Title and priority are required' });
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
            title: title.trim(),
            description: description?.trim(),
            priority,
            date: taskDate
        });
        
        await task.save();
        res.status(201).json(task);
    } catch (error) {
        res.status(400).json({ error: error.message });
    }
});

// Update task
router.put('/:id', async (req, res) => {
    try {
        const { id } = req.params;
        const updates = req.body;
        
        if (updates.completed && !updates.completedAt) {
            updates.completedAt = new Date();
        }
        
        const task = await Task.findByIdAndUpdate(id, updates, { new: true });
        
        if (!task) {
            return res.status(404).json({ error: 'Task not found' });
        }
        
        res.json(task);
    } catch (error) {
        res.status(400).json({ error: error.message });
    }
});

// Delete task - 5 AM BOUNDARY VERSION
router.delete('/:id', async (req, res) => {
    try {
        const { id } = req.params;
        
        const taskToDelete = await Task.findById(id);
        if (!taskToDelete) {
            return res.status(404).json({ error: 'Task not found' });
        }
        
        const { todayStart, tomorrowStart, dayAfterTomorrowStart } = getDayBoundaries();
        
        // Check if this is a tomorrow task (between tomorrow 5 AM and day after 5 AM)
        const isTomorrowTask = taskToDelete.date >= tomorrowStart && taskToDelete.date < dayAfterTomorrowStart;
        
        if (isTomorrowTask) {
            // Find and delete related moved task from today's period
            const relatedMovedTask = await Task.findOne({
                title: taskToDelete.title,
                description: taskToDelete.description,
                priority: taskToDelete.priority,
                date: { $gte: todayStart, $lt: tomorrowStart },
                moved: true
            });
            
            if (relatedMovedTask) {
                await Task.findByIdAndDelete(relatedMovedTask._id);
                console.log(`🗑️ Deleted related moved task: ${relatedMovedTask._id}`);
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

// Move uncompleted tasks to tomorrow - 5 AM BOUNDARY VERSION
router.post('/move-to-tomorrow', async (req, res) => {
    try {
        const { todayStart, tomorrowStart } = getDayBoundaries();
        
        // Find uncompleted tasks from today's period (5 AM today → 5 AM tomorrow)
        const uncompletedTasks = await Task.find({
            date: { $gte: todayStart, $lt: tomorrowStart },
            completed: false,
            $and: [
                { $or: [{ moved: { $exists: false } }, { moved: false }] },
                { $or: [{ deleted: { $exists: false } }, { deleted: false }] }
            ]
        });
        
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
            // Check for duplicate in tomorrow's period
            const dayAfterTomorrowStart = new Date(tomorrowStart);
            dayAfterTomorrowStart.setDate(dayAfterTomorrowStart.getDate() + 1);
            
            const existingTomorrowTask = await Task.findOne({
                title: task.title,
                date: { $gte: tomorrowStart, $lt: dayAfterTomorrowStart },
                $or: [{ deleted: { $exists: false } }, { deleted: false }]
            });
            
            if (!existingTomorrowTask) {
                // Create new task for tomorrow's period (starts at 5 AM tomorrow)
                const newTask = new Task({
                    title: task.title,
                    description: task.description,
                    priority: task.priority,
                    date: tomorrowStart, // 5 AM tomorrow
                    originalTaskId: task._id
                });
                
                await newTask.save();
                newTomorrowTasks.push(newTask);
            }
            
            // Mark original task as moved
            await Task.findByIdAndUpdate(task._id, { moved: true });
            movedTaskIds.push(task._id);
        }
        
        const message = `Successfully moved ${newTomorrowTasks.length} task${newTomorrowTasks.length !== 1 ? 's' : ''} to tomorrow (starting 5 AM)`;
        
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

// Get day boundary info (for debugging/display)
router.get('/day-info', async (req, res) => {
    try {
        const { todayStart, tomorrowStart, dayAfterTomorrowStart } = getDayBoundaries();
        const now = new Date();
        
        res.json({
            currentTime: now.toISOString(),
            boundaries: {
                todayStart: todayStart.toISOString(),
                tomorrowStart: tomorrowStart.toISOString(),
                dayAfterTomorrowStart: dayAfterTomorrowStart.toISOString()
            },
            explanation: {
                today: `${todayStart.toLocaleString()} → ${tomorrowStart.toLocaleString()}`,
                tomorrow: `${tomorrowStart.toLocaleString()} → ${dayAfterTomorrowStart.toLocaleString()}`
            }
        });
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

module.exports = router;'''
    
    update_file("backend/routes/tasks.js", enhanced_tasks_route)
    
    print("🖥️ Creating frontend helper for 5 AM boundaries...")
    
    # 2. Create frontend utility for 5 AM boundaries
    date_utils = '''// Date utilities for 5 AM day boundary system
export const DateUtils = {
    // Get day boundaries starting at 5 AM instead of midnight
    getDayBoundaries(referenceDate = new Date()) {
        const current = new Date(referenceDate);
        
        // Calculate "today" start (5 AM of current date or previous date if before 5 AM)
        const todayStart = new Date(current);
        todayStart.setHours(5, 0, 0, 0);
        
        // If current time is before 5 AM, "today" actually started yesterday at 5 AM
        if (current.getHours() < 5) {
            todayStart.setDate(todayStart.getDate() - 1);
        }
        
        // "Tomorrow" starts 24 hours after "today" starts
        const tomorrowStart = new Date(todayStart);
        tomorrowStart.setDate(tomorrowStart.getDate() + 1);
        
        return {
            todayStart,
            tomorrowStart,
            current
        };
    },
    
    // Format day boundary info for display
    formatDayInfo() {
        const { todayStart, tomorrowStart, current } = this.getDayBoundaries();
        
        return {
            today: `${todayStart.toLocaleString()} → ${tomorrowStart.toLocaleString()}`,
            tomorrow: `${tomorrowStart.toLocaleString()} → ${new Date(tomorrowStart.getTime() + 24*60*60*1000).toLocaleString()}`,
            currentTime: current.toLocaleString(),
            isEarlyMorning: current.getHours() < 5
        };
    },
    
    // Check if a given time is in "today's" period (5 AM boundaries)
    isInTodayPeriod(date) {
        const { todayStart, tomorrowStart } = this.getDayBoundaries();
        const checkDate = new Date(date);
        return checkDate >= todayStart && checkDate < tomorrowStart;
    }
};'''
    
    os.makedirs("frontend/src/utils", exist_ok=True)
    update_file("frontend/src/utils/dateUtils.js", date_utils)
    
    print("📱 Creating day boundary display component...")
    
    # 3. Create component to show current day boundaries
    day_info_component = '''import React, { useState, useEffect } from 'react';
import { FiClock, FiSun, FiMoon, FiInfo } from 'react-icons/fi';
import { DateUtils } from '../utils/dateUtils';

const DayBoundaryInfo = ({ isExpanded = false }) => {
    const [dayInfo, setDayInfo] = useState(null);
    const [showDetails, setShowDetails] = useState(isExpanded);

    useEffect(() => {
        const updateDayInfo = () => {
            setDayInfo(DateUtils.formatDayInfo());
        };
        
        updateDayInfo();
        const interval = setInterval(updateDayInfo, 60000); // Update every minute
        
        return () => clearInterval(interval);
    }, []);

    if (!dayInfo) return null;

    return (
        <div className="day-boundary-info">
            <div className="day-status">
                <div className="current-period">
                    {dayInfo.isEarlyMorning ? (
                        <>
                            <FiMoon className="period-icon" />
                            <span>Still "Yesterday" until 5 AM</span>
                        </>
                    ) : (
                        <>
                            <FiSun className="period-icon" />
                            <span>"Today" started at 5 AM</span>
                        </>
                    )}
                </div>
                
                <button 
                    className="info-toggle"
                    onClick={() => setShowDetails(!showDetails)}
                    title="Show day boundary details"
                >
                    <FiInfo />
                </button>
            </div>
            
            {showDetails && (
                <div className="day-details">
                    <div className="boundary-item">
                        <strong>📅 Today:</strong>
                        <span className="time-range">{dayInfo.today}</span>
                    </div>
                    <div className="boundary-item">
                        <strong>📅 Tomorrow:</strong>
                        <span className="time-range">{dayInfo.tomorrow}</span>
                    </div>
                    <div className="boundary-item">
                        <strong>🕐 Current Time:</strong>
                        <span className="current-time">{dayInfo.currentTime}</span>
                    </div>
                    
                    <div className="boundary-explanation">
                        💡 <strong>Day Boundary:</strong> Days start at 5 AM instead of midnight. 
                        This means if it's 2 AM Tuesday, you're still in "Monday" until 5 AM arrives.
                    </div>
                </div>
            )}
        </div>
    );
};

export default DayBoundaryInfo;'''
    
    update_file("frontend/src/components/DayBoundaryInfo.js", day_info_component)
    
    print("🔄 Updating main App component...")
    
    # 4. Update App.js to include the day boundary info
    try:
        with open("frontend/src/App.js", 'r') as f:
            app_content = f.read()
        
        # Add import for DayBoundaryInfo
        if "DayBoundaryInfo" not in app_content:
            app_content = app_content.replace(
                "import ThemeToggle from './components/ThemeToggle';",
                "import ThemeToggle from './components/ThemeToggle';\nimport DayBoundaryInfo from './components/DayBoundaryInfo';"
            )
        
        # Add the component to the header
        if "DayBoundaryInfo" not in app_content:
            app_content = app_content.replace(
                '''                    <div className="header-main">
                        <h1>⚡ ENTROPY</h1>
                        <p>Fight chaos. Complete tasks. Win the day.</p>
                    </div>''',
                '''                    <div className="header-main">
                        <h1>⚡ ENTROPY</h1>
                        <p>Fight chaos. Complete tasks. Win the day.</p>
                        <DayBoundaryInfo />
                    </div>'''
            )
        
        update_file("frontend/src/App.js", app_content)
        
    except Exception as e:
        print(f"⚠️ Could not automatically update App.js: {e}")
    
    print("🎨 Adding CSS for day boundary components...")
    
    # 5. Add CSS for the new components
    day_boundary_css = '''
/* Day Boundary Info Styles */
.day-boundary-info {
    margin-top: 1rem;
    background: var(--bg-tertiary);
    border: 1px solid var(--border-secondary);
    border-radius: 8px;
    padding: 0.75rem;
    font-family: 'Roboto Mono', monospace;
    font-size: 0.85rem;
}

.day-status {
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.current-period {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-weight: 600;
    color: var(--text-primary);
}

.period-icon {
    font-size: 1rem;
    color: var(--text-secondary);
}

.info-toggle {
    background: transparent;
    border: none;
    color: var(--text-tertiary);
    cursor: pointer;
    padding: 0.25rem;
    border-radius: 4px;
    transition: all 0.3s ease;
}

.info-toggle:hover {
    color: var(--text-primary);
    background: var(--bg-secondary);
}

.day-details {
    margin-top: 0.75rem;
    padding-top: 0.75rem;
    border-top: 1px solid var(--border-tertiary);
}

.boundary-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.25rem 0;
    font-size: 0.8rem;
}

.boundary-item strong {
    color: var(--text-primary);
    min-width: 100px;
}

.time-range,
.current-time {
    color: var(--text-secondary);
    font-family: 'Roboto Mono', monospace;
}

.current-time {
    font-weight: 600;
    color: var(--accent-primary);
}

.boundary-explanation {
    margin-top: 0.75rem;
    padding: 0.5rem;
    background: var(--info-bg);
    border: 1px solid var(--info-border);
    border-radius: 6px;
    font-size: 0.75rem;
    line-height: 1.4;
    color: var(--info-text);
}

/* Mobile responsive */
@media (max-width: 768px) {
    .day-boundary-info {
        font-size: 0.75rem;
        padding: 0.5rem;
    }
    
    .boundary-item {
        flex-direction: column;
        align-items: flex-start;
        gap: 0.25rem;
    }
    
    .boundary-explanation {
        font-size: 0.7rem;
    }
}'''
    
    # Append to existing CSS
    with open("frontend/src/styles/App.css", 'a') as f:
        f.write(day_boundary_css)
    
    print("✅ Added day boundary CSS")
    
    # 6. Create test script to verify 5 AM boundaries
    test_script = '''#!/bin/bash
echo "🧪 Testing 5 AM Day Boundaries"
echo "=============================="
echo ""

# Test the day boundary info endpoint
echo "📋 Current Day Boundary Information:"
curl -s http://localhost:5000/api/tasks/day-info | python3 -m json.tool

echo ""
echo "📋 Today's and Tomorrow's Tasks:"
curl -s http://localhost:5000/api/tasks/today | python3 -c "
import sys, json
data = json.load(sys.stdin)
print(f'📅 Today: {data[\"todayCount\"]} tasks')
print(f'📅 Tomorrow: {data[\"tomorrowCount\"]} tasks')
if 'boundaries' in data:
    print(f'🕔 Today starts: {data[\"boundaries\"][\"todayStart\"]}')
    print(f'🕔 Tomorrow starts: {data[\"boundaries\"][\"tomorrowStart\"]}')
    print(f'🕐 Current time: {data[\"boundaries\"][\"currentTime\"]}')
"

echo ""
echo "✅ 5 AM boundaries are working!"
echo ""
echo "💡 Remember:"
echo "   - Today = 5 AM today → 5 AM tomorrow" 
echo "   - Tomorrow = 5 AM tomorrow → 5 AM day after"
echo "   - If it's 2 AM Tuesday, you're still in 'Monday' period"'''
    
    with open("test_5am_boundaries.sh", 'w') as f:
        f.write(test_script)
    os.chmod("test_5am_boundaries.sh", 0o755)
    
    # Create restart script
    restart_script = f'''#!/bin/bash
echo "🕔 Restarting ENTROPY with 5 AM Day Boundaries..."
echo "Backup created: {backup_dir}"
echo ""

# Kill existing processes
pkill -f "node.*server.js" || true
pkill -f "react-scripts" || true

# Wait a moment
sleep 2

echo "✅ 5 AM Day Boundary Implementation Complete:"
echo "  🕔 Days now start at 5 AM instead of midnight"
echo "  📅 Today: 5 AM today → 5 AM tomorrow"
echo "  📅 Tomorrow: 5 AM tomorrow → 5 AM day after"
echo "  💡 Early morning (12-5 AM) counts as previous day"
echo ""
echo "🧪 Test the boundaries:"
echo "  ./test_5am_boundaries.sh"
echo ""
echo "🛡️  Backup & Restore:"
echo "  📦 Backup created: {backup_dir}"
echo "  🔄 To restore: python3 ../restore_backup.py {backup_dir}"
echo ""

# Start the application
./start.sh'''
    
    with open("restart_5am_boundary.sh", 'w') as f:
        f.write(restart_script)
    os.chmod("restart_5am_boundary.sh", 0o755)
    
    print(f"\n🎉 5 AM Day Boundary Implementation Complete!")
    print("=" * 50)
    print("✅ Backend: All date calculations now use 5 AM boundaries")
    print("✅ Frontend: Day boundary info component added")
    print("✅ Database: Queries updated for 5 AM → 5 AM periods")
    print("✅ UI: Visual indicator shows current day period")
    
    print(f"\n📦 BACKUP CREATED: {backup_dir}")
    print(f"🔄 Restore command: python3 ../restore_backup.py {backup_dir}")
    
    print("\n🕔 NEW DAY DEFINITION:")
    print("• Today: 5 AM today → 5 AM tomorrow")
    print("• Tomorrow: 5 AM tomorrow → 5 AM day after")
    print("• Early morning (12-5 AM) = previous day")
    print("• Tasks created at 2 AM Tuesday = Monday tasks")
    
    print("\n🚀 To start with 5 AM boundaries:")
    print("./restart_5am_boundary.sh")
    
    print("\n🧪 To test the boundaries:")
    print("./test_5am_boundaries.sh")
    
    print("\n⚡ Your ENTROPY now uses 5 AM day boundaries! ⚡")

if __name__ == "__main__":
    main()
