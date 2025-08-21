#!/usr/bin/env python3
"""
ENTROPY - White Theme UI/UX Redesign Script
Converts app to clean white background with black text and modern robotic font
"""

import os
import re

def update_file(file_path, content):
    """Update file with given content"""
    with open(file_path, 'w') as f:
        f.write(content)
    print(f"✅ Updated: {file_path}")

def main():
    print("🎨 ENTROPY UI/UX Redesign - White Theme + Modern Robotic Font")
    print("=" * 65)
    
    # Check if we're in the right directory
    if not os.path.exists("backend") or not os.path.exists("frontend"):
        print("❌ Please run this script from the entropy-app directory")
        return
    
    # 1. Update HTML to include Roboto Mono font
    print("🔤 Adding Roboto Mono font...")
    
    html_content = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8" />
    <link rel="icon" href="%PUBLIC_URL%/favicon.ico" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <meta name="theme-color" content="#ffffff" />
    <meta name="description" content="Entropy - Fight chaos, complete tasks, win the day" />
    <link rel="apple-touch-icon" href="%PUBLIC_URL%/logo192.png" />
    <link rel="manifest" href="%PUBLIC_URL%/manifest.json" />
    
    <!-- Google Fonts - Roboto Mono for modern robotic look -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    
    <title>Entropy - Task Manager</title>
</head>
<body>
    <noscript>You need to enable JavaScript to run this app.</noscript>
    <div id="root"></div>
</body>
</html>'''
    
    update_file("frontend/public/index.html", html_content)
    
    # 2. Update EntropyAnimation component for simpler, cleaner animation
    print("🎮 Simplifying entropy animation...")
    
    entropy_animation = '''import React from 'react';
import { motion } from 'framer-motion';

const EntropyAnimation = ({ completionRate, totalTasks, completedTasks }) => {
    const position = Math.max(0, Math.min(100, completionRate));
    const characterX = 50 + (position * 3);
    const characterY = 180 - (position * 1.2);
    
    // Simple stairs - 10 steps
    const stairs = Array.from({ length: 10 }, (_, i) => ({
        x: 40 + i * 32,
        y: 200 - i * 12,
        width: 30,
        height: 12,
        completed: (i + 1) * 10 <= position
    }));
    
    return (
        <div className="entropy-animation">
            <h3 className="progress-title">Battle Progress</h3>
            
            <div className="animation-container">
                <svg className="stairs-svg" viewBox="0 0 400 220" preserveAspectRatio="xMidYMid meet">
                    {/* Background */}
                    <rect x="0" y="0" width="400" height="220" fill="#f9f9f9" stroke="#ddd" strokeWidth="1" rx="8"/>
                    
                    {/* Stairs */}
                    {stairs.map((stair, i) => (
                        <rect
                            key={i}
                            x={stair.x}
                            y={stair.y}
                            width={stair.width}
                            height={stair.height}
                            fill={stair.completed ? "#000000" : "#e0e0e0"}
                            stroke="#999"
                            strokeWidth="1"
                            className="stair-step"
                        />
                    ))}
                    
                    {/* Character - Simple Robot */}
                    <motion.g
                        animate={{
                            x: characterX,
                            y: characterY
                        }}
                        transition={{
                            type: "spring",
                            stiffness: 100,
                            damping: 20,
                            duration: 0.8
                        }}
                    >
                        {/* Robot Body */}
                        <rect x="-8" y="-15" width="16" height="20" rx="3" fill="#000000" stroke="#444" strokeWidth="1"/>
                        
                        {/* Robot Head */}
                        <rect x="-6" y="-25" width="12" height="12" rx="2" fill="#000000" stroke="#444" strokeWidth="1"/>
                        
                        {/* Robot Eyes */}
                        <circle cx="-3" cy="-20" r="1.5" fill="#ffffff"/>
                        <circle cx="3" cy="-20" r="1.5" fill="#ffffff"/>
                        
                        {/* Robot Arms */}
                        <motion.line
                            x1="-8" y1="-8" x2="-15" y2="-5"
                            stroke="#000000" strokeWidth="2" strokeLinecap="round"
                            animate={{ rotate: completionRate > 50 ? 20 : -20 }}
                            style={{ transformOrigin: "-8px -8px" }}
                        />
                        <motion.line
                            x1="8" y1="-8" x2="15" y2="-5"
                            stroke="#000000" strokeWidth="2" strokeLinecap="round"
                            animate={{ rotate: completionRate > 50 ? -20 : 20 }}
                            style={{ transformOrigin: "8px -8px" }}
                        />
                        
                        {/* Robot Legs */}
                        <line x1="-4" y1="5" x2="-4" y2="12" stroke="#000000" strokeWidth="2" strokeLinecap="round"/>
                        <line x1="4" y1="5" x2="4" y2="12" stroke="#000000" strokeWidth="2" strokeLinecap="round"/>
                        
                        {/* Victory Flag when 100% */}
                        {completionRate === 100 && (
                            <motion.g
                                initial={{ scale: 0, opacity: 0 }}
                                animate={{ scale: 1, opacity: 1 }}
                                transition={{ delay: 0.5, duration: 0.5 }}
                            >
                                <line x1="20" y1="-25" x2="20" y2="-5" stroke="#000000" strokeWidth="2"/>
                                <polygon points="20,-25 35,-20 20,-15" fill="#000000"/>
                                <text x="22" y="-18" fontSize="8" fill="#ffffff" fontFamily="Roboto Mono">WIN</text>
                            </motion.g>
                        )}
                    </motion.g>
                    
                    {/* Progress Text */}
                    <text x="200" y="25" textAnchor="middle" fontSize="14" fontFamily="Roboto Mono" fontWeight="600" fill="#000000">
                        {completedTasks}/{totalTasks} TASKS • {position}%
                    </text>
                    
                    {/* Entropy Warning (when progress is low) */}
                    {position < 50 && (
                        <motion.text
                            x="200" y="45" textAnchor="middle" fontSize="12" fontFamily="Roboto Mono" fontWeight="400" fill="#666"
                            animate={{ opacity: [0.5, 1, 0.5] }}
                            transition={{ duration: 2, repeat: Infinity }}
                        >
                            ENTROPY INCREASING...
                        </motion.text>
                    )}
                </svg>
            </div>
            
            <div className="progress-status">
                <div className="status-message">
                    {completionRate === 100 && "🏆 ENTROPY DEFEATED! Perfect victory today!"}
                    {completionRate >= 75 && completionRate < 100 && "⚡ STRONG PROGRESS! Keep pushing forward!"}
                    {completionRate >= 50 && completionRate < 75 && "🔥 GOOD MOMENTUM! Don't let entropy win!"}
                    {completionRate >= 25 && completionRate < 50 && "⚠️ ENTROPY GAINING! Time to take action!"}
                    {completionRate < 25 && "🚨 CHAOS DETECTED! Start completing tasks now!"}
                </div>
            </div>
        </div>
    );
};

