import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { FiCheck, FiInfo, FiAlertTriangle, FiX } from 'react-icons/fi';

const NotificationSystem = ({ notifications, removeNotification }) => {
    const getIcon = (type) => {
        switch (type) {
            case 'success': return <FiCheck />;
            case 'warning': return <FiAlertTriangle />;
            case 'error': return <FiX />;
            default: return <FiInfo />;
        }
    };

    const getColors = (type) => {
        switch (type) {
            case 'success': 
                return { bg: '#f0f8f0', border: '#4caf50', text: '#2e7d32' };
            case 'warning': 
                return { bg: '#fff8e1', border: '#ff9800', text: '#ef6c00' };
            case 'error': 
                return { bg: '#ffebee', border: '#f44336', text: '#c62828' };
            default: 
                return { bg: '#e3f2fd', border: '#2196f3', text: '#1565c0' };
        }
    };

    return (
        <div className="notification-container">
            <AnimatePresence>
                {notifications.map((notification) => {
                    const colors = getColors(notification.type);
                    
                    return (
                        <motion.div
                            key={notification.id}
                            initial={{ opacity: 0, y: -50, scale: 0.9 }}
                            animate={{ opacity: 1, y: 0, scale: 1 }}
                            exit={{ opacity: 0, y: -20, scale: 0.9 }}
                            transition={{ duration: 0.3 }}
                            className="notification"
                            style={{
                                backgroundColor: colors.bg,
                                borderColor: colors.border,
                                color: colors.text
                            }}
                        >
                            <div className="notification-icon">
                                {getIcon(notification.type)}
                            </div>
                            
                            <div className="notification-content">
                                <h4>{notification.title}</h4>
                                {notification.message && (
                                    <p>{notification.message}</p>
                                )}
                            </div>
                            
                            <button
                                className="notification-close"
                                onClick={() => removeNotification(notification.id)}
                                style={{ color: colors.text }}
                            >
                                <FiX />
                            </button>
                        </motion.div>
                    );
                })}
            </AnimatePresence>
        </div>
    );
};

// Hook to manage notifications
export const useNotifications = () => {
    const [notifications, setNotifications] = useState([]);

    const addNotification = (title, message = '', type = 'info', duration = 4000) => {
        const id = Date.now() + Math.random();
        const notification = { id, title, message, type };
        
        setNotifications(prev => [...prev, notification]);
        
        // Auto remove after duration
        setTimeout(() => {
            removeNotification(id);
        }, duration);
        
        return id;
    };

    const removeNotification = (id) => {
        setNotifications(prev => prev.filter(n => n.id !== id));
    };

    const clearAllNotifications = () => {
        setNotifications([]);
    };

    return {
        notifications,
        addNotification,
        removeNotification,
        clearAllNotifications
    };
};

export default NotificationSystem;