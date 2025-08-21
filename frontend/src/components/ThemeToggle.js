import React from 'react';
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

export default ThemeToggle;