export default EntropyAnimation;'''
    
    update_file("frontend/src/components/EntropyAnimation.js", entropy_animation)
    
    # 3. Create comprehensive white theme CSS
    print("🎨 Applying white theme with modern robotic styling...")
    
    white_theme_css = '''/* ENTROPY - White Theme with Modern Robotic Font */

* {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
}

body {
    font-family: 'Roboto Mono', 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
    background: #ffffff;
    color: #000000;
    min-height: 100vh;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
    font-weight: 400;
    line-height: 1.6;
}

.App {
    min-height: 100vh;
    display: flex;
    flex-direction: column;
    background: #ffffff;
}

/* Header */
.app-header {
    background: #f8f8f8;
    padding: 2rem;
    text-align: center;
    border-bottom: 2px solid #000000;
}

.app-header h1 {
    font-family: 'Roboto Mono', monospace;
    font-size: 3rem;
    font-weight: 700;
    margin-bottom: 0.5rem;
    color: #000000;
    letter-spacing: 0.1em;
    text-transform: uppercase;
}

.app-header p {
    font-size: 1.1rem;
    color: #333333;
    font-weight: 500;
    letter-spacing: 0.05em;
}

/* Navigation */
.app-nav {
    display: flex;
    justify-content: center;
    gap: 0;
    padding: 0;
    background: #ffffff;
    border-bottom: 1px solid #ddd;
}

.app-nav button {
    background: #ffffff;
    border: none;
    border-bottom: 3px solid transparent;
    color: #000000;
    padding: 1rem 2rem;
    cursor: pointer;
    transition: all 0.3s ease;
    font-family: 'Roboto Mono', monospace;
    font-size: 0.9rem;
    font-weight: 600;
    letter-spacing: 0.05em;
    text-transform: uppercase;
}

.app-nav button:hover {
    background: #f5f5f5;
    border-bottom-color: #666666;
}

.app-nav button.active {
    background: #000000;
    color: #ffffff;
    border-bottom-color: #000000;
}

