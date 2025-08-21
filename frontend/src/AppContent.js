import React, { useState, useEffect, useContext } from 'react';
import axios from 'axios';
import TaskList from './components/TaskList';
import TaskForm from './components/TaskForm';
import TomorrowTasks from './components/TomorrowTasks';
import ProgressChart from './components/ProgressChart';
import EntropyAnimation from './components/EntropyAnimation';
import DailyAudit from './components/DailyAudit';
import CompletedTasksHistory from './components/CompletedTasksHistory';
import NotificationSystem, { useNotifications } from './components/NotificationSystem';
import { ThemeProvider } from './contexts/ThemeContext';
import ThemeToggle from './components/ThemeToggle';
import DayBoundaryInfo from './components/DayBoundaryInfo';
import CategoryManager from './components/CategoryManager';
import TemplateManager from './components/TemplateManager';
import AnalyticsDashboard from './components/AnalyticsDashboard';
import AuthContext from './contexts/AuthContext';
import './styles/App.css';

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL;

function AppContent() {
    const { logout } = useContext(AuthContext);
    const [todayTasks, setTodayTasks] = useState([]);
    const [tomorrowTasks, setTomorrowTasks] = useState([]);
    const [showTaskForm, setShowTaskForm] = useState(false);
    const [currentView, setCurrentView] = useState('today');
    const [progressData, setProgressData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [showCategoryManager, setShowCategoryManager] = useState(false);
    const [showTemplateManager, setShowTemplateManager] = useState(false);
    
    // Notification system
    const { notifications, addNotification, removeNotification } = useNotifications();

    const handleCategoryChange = () => {
        // Reload tasks when categories change
        loadTasks();
    };

    const handleMoveUp = async (taskId) => {
        console.log('[Frontend] handleMoveUp called for taskId:', taskId);
        try {
            const response = await axios.post(`/api/tasks/move-task-up/${taskId}`);
            console.log('[Frontend] handleMoveUp response:', response.data);
            setTodayTasks(response.data.tasks);
            addNotification('Task Moved Up! ⬆️', 'Task priority increased.', 'success', 2000);
        } catch (error) {
            console.error('[Frontend] Error moving task up:', error);
            addNotification('Move Failed', error.response?.data?.message || 'Could not move task up.', 'error');
        }
    };

    const handleMoveDown = async (taskId) => {
        console.log('[Frontend] handleMoveDown called for taskId:', taskId);
        try {
            const response = await axios.post(`/api/tasks/move-task-down/${taskId}`);
            console.log('[Frontend] handleMoveDown response:', response.data);
            setTodayTasks(response.data.tasks);
            addNotification('Task Moved Down! ⬇️', 'Task priority decreased.', 'success', 2000);
        } catch (error) {
            console.error('[Frontend] Error moving task down:', error);
            addNotification('Move Failed', error.response?.data?.message || 'Could not move task down.', 'error');
        }
    };

    const moveBackToToday = async (taskId) => {
    try {
        const response = await axios.post(`/api/tasks/move-back-to-today/${taskId}`);
        
        const movedTask = response.data.task;
        
        // CRITICAL FIX: Clean up any duplicate tasks in frontend state
        setTodayTasks(prev => {
            // Remove any tasks with same title or ID
            const filtered = prev.filter(task => 
                task._id !== movedTask._id && 
                task.title !== movedTask.title
            );
            // Add the moved task
            return [...filtered, movedTask];
        });
        
        // Remove from tomorrow's state
        setTomorrowTasks(prev => prev.filter(task => task._id !== taskId));
        
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
};


    const handleTemplateChange = () => {
        // Reload tasks when templates run
        loadTasks();
    };

    useEffect(() => {
        loadTasks();
        loadTodaysProgress();
    }, []);

    const loadTasks = async () => {
        try {
            setLoading(true);
            const response = await axios.get('/api/tasks/today');
            setTodayTasks(response.data.today || []);
            setTomorrowTasks(response.data.tomorrow || []);
        } catch (error) {
            console.error('Error loading tasks:', error);
            addNotification(
                'Error Loading Tasks', 
                'Failed to load your tasks. Please refresh the page.', 
                'error'
            );
        } finally {
            setLoading(false);
        }
    };

    const loadTodaysProgress = async () => {
        try {
            const response = await axios.get('/api/progress/today');
            setProgressData(response.data);
        } catch (error) {
            console.error('Error loading progress:', error);
        }
    };

    const addTask = async (taskData) => {
        try {
            const response = await axios.post('/api/tasks', taskData);
            setTodayTasks(prev => [...prev, response.data]);
            setShowTaskForm(false);
            
            addNotification(
                'Task Added Successfully!', 
                `"${taskData.title}" has been added to today's battle plan`, 
                'success'
            );
        } catch (error) {
            console.error('Error adding task:', error);
            
            if (error.response?.status === 409) {
                // Duplicate task error
                addNotification(
                    'Duplicate Task Detected! ⚠️',
                    error.response.data.message,
                    'warning',
                    6000
                );
            } else {
                addNotification(
                    'Failed to Add Task', 
                    'There was an error adding your task. Please try again.', 
                    'error'
                );
            }
        }
    };

const updateTask = async (taskId, updates) => {
    try {
        const response = await axios.put(`/api/tasks/${taskId}`, updates);
        
        // Update both today and tomorrow tasks states
        setTodayTasks(prev => prev.map(task => 
            task._id === taskId ? response.data : task
        ));
        setTomorrowTasks(prev => prev.map(task => 
            task._id === taskId ? response.data : task
        ));
        
        // Show completion notification
        if (updates.completed) {
            addNotification(
                'Task Completed! ⚡', 
                `Great job completing "${response.data.title}"`, 
                'success'
            );
        }
        
        // Reload progress to trigger animation update
        loadTodaysProgress();
    } catch (error) {
        console.error('Error updating task:', error);
        addNotification('Update Failed', 'Please try again', 'error');
    }
};


    const deleteTask = async (taskId) => {
        try {
            const response = await axios.delete(`/api/tasks/${taskId}`);
            
            // Remove from both lists
            setTodayTasks(prev => prev.filter(task => task._id !== taskId));
            setTomorrowTasks(prev => prev.filter(task => task._id !== taskId));
            
            const taskType = response.data.taskType;
            const taskTitle = response.data.deletedTask?.title || 'Task';
            
            addNotification(
                `${taskType === 'tomorrow' ? 'Tomorrow' : 'Today'} Task Deleted`,
                `"${taskTitle}" has been removed`,
                'info'
            );
            
            loadTodaysProgress();
        } catch (error) {
            console.error('Error deleting task:', error);
            addNotification(
                'Delete Failed', 
                'Failed to delete the task. Please try again.', 
                'error'
            );
        }
    };

const moveUncompletedTasks = async () => {
    try {
        const response = await axios.post(`${API_BASE_URL}/api/tasks/move-to-tomorrow`);
        
        if (response.data.movedCount === 0) {
            addNotification('Nothing to Move', 'All tasks completed!', 'info');
        } else {
            // CRITICAL FIX: Get the exact IDs of moved tasks
            const movedTaskIds = response.data.movedTaskIds || [];
            const newTomorrowTasks = response.data.tasks || [];
            
            // REMOVE moved tasks from today's list immediately
            setTodayTasks(prev => prev.filter(task => !movedTaskIds.includes(task._id)));
            
            // ADD new tasks to tomorrow's list (avoid duplicates)
            setTomorrowTasks(prev => {
                const existingIds = new Set(prev.map(t => t._id));
                const filtered = newTomorrowTasks.filter(t => !existingIds.has(t._id));
                return [...prev, ...filtered];
            });
            
            addNotification('Tasks Moved Successfully! 📅', response.data.message, 'success', 5000);
        }
    } catch (error) {
        console.error('Error moving tasks:', error);
        addNotification('Move Failed', 'Please try again', 'error');
    }
};


    if (loading) {
        return (
            <div className="app-loading">
                <div className="loading-spinner"></div>
                <p>Loading Entropy...</p>
            </div>
        );
    }

    return (
        <div className="App">
            <NotificationSystem 
                notifications={notifications} 
                removeNotification={removeNotification} 
            />
            
            <header className="app-header">
                <div className="header-content">
                    <div className="header-main">
                        <h1>⚡ ENTROPY</h1>
                        <p>Fight chaos. Complete tasks. Win the day.</p>
                    </div>
                    <div>
                        <ThemeToggle />
                        <button onClick={logout} className="btn-secondary">Logout</button>
                    </div>
                </div>
            </header>

            <nav className="app-nav">
                <button 
                    className={currentView === 'today' ? 'active' : ''}
                    onClick={() => setCurrentView('today')}
                >
                    Today
                </button>
                <button 
                    className={currentView === 'history' ? 'active' : ''}
                    onClick={() => setCurrentView('history')}
                >
                    History
                </button>
                <button 
                    className={currentView === 'progress' ? 'active' : ''}
                    onClick={() => setCurrentView('progress')}
                >
                    Progress
                </button>
                <button 
                    className={currentView === 'analytics' ? 'active' : ''}
                    onClick={() => setCurrentView('analytics')}
                >
                    Analytics
                </button>
                <button 
                    className={currentView === 'audit' ? 'active' : ''}
                    onClick={() => setCurrentView('audit')}
                >
                    Daily Audit
                </button>
            </nav>

            <main className="app-main">
                {currentView === 'today' && (
                    <>
<EntropyAnimation 
    completionRate={
        todayTasks.length === 0 
            ? 0  // No tasks = 0% completion (not victory)
            : Math.round(
                (todayTasks.filter(t => t.completed).length / todayTasks.length) * 100
            )
    }
    totalTasks={todayTasks.length}
    completedTasks={todayTasks.filter(t => t.completed).length}
/>


                        
                        <div className="tasks-container">
                            <div className="today-section">
                                <div className="task-header">
                                    <h2>Today's Battle Against Entropy</h2>
                                    <div className="task-actions">
                                        <button 
                                            className="btn-secondary"
                                            onClick={() => setShowCategoryManager(true)}
                                        >
                                            📂 Categories
                                        </button>
                                        <button 
                                            className="btn-secondary"
                                            onClick={() => setShowTemplateManager(true)}
                                        >
                                            🔄 Templates
                                        </button>
                                        <button 
                                            className="btn-primary"
                                            onClick={() => setShowTaskForm(true)}
                                            disabled={todayTasks.length >= 5}
                                        >
                                            + Add Task {todayTasks.length >= 3 && '(Not Recommended)'}
                                        </button>
                                        {todayTasks.some(t => !t.completed) && (
                                            <button 
                                                className="btn-secondary"
                                                onClick={moveUncompletedTasks}
                                            >
                                                Move Uncompleted to Tomorrow
                                            </button>
                                        )}
                                    </div>
                                </div>

                                <TaskList 
                                    tasks={todayTasks}
                                    onUpdate={updateTask}
                                    onDelete={deleteTask}
                                    onMoveUp={handleMoveUp}
                                    onMoveDown={handleMoveDown}
                                />
                            </div>
                            
                            {/* Tomorrow Section */}
                            {tomorrowTasks.length > 0 && (
                                <div className="tomorrow-section">
                                    <TomorrowTasks 
                                        tasks={tomorrowTasks}
                                        onUpdate={updateTask}
                                        onDelete={deleteTask}
                                        onMoveBack={moveBackToToday}
                                    />
                                </div>
                            )}
                        </div>

                        {showTaskForm && (
                            <TaskForm 
                                onSubmit={addTask}
                                onCancel={() => setShowTaskForm(false)}
                            />
                        )}
                        
                        {showCategoryManager && (
                            <CategoryManager
                                isOpen={showCategoryManager}
                                onClose={() => setShowCategoryManager(false)}
                                onCategoryChange={handleCategoryChange}
                            />
                        )}
                        
                        {showTemplateManager && (
                            <TemplateManager
                                isOpen={showTemplateManager}
                                onClose={() => setShowTemplateManager(false)}
                                onTemplateChange={handleTemplateChange}
                            />
                        )}
                    </>
                )}

                {currentView === 'history' && (
                    <CompletedTasksHistory />
                )}

                {currentView === 'progress' && (
                    <ProgressChart />
                )}
                  {currentView === 'analytics' && (
    <AnalyticsDashboard />
  )}

                {currentView === 'audit' && (
                    <DailyAudit 
                        progressData={progressData}
                        onAuditComplete={loadTodaysProgress}
                    />
                )}
            </main>
        </div>
    );
}

export default AppContent;
