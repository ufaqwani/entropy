#!/usr/bin/env python3
"""
ENTROPY - Add Dark Mode Theme Only
Clean implementation of dark/light theme toggle functionality
"""

import os
import shutil
import json
from datetime import datetime

def create_backup():
    """Create a timestamped backup before making changes"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = f"../entropy_backup_darkmode_only_{timestamp}"
    
    print(f"📦 Creating backup: {backup_dir}")
    
    try:
        shutil.copytree(".", backup_dir, ignore=shutil.ignore_patterns(
            'node_modules', '.git', '*.log', 'build', 'dist'
        ))
        
        backup_info = {
            "timestamp": timestamp,
            "date": datetime.now().isoformat(),
            "description": "Backup before adding dark mode theme only",
            "restore_command": f"../restore_backup.py {backup_dir}"
        }
        
        with open(f"{backup_dir}/backup_info.json", 'w') as f:
            json.dump(backup_info, f, indent=2)
        
        print(f"✅ Backup created: {backup_dir}")
        return backup_dir
        
    except Exception as e:
        print(f"❌ Backup failed: {e}")
        return None

def create_file(file_path, content):
    """Create file with proper directory structure"""
    # Ensure parent directory exists
    directory = os.path.dirname(file_path)
    if directory:
        os.makedirs(directory, exist_ok=True)
    
    with open(file_path, 'w') as f:
        f.write(content)
    print(f"✅ Created: {file_path}")

def main():
    print("🌙 ENTROPY - Adding Dark Mode Theme Only")
    print("=" * 45)
    
    # Check if we're in the right directory
    if not os.path.exists("backend") or not os.path.exists("frontend"):
        print("❌ Please run this script from the entropy-app directory")
        return
    
    # 1. Create backup
    backup_dir = create_backup()
    if not backup_dir:
        print("❌ Cannot proceed without backup.")
        return
    
    # 2. Create Theme Context
    print("🔧 Creating theme context...")
    
    theme_context = '''import React, { createContext, useContext, useState, useEffect } from 'react';

const ThemeContext = createContext();

export const useTheme = () => {
    const context = useContext(ThemeContext);
    if (!context) {
        throw new Error('useTheme must be used within a ThemeProvider');
    }
    return context;
};

export const ThemeProvider = ({ children }) => {
    const [isDarkMode, setIsDarkMode] = useState(() => {
        // Check localStorage for saved preference
        const saved = localStorage.getItem('entropy-theme');
        if (saved) {
            return saved === 'dark';
        }
        // Check system preference as fallback
        if (window.matchMedia) {
            return window.matchMedia('(prefers-color-scheme: dark)').matches;
        }
        return false;
    });

    useEffect(() => {
        // Save preference to localStorage
        localStorage.setItem('entropy-theme', isDarkMode ? 'dark' : 'light');
        
        // Apply theme attribute to document
        document.documentElement.setAttribute('data-theme', isDarkMode ? 'dark' : 'light');
    }, [isDarkMode]);

    const toggleTheme = () => {
        setIsDarkMode(prev => !prev);
    };

    const value = {
        isDarkMode,
        toggleTheme,
        theme: isDarkMode ? 'dark' : 'light'
    };

    return (
        <ThemeContext.Provider value={value}>
            {children}
        </ThemeContext.Provider>
    );
};'''
    
    create_file("frontend/src/contexts/ThemeContext.js", theme_context)
    
    # 3. Create Theme Toggle Component
    print("🎨 Creating theme toggle component...")
    
    theme_toggle = '''import React from 'react';
import { motion } from 'framer-motion';
import { FiSun, FiMoon } from 'react-icons/fi';
import { useTheme } from '../contexts/ThemeContext';

const ThemeToggle = () => {
    const { isDarkMode, toggleTheme } = useTheme();

    return (
        <div className="theme-toggle-container">
            <motion.button
                className="theme-toggle"
                onClick={toggleTheme}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                title={`Switch to ${isDarkMode ? 'light' : 'dark'} mode`}
            >
                <motion.div
                    className="theme-toggle-track"
                    animate={{
                        backgroundColor: isDarkMode ? '#4a5568' : '#e2e8f0'
                    }}
                    transition={{ duration: 0.3 }}
                >
                    <motion.div
                        className="theme-toggle-handle"
                        animate={{
                            x: isDarkMode ? 26 : 2
                        }}
                        transition={{
                            type: "spring",
                            stiffness: 300,
                            damping: 30
                        }}
                    >
                        <motion.div
                            animate={{ rotate: isDarkMode ? 180 : 0 }}
                            transition={{ duration: 0.3 }}
                        >
                            {isDarkMode ? <FiMoon size={14} /> : <FiSun size={14} />}
                        </motion.div>
                    </motion.div>
                </motion.div>
                
                <span className="theme-toggle-label">
                    {isDarkMode ? 'DARK' : 'LIGHT'}
                </span>
            </motion.button>
        </div>
    );
};

export default ThemeToggle;'''
    
    create_file("frontend/src/components/ThemeToggle.js", theme_toggle)
    
    # 4. Update existing App.js to include theme provider
    print("🔄 Updating App.js with theme provider...")
    
    # Read existing App.js
    try:
        with open("frontend/src/App.js", 'r') as f:
            app_content = f.read()
        
        # Add theme imports at the top
        if "ThemeProvider" not in app_content:
            app_content = app_content.replace(
                "import './styles/App.css';",
                "import { ThemeProvider } from './contexts/ThemeContext';\nimport ThemeToggle from './components/ThemeToggle';\nimport './styles/App.css';"
            )
        
        # Update header to include theme toggle
        if "header-content" not in app_content:
            app_content = app_content.replace(
                '''<header className="app-header">
                <h1>⚡ ENTROPY</h1>
                <p>Fight chaos. Complete tasks. Win the day.</p>
            </header>''',
                '''<header className="app-header">
                <div className="header-content">
                    <div className="header-main">
                        <h1>⚡ ENTROPY</h1>
                        <p>Fight chaos. Complete tasks. Win the day.</p>
                    </div>
                    <ThemeToggle />
                </div>
            </header>'''
            )
        
        # Wrap the main App component with ThemeProvider
        if "function App()" in app_content and "ThemeProvider" not in app_content.split("function App()")[1]:
            # Find the App component and wrap it
            app_content = app_content.replace(
                "function App() {",
                "function AppContent() {"
            )
            
            # Add new App wrapper function
            app_content = app_content.replace(
                "export default App;",
                '''function App() {
    return (
        <ThemeProvider>
            <AppContent />
        </ThemeProvider>
    );
}

export default App;'''
            )
        
        create_file("frontend/src/App.js", app_content)
        
    except Exception as e:
        print(f"❌ Error updating App.js: {e}")
        return
    
    # 5. Add comprehensive dark mode CSS
    print("🎨 Adding dark mode CSS styles...")
    
    dark_mode_css = '''

/* ENTROPY - Dark Mode Theme System */

:root {
    /* Light Theme Variables */
    --bg-primary: #ffffff;
    --bg-secondary: #f8f8f8;
    --bg-tertiary: #f9f9f9;
    --text-primary: #000000;
    --text-secondary: #333333;
    --text-tertiary: #666666;
    --text-muted: #999999;
    --border-primary: #000000;
    --border-secondary: #e0e0e0;
    --border-tertiary: #ddd;
    --accent-primary: #000000;
    --accent-secondary: #333333;
    --shadow: rgba(0, 0, 0, 0.1);
    --overlay: rgba(255, 255, 255, 0.95);
    
    /* Notification Colors - Light */
    --success-bg: #f0f8f0;
    --success-border: #4caf50;
    --success-text: #2e7d32;
    --warning-bg: #fff8e1;
    --warning-border: #ff9800;
    --warning-text: #ef6c00;
    --error-bg: #ffebee;
    --error-border: #f44336;
    --error-text: #c62828;
    --info-bg: #e3f2fd;
    --info-border: #2196f3;
    --info-text: #1565c0;
}

[data-theme="dark"] {
    /* Dark Theme Variables */
    --bg-primary: #1a1a1a;
    --bg-secondary: #2d2d2d;
    --bg-tertiary: #3d3d3d;
    --text-primary: #ffffff;
    --text-secondary: #e0e0e0;
    --text-tertiary: #b0b0b0;
    --text-muted: #888888;
    --border-primary: #ffffff;
    --border-secondary: #4a4a4a;
    --border-tertiary: #555555;
    --accent-primary: #ffffff;
    --accent-secondary: #e0e0e0;
    --shadow: rgba(0, 0, 0, 0.3);
    --overlay: rgba(26, 26, 26, 0.95);
    
    /* Notification Colors - Dark */
    --success-bg: #1b2f1b;
    --success-border: #4caf50;
    --success-text: #81c784;
    --warning-bg: #2d2416;
    --warning-border: #ff9800;
    --warning-text: #ffb74d;
    --error-bg: #2f1b1b;
    --error-border: #f44336;
    --error-text: #e57373;
    --info-bg: #1b2228;
    --info-border: #2196f3;
    --info-text: #64b5f6;
}

/* Apply theme variables to existing elements */
body {
    background: var(--bg-primary);
    color: var(--text-primary);
    transition: background-color 0.3s ease, color 0.3s ease;
}

.App {
    background: var(--bg-primary);
    transition: background-color 0.3s ease;
}

/* Header Updates */
.app-header {
    background: var(--bg-secondary);
    border-bottom: 2px solid var(--border-primary);
    transition: all 0.3s ease;
}

.header-content {
    display: flex;
    justify-content: space-between;
    align-items: center;
    max-width: 1000px;
    margin: 0 auto;
}

.header-main {
    text-align: center;
    flex: 1;
}

.app-header h1 {
    color: var(--text-primary);
}

.app-header p {
    color: var(--text-secondary);
}

/* Theme Toggle Styles */
.theme-toggle-container {
    display: flex;
    align-items: center;
}

.theme-toggle {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.5rem;
    background: transparent;
    border: none;
    cursor: pointer;
    padding: 0.5rem;
    border-radius: 8px;
    transition: background-color 0.3s ease;
}

.theme-toggle:hover {
    background: rgba(255, 255, 255, 0.1);
}

.theme-toggle-track {
    width: 52px;
    height: 26px;
    border-radius: 13px;
    position: relative;
    display: flex;
    align-items: center;
    border: 2px solid var(--border-primary);
}

.theme-toggle-handle {
    width: 20px;
    height: 20px;
    border-radius: 50%;
    background: var(--text-primary);
    display: flex;
    align-items: center;
    justify-content: center;
    color: var(--bg-primary);
    position: absolute;
    top: 1px;
}

.theme-toggle-label {
    font-family: 'Roboto Mono', monospace;
    font-size: 0.7rem;
    font-weight: 700;
    color: var(--text-tertiary);
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

/* Navigation Updates */
.app-nav {
    background: var(--bg-primary);
    border-bottom: 1px solid var(--border-secondary);
}

.app-nav button {
    background: var(--bg-primary);
    color: var(--text-primary);
    transition: all 0.3s ease;
}

.app-nav button:hover {
    background: var(--bg-secondary);
    border-bottom-color: var(--border-tertiary);
}

.app-nav button.active {
    background: var(--accent-primary);
    color: var(--bg-primary);
    border-bottom-color: var(--accent-primary);
}

/* Main Content Updates */
.app-main {
    background: var(--bg-primary);
}

/* Loading Spinner */
.loading-spinner {
    border-color: var(--border-secondary);
    border-top-color: var(--accent-primary);
}

/* Animation Container */
.entropy-animation {
    background: var(--bg-primary);
    border: 2px solid var(--border-primary);
    transition: all 0.3s ease;
}

.progress-title {
    color: var(--text-primary);
}

.status-message {
    background: var(--bg-secondary);
    border: 1px solid var(--border-secondary);
    color: var(--text-primary);
}

/* Task Sections */
.task-section,
.today-section {
    background: var(--bg-primary);
    border: 2px solid var(--border-primary);
    transition: all 0.3s ease;
}

.tomorrow-section {
    background: var(--bg-secondary);
    border: 2px solid var(--border-secondary);
    transition: all 0.3s ease;
}

.task-header h2 {
    color: var(--text-primary);
}

/* Buttons */
.btn-primary {
    background: var(--accent-primary);
    color: var(--bg-primary);
    border: 2px solid var(--accent-primary);
}

.btn-primary:hover:not(:disabled) {
    background: var(--accent-secondary);
    border-color: var(--accent-secondary);
}

.btn-primary:disabled {
    background: var(--text-muted);
    border-color: var(--text-muted);
    color: var(--bg-secondary);
}

.btn-secondary {
    background: var(--bg-primary);
    color: var(--accent-primary);
    border: 2px solid var(--accent-primary);
}

.btn-secondary:hover {
    background: var(--accent-primary);
    color: var(--bg-primary);
}

/* Task Items */
.task-item {
    background: var(--bg-tertiary);
    border: 2px solid var(--border-secondary);
    transition: all 0.3s ease;
}

.task-item:hover {
    border-color: var(--border-primary);
    box-shadow: 0 2px 8px var(--shadow);
}

.task-item.completed {
    background: var(--success-bg);
    border-color: var(--success-border);
}

.task-checkbox {
    border: 3px solid var(--accent-primary);
    background: var(--bg-primary);
    color: var(--bg-primary);
}

.task-checkbox.checked {
    background: var(--accent-primary);
    border-color: var(--accent-primary);
}

.task-info h4 {
    color: var(--text-primary);
}

.task-description {
    color: var(--text-tertiary);
}

.priority-badge {
    color: var(--text-primary);
    border: 1px solid var(--border-primary);
}

.delete-btn {
    color: var(--text-tertiary);
}

.delete-btn:hover {
    color: var(--text-primary);
}

/* Task Form */
.task-form-overlay {
    background: var(--overlay);
    backdrop-filter: blur(10px);
}

.task-form {
    background: var(--bg-primary);
    border: 2px solid var(--border-primary);
    box-shadow: 0 4px 20px var(--shadow);
}

.task-form h3 {
    color: var(--text-primary);
}

.form-group label {
    color: var(--text-primary);
}

.form-group input,
.form-group textarea,
.form-group select {
    background: var(--bg-primary);
    border: 2px solid var(--border-secondary);
    color: var(--text-primary);
}

.form-group input:focus,
.form-group textarea:focus,
.form-group select:focus {
    border-color: var(--accent-primary);
}

.btn-cancel {
    background: var(--bg-primary);
    color: var(--text-primary);
    border: 2px solid var(--border-primary);
}

.btn-cancel:hover {
    background: var(--accent-primary);
    color: var(--bg-primary);
}

.btn-submit {
    background: var(--accent-primary);
    color: var(--bg-primary);
    border: 2px solid var(--accent-primary);
}

.btn-submit:hover {
    background: var(--accent-secondary);
    border-color: var(--accent-secondary);
}

/* Tomorrow Tasks */
.tomorrow-header h3 {
    color: var(--text-primary);
}

.tomorrow-icon {
    color: var(--text-tertiary);
}

.task-count {
    background: var(--border-secondary);
    color: var(--text-primary);
}

.tomorrow-task-item {
    background: var(--bg-primary);
    border: 1px solid var(--border-secondary);
}

.tomorrow-task-item:hover {
    border-color: var(--border-primary);
    box-shadow: 0 2px 8px var(--shadow);
}

.tomorrow-task-item .task-content h5 {
    color: var(--text-primary);
}

.tomorrow-task-item .task-description {
    color: var(--text-tertiary);
}

.priority-label {
    color: var(--text-tertiary);
}

.time-icon {
    color: var(--text-muted);
}

.tomorrow-note {
    color: var(--text-tertiary);
    border-top: 1px solid var(--border-secondary);
}

.tomorrow-empty {
    color: var(--text-tertiary);
}

.empty-icon {
    color: var(--text-muted);
}

.tomorrow-empty h4 {
    color: var(--text-primary);
}

/* Charts and Other Components */
.progress-chart,
.daily-audit {
    background: var(--bg-primary);
    border: 2px solid var(--border-primary);
}

.chart-header h2,
.audit-header h2 {
    color: var(--text-primary);
}

.stat-card {
    background: var(--bg-secondary);
    border: 2px solid var(--border-secondary);
}

.stat-card:hover {
    border-color: var(--border-primary);
}

.stat-card h3 {
    color: var(--text-primary);
}

.stat-card p {
    color: var(--text-tertiary);
}

.chart-container {
    background: var(--bg-tertiary);
    border: 1px solid var(--border-secondary);
}

/* Notifications - Updated for Dark Mode */
.notification {
    backdrop-filter: blur(10px);
    box-shadow: 0 4px 12px var(--shadow);
}

/* No Tasks State */
.no-tasks h3,
.no-data h3 {
    color: var(--text-primary);
}

.no-tasks,
.no-data {
    color: var(--text-tertiary);
}

/* Responsive Updates */
@media (max-width: 768px) {
    .header-content {
        flex-direction: column;
        gap: 1rem;
        text-align: center;
    }
    
    .theme-toggle {
        order: -1;
    }
}

@media (max-width: 480px) {
    .theme-toggle-track {
        width: 44px;
        height: 22px;
    }
    
    .theme-toggle-handle {
        width: 16px;
        height: 16px;
    }
    
    .theme-toggle-label {
        font-size: 0.6rem;
    }
}

/* Smooth transitions for theme switching */
* {
    transition-property: background-color, border-color, color, box-shadow;
    transition-duration: 0.3s;
    transition-timing-function: ease;
}

/* Focus states for accessibility */
.theme-toggle:focus {
    outline: 2px solid var(--accent-primary);
    outline-offset: 2px;
}

/* High contrast mode support */
@media (prefers-contrast: high) {
    :root {
        --border-primary: #000000;
        --border-secondary: #333333;
    }
    
    [data-theme="dark"] {
        --border-primary: #ffffff;
        --border-secondary: #cccccc;
    }
}

/* Reduced motion support */
@media (prefers-reduced-motion: reduce) {
    * {
        transition-duration: 0.01ms !important;
        animation-duration: 0.01ms !important;
    }
}'''
    
    # Append dark mode CSS to existing file
    with open("frontend/src/styles/App.css", 'a') as f:
        f.write(dark_mode_css)
    
    print("✅ Added dark mode CSS")
    
    # 6. Create restart script
    restart_script = f'''#!/bin/bash
echo "🌙 Restarting ENTROPY with Dark Mode Theme..."
echo "Backup created: {backup_dir}"
echo ""

# Kill existing processes
pkill -f "node.*server.js" || true
pkill -f "react-scripts" || true

# Wait a moment
sleep 2

echo "✅ Dark Mode Features Added:"
echo "  🌙 Theme toggle button in header"
echo "  🎨 Complete light/dark theme system"
echo "  💾 Automatic theme preference saving"
echo "  📱 Mobile-optimized theme toggle"
echo "  🔄 Smooth theme transitions"
echo ""
echo "🛡️  Backup & Restore:"
echo "  📦 Backup created: {backup_dir}"
echo "  🔄 To restore: python3 ../restore_backup.py {backup_dir}"
echo ""

# Start the application
./start.sh'''
    
    create_file("restart_darkmode.sh", restart_script)
    os.chmod("restart_darkmode.sh", 0o755)
    
    print("\n🎉 Dark Mode Successfully Added!")
    print("=" * 40)
    print("✅ Theme Context: Created with localStorage support")
    print("✅ Toggle Component: Animated theme switcher in header")
    print("✅ CSS Variables: Complete light/dark theme system")
    print("✅ App Integration: Theme provider wrapper added")
    print("✅ Mobile Support: Responsive theme toggle")
    
    print(f"\n📦 BACKUP CREATED: {backup_dir}")
    print(f"🔄 Restore command: python3 ../restore_backup.py {backup_dir}")
    
    print("\n🌙 DARK MODE FEATURES:")
    print("• Toggle button in header switches between themes")
    print("• Automatic system preference detection")
    print("• Theme choice saved to localStorage")
    print("• Smooth transitions between light/dark")
    print("• All components adapt automatically")
    
    print("\n🚀 To start with dark mode:")
    print("./restart_darkmode.sh")
    
    print("\n⚡ Your ENTROPY app now has beautiful dark mode! ⚡")

if __name__ == "__main__":
    main()