/* Main Content */
.app-main {
    flex: 1;
    padding: 2rem;
    max-width: 1000px;
    margin: 0 auto;
    width: 100%;
}

/* Loading */
.app-loading {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 100vh;
    gap: 1rem;
}

.loading-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 3rem;
    gap: 1rem;
}

.loading-spinner {
    width: 40px;
    height: 40px;
    border: 3px solid #e0e0e0;
    border-top: 3px solid #000000;
    border-radius: 50%;
    animation: spin 1s linear infinite;
}

@keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}

/* Entropy Animation */
.entropy-animation {
    background: #ffffff;
    border: 2px solid #000000;
    border-radius: 12px;
    padding: 1.5rem;
    margin-bottom: 2rem;
    text-align: center;
}

.progress-title {
    font-family: 'Roboto Mono', monospace;
    font-size: 1.2rem;
    font-weight: 600;
    margin-bottom: 1rem;
    color: #000000;
    letter-spacing: 0.1em;
    text-transform: uppercase;
}

.animation-container {
    width: 100%;
    max-width: 500px;
    margin: 0 auto;
}

.stairs-svg {
    width: 100%;
    height: auto;
    max-height: 200px;
    border-radius: 8px;
}

.stair-step {
    transition: fill 0.4s ease;
}

.progress-status {
    margin-top: 1rem;
}

.status-message {
    font-family: 'Roboto Mono', monospace;
    font-size: 1rem;
    font-weight: 500;
    padding: 0.75rem 1rem;
    background: #f5f5f5;
    border: 1px solid #ddd;
    border-radius: 8px;
    color: #000000;
    letter-spacing: 0.05em;
}

/* Task Section */
.task-section {
    background: #ffffff;
    border: 2px solid #000000;
    border-radius: 12px;
    padding: 2rem;
}

.task-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 2rem;
    flex-wrap: wrap;
    gap: 1rem;
}

.task-header h2 {
    font-family: 'Roboto Mono', monospace;
    font-size: 1.5rem;
    font-weight: 700;
    color: #000000;
    letter-spacing: 0.05em;
    text-transform: uppercase;
}

.task-actions {
    display: flex;
    gap: 1rem;
    flex-wrap: wrap;
}

.btn-primary {
    background: #000000;
    color: #ffffff;
    border: 2px solid #000000;
    padding: 0.75rem 1.5rem;
    border-radius: 8px;
    cursor: pointer;
    font-family: 'Roboto Mono', monospace;
    font-weight: 600;
    font-size: 0.9rem;
    letter-spacing: 0.05em;
    text-transform: uppercase;
    transition: all 0.3s ease;
}

.btn-primary:hover:not(:disabled) {
    background: #333333;
    border-color: #333333;
}

.btn-primary:disabled {
    background: #cccccc;
    border-color: #cccccc;
    color: #666666;
    cursor: not-allowed;
}

.btn-secondary {
    background: #ffffff;
    color: #000000;
    border: 2px solid #000000;
    padding: 0.75rem 1.5rem;
    border-radius: 8px;
    cursor: pointer;
    font-family: 'Roboto Mono', monospace;
    font-weight: 600;
    font-size: 0.9rem;
    letter-spacing: 0.05em;
    text-transform: uppercase;
    transition: all 0.3s ease;
}

.btn-secondary:hover {
    background: #000000;
    color: #ffffff;
}

/* Task List */
.task-list {
    display: flex;
    flex-direction: column;
    gap: 1rem;
}

.no-tasks {
    text-align: center;
    padding: 3rem;
    color: #666666;
}

.no-tasks h3 {
    font-family: 'Roboto Mono', monospace;
    font-size: 1.2rem;
    margin-bottom: 0.5rem;
    color: #000000;
    font-weight: 600;
}

.task-item {
    background: #f9f9f9;
    border: 2px solid #e0e0e0;
    border-radius: 10px;
    transition: all 0.3s ease;
}

.task-item:hover {
    border-color: #000000;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.task-item.completed {
    background: #f0f8f0;
    border-color: #4caf50;
}

.task-content {
    display: flex;
    align-items: center;
    padding: 1.25rem;
    gap: 1rem;
}

.task-checkbox {
    width: 28px;
    height: 28px;
    border-radius: 50%;
    border: 3px solid #000000;
    background: #ffffff;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.3s ease;
    flex-shrink: 0;
    font-size: 1rem;
    color: #ffffff;
}

