import React from 'react';
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

export default EntropyAnimation;