.task-checkbox:hover {
    border-color: #333333;
}

.task-checkbox.checked {
    background: #000000;
    border-color: #000000;
}

.task-info {
    flex: 1;
}

.task-info h4 {
    font-family: 'Roboto Mono', monospace;
    font-size: 1.1rem;
    font-weight: 600;
    margin-bottom: 0.25rem;
    color: #000000;
}

.task-info h4.strikethrough {
    text-decoration: line-through;
    opacity: 0.6;
}

.task-description {
    font-family: 'Roboto Mono', monospace;
    font-size: 0.9rem;
    color: #666666;
    margin: 0;
}

.task-meta {
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.priority-badge {
    display: flex;
    align-items: center;
    gap: 0.25rem;
    padding: 0.4rem 0.8rem;
    border-radius: 6px;
    font-family: 'Roboto Mono', monospace;
    font-size: 0.75rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: #000000;
    border: 1px solid #000000;
}

.delete-btn {
    background: transparent;
    border: none;
    color: #666666;
    cursor: pointer;
    padding: 0.5rem;
    border-radius: 4px;
    transition: color 0.3s ease;
    flex-shrink: 0;
    font-size: 1.2rem;
}

.delete-btn:hover {
    color: #000000;
}

/* Task Form */
.task-form-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(255, 255, 255, 0.95);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
    padding: 1rem;
}

.task-form {
    background: #ffffff;
    padding: 2rem;
    border-radius: 12px;
    border: 2px solid #000000;
    max-width: 500px;
    width: 100%;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}

.task-form h3 {
    font-family: 'Roboto Mono', monospace;
    font-size: 1.4rem;
    font-weight: 700;
    margin-bottom: 1.5rem;
    color: #000000;
    text-align: center;
    letter-spacing: 0.05em;
    text-transform: uppercase;
}

.form-group {
    margin-bottom: 1.5rem;
}

.form-group label {
    display: block;
    margin-bottom: 0.5rem;
    font-family: 'Roboto Mono', monospace;
    font-weight: 600;
    color: #000000;
    font-size: 0.9rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

.form-group input,
.form-group textarea,
.form-group select {
    width: 100%;
    padding: 0.8rem;
    background: #ffffff;
    border: 2px solid #e0e0e0;
    border-radius: 8px;
    color: #000000;
    font-size: 1rem;
    font-family: 'Roboto Mono', monospace;
    transition: border-color 0.3s ease;
}

.form-group input:focus,
.form-group textarea:focus,
.form-group select:focus {
    outline: none;
    border-color: #000000;
}

.form-group textarea {
    resize: vertical;
    min-height: 80px;
}

.form-actions {
    display: flex;
    gap: 1rem;
    justify-content: flex-end;
    margin-top: 2rem;
}

.btn-cancel {
    background: #ffffff;
    color: #000000;
    border: 2px solid #000000;
    padding: 0.75rem 1.5rem;
    border-radius: 8px;
    cursor: pointer;
    font-family: 'Roboto Mono', monospace;
    font-weight: 600;
    font-size: 0.9rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    transition: all 0.3s ease;
}

.btn-cancel:hover {
    background: #000000;
    color: #ffffff;
}

.btn-submit {
    background: #000000;
    color: #ffffff;
    border: 2px solid #000000;
    padding: 0.75rem 1.5rem;
    border-radius: 8px;
    cursor: pointer;
    font-family: 'Roboto Mono', monospace;
    font-weight: 600;
    font-size: 0.9rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    transition: all 0.3s ease;
}

.btn-submit:hover {
    background: #333333;
    border-color: #333333;
}

/* Progress Chart */
.progress-chart {
    background: #ffffff;
    border: 2px solid #000000;
    border-radius: 12px;
    padding: 2rem;
}

.chart-header {
    text-align: center;
    margin-bottom: 2rem;
}

.chart-header h2 {
    font-family: 'Roboto Mono', monospace;
    font-size: 1.5rem;
    font-weight: 700;
    color: #000000;
    letter-spacing: 0.05em;
    text-transform: uppercase;
}

.time-range-selector {
    display: flex;
    justify-content: center;
    gap: 0.5rem;
    margin-top: 1rem;
}

.time-range-selector button {
    background: #ffffff;
    border: 2px solid #000000;
    color: #000000;
    padding: 0.5rem 1rem;
    border-radius: 6px;
    cursor: pointer;
    font-family: 'Roboto Mono', monospace;
    font-weight: 600;
    font-size: 0.8rem;
    text-transform: uppercase;
    transition: all 0.3s ease;
}

.time-range-selector button:hover {
    background: #f5f5f5;
}

.time-range-selector button.active {
    background: #000000;
    color: #ffffff;
}

.stats-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    gap: 1rem;
    margin-bottom: 2rem;
}

.stat-card {
    background: #f8f8f8;
    border: 2px solid #e0e0e0;
    padding: 1.5rem;
    border-radius: 8px;
    text-align: center;
    transition: border-color 0.3s ease;
}

.stat-card:hover {
    border-color: #000000;
}

.stat-card h3 {
    font-family: 'Roboto Mono', monospace;
    font-size: 2rem;
    font-weight: 700;
    color: #000000;
    margin-bottom: 0.5rem;
}

.stat-card p {
    font-family: 'Roboto Mono', monospace;
    font-size: 0.8rem;
    font-weight: 600;
    color: #666666;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

.chart-container {
    background: #f9f9f9;
    border: 1px solid #e0e0e0;
    border-radius: 8px;
    padding: 1rem;
    margin-top: 1rem;
}

.no-data {
    text-align: center;
    padding: 3rem;
    color: #666666;
}

.no-data h3 {
    font-family: 'Roboto Mono', monospace;
    font-size: 1.2rem;
    color: #000000;
    margin-bottom: 0.5rem;
    font-weight: 600;
}

/* Daily Audit */
.daily-audit {
    background: #ffffff;
    border: 2px solid #000000;
    border-radius: 12px;
    padding: 2rem;
    max-width: 800px;
    margin: 0 auto;
}

.audit-header {
    text-align: center;
    margin-bottom: 2rem;
}

.audit-header h2 {
    font-family: 'Roboto Mono', monospace;
    font-size: 1.5rem;
    font-weight: 700;
    color: #000000;
    letter-spacing: 0.05em;
    text-transform: uppercase;
    margin-bottom: 0.5rem;
}

.audit-header p {
    color: #666666;
    font-size: 1rem;
}

.audit-summary {
    margin-bottom: 2rem;
}

.summary-card {
    background: #f8f8f8;
    border: 2px solid #e0e0e0;
    padding: 1.5rem;
    border-radius: 8px;
}

.summary-card h3 {
    font-family: 'Roboto Mono', monospace;
    font-weight: 700;
    margin-bottom: 1rem;
    color: #000000;
    text-align: center;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

.performance-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1rem;
}

.performance-item {
    display: flex;
    justify-content: space-between;
    padding: 0.75rem 0;
    border-bottom: 1px solid #e0e0e0;
    font-family: 'Roboto Mono', monospace;
}

.performance-item:last-child {
    border-bottom: none;
}

.performance-item .label {
    font-weight: 600;
    color: #000000;
}

.performance-item .value {
    font-weight: 700;
    color: #000000;
}

.audit-question {
    text-align: center;
    padding: 2rem;
}

.audit-question h3 {
    font-family: 'Roboto Mono', monospace;
    font-size: 1.3rem;
    font-weight: 700;
    margin-bottom: 1rem;
    color: #000000;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

.audit-question p {
    color: #666666;
    margin-bottom: 2rem;
    max-width: 500px;
    margin-left: auto;
    margin-right: auto;
    line-height: 1.6;
}

.audit-buttons {
    display: flex;
    gap: 1rem;
    justify-content: center;
    flex-wrap: wrap;
}

.audit-btn {
    padding: 1rem 2rem;
    border: 2px solid #000000;
    border-radius: 8px;
    font-family: 'Roboto Mono', monospace;
    font-size: 1rem;
    font-weight: 700;
    cursor: pointer;
    transition: all 0.3s ease;
    min-width: 180px;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

.audit-btn.success {
    background: #ffffff;
    color: #000000;
}

.audit-btn.success:hover:not(:disabled) {
    background: #000000;
    color: #ffffff;
}

.audit-btn.failure {
    background: #000000;
    color: #ffffff;
}

.audit-btn.failure:hover:not(:disabled) {
    background: #333333;
}

.audit-btn:disabled {
    opacity: 0.6;
    cursor: not-allowed;
}

.audit-complete {
    text-align: center;
}

.audit-result {
    padding: 2rem;
    border-radius: 8px;
    margin-bottom: 2rem;
    border: 2px solid #000000;
}

.audit-result.success {
    background: #f0f8f0;
}

.audit-result.failure {
    background: #f8f0f0;
}

.audit-result h3 {
    font-family: 'Roboto Mono', monospace;
    font-size: 1.3rem;
    font-weight: 700;
    margin-bottom: 1rem;
    color: #000000;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

.audit-motivation {
    background: #f8f8f8;
    border: 2px solid #e0e0e0;
    padding: 1.5rem;
    border-radius: 8px;
    text-align: left;
}

.audit-motivation h4 {
    font-family: 'Roboto Mono', monospace;
    margin-bottom: 1rem;
    color: #000000;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

.audit-motivation ul {
    list-style: none;
    padding-left: 0;
}

.audit-motivation li {
    padding: 0.5rem 0;
    padding-left: 1.5rem;
    position: relative;
    font-family: 'Roboto Mono', monospace;
    color: #333333;
}

.audit-motivation li::before {
    content: "▶";
    position: absolute;
    left: 0;
    color: #000000;
    font-weight: bold;
}

/* Responsive Design */
@media (max-width: 768px) {
    .app-header {
        padding: 1.5rem 1rem;
    }
    
    .app-header h1 {
        font-size: 2rem;
    }
    
    .app-main {
        padding: 1rem;
    }
    
    .task-header {
        flex-direction: column;
        align-items: stretch;
        text-align: center;
    }
    
    .task-actions {
        justify-content: center;
    }
    
    .chart-header {
        flex-direction: column;
        text-align: center;
    }
    
    .audit-buttons {
        flex-direction: column;
        align-items: center;
    }
    
    .stats-grid {
        grid-template-columns: 1fr;
    }
    
    .app-nav {
        flex-wrap: wrap;
    }
    
    .app-nav button {
        flex: 1;
        min-width: 120px;
    }
}

@media (max-width: 480px) {
    .task-form {
        margin: 0;
        border-radius: 0;
        max-height: 100vh;
        border: none;
        border-top: 2px solid #000000;
    }
    
    .app-header h1 {
        font-size: 1.8rem;
    }
    
    .task-content {
        padding: 1rem;
    }
    
    .entropy-animation {
        padding: 1rem;
    }
}

/* Animation improvements for better performance */
@media (prefers-reduced-motion: reduce) {
    * {
        animation-duration: 0.01ms !important;
        animation-iteration-count: 1 !important;
        transition-duration: 0.01ms !important;
    }
}'''
    
    update_file("frontend/src/styles/App.css", white_theme_css)
    
    # 4. Update task list component to use new styling classes
    print("🔧 Updating TaskList component...")
    
    with open("frontend/src/components/TaskList.js", 'r') as f:
        task_list_content = f.read()
    
    # Update priority badge styling
    task_list_content = task_list_content.replace(
        'style={{ backgroundColor: priorityConfig[task.priority].color }}',
        'className={`priority-badge ${priorityConfig[task.priority].label.toLowerCase()}`}'
    )
    
    update_file("frontend/src/components/TaskList.js", task_list_content)
    
    # 5. Create a restart script for easy testing
    restart_script = '''#!/bin/bash
echo "🔄 Restarting ENTROPY with new White Theme..."

# Kill existing processes
pkill -f "node.*server.js" || true
pkill -f "react-scripts" || true

# Wait a moment
sleep 2

echo "🎨 Starting ENTROPY with:"
echo "  ✅ White background & black text"
echo "  ✅ Modern Roboto Mono font"
echo "  ✅ Simplified, clean animations"
echo "  ✅ Mobile-optimized design"
echo ""

# Start the application
./start.sh'''
    
    update_file("restart_white_theme.sh", restart_script)
    os.chmod("restart_white_theme.sh", 0o755)
    
    print("\n🎉 ENTROPY White Theme Redesign Complete!")
    print("=" * 50)
    print("✅ Updated HTML with Roboto Mono font")
    print("✅ Redesigned entropy animation (simple & clean)")
    print("✅ Applied white background with black text")
    print("✅ Modern robotic typography throughout")
    print("✅ Mobile-optimized responsive design")
    print("✅ High contrast for perfect visibility")
    print("\n🚀 To see your new design:")
    print("./restart_white_theme.sh")
    print("\n🎨 Your app now features:")
    print("• Clean white background with sharp black text")
    print("• Modern Roboto Mono font for that robotic feel")
    print("• Simplified robot character animation")
    print("• Bold borders and clear visual hierarchy")
    print("• Perfect readability on any device")
    print("\n⚡ Clean, modern, and entropy-fighting ready! ⚡")

if __name__ == "__main__":
    main()
