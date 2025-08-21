import React, { useState } from 'react';
import { motion } from 'framer-motion';
import axios from 'axios';

const DailyAudit = ({ progressData, onAuditComplete }) => {
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [auditSubmitted, setAuditSubmitted] = useState(progressData?.hasAudit || false);

    const submitAudit = async (success) => {
        try {
            setIsSubmitting(true);
            const today = new Date();
            today.setHours(0, 0, 0, 0);
            
            await axios.post('/api/progress/audit', {
                date: today.toISOString(),
                success
            });
            
            setAuditSubmitted(true);
            onAuditComplete();
        } catch (error) {
            console.error('Error submitting audit:', error);
            alert('Error submitting audit. Please try again.');
        } finally {
            setIsSubmitting(false);
        }
    };

    if (!progressData) {
        return (
            <div className="loading-container">
                <div className="loading-spinner"></div>
                <p>Loading audit data...</p>
            </div>
        );
    }

    return (
        <div className="daily-audit">
            <div className="audit-header">
                <h2>Daily Audit</h2>
                <p>Reflect on your battle against entropy today</p>
            </div>

            <div className="audit-summary">
                <div className="summary-card">
                    <h3>Today's Performance</h3>
                    <div className="performance-grid">
                        <div className="performance-item">
                            <span className="label">Tasks Completed:</span>
                            <span className="value">{progressData.completedTasks} / {progressData.totalTasks}</span>
                        </div>
                        <div className="performance-item">
                            <span className="label">Completion Rate:</span>
                            <span className="value">{progressData.completionRate}%</span>
                        </div>
                    </div>
                </div>
            </div>

            {!auditSubmitted ? (
                <motion.div 
                    className="audit-question"
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                >
                    <h3>Was today a success?</h3>
                    <p>Consider not just completion rate, but effort, learning, and progress toward your goals.</p>
                    
                    <div className="audit-buttons">
                        <motion.button
                            className="audit-btn success"
                            onClick={() => submitAudit(true)}
                            disabled={isSubmitting}
                            whileHover={{ scale: 1.05 }}
                            whileTap={{ scale: 0.95 }}
                        >
                            {isSubmitting ? 'Submitting...' : '✅ Yes - Victory!'}
                        </motion.button>
                        
                        <motion.button
                            className="audit-btn failure"
                            onClick={() => submitAudit(false)}
                            disabled={isSubmitting}
                            whileHover={{ scale: 1.05 }}
                            whileTap={{ scale: 0.95 }}
                        >
                            {isSubmitting ? 'Submitting...' : '❌ No - Entropy Won'}
                        </motion.button>
                    </div>
                </motion.div>
            ) : (
                <motion.div 
                    className="audit-complete"
                    initial={{ opacity: 0, scale: 0.9 }}
                    animate={{ opacity: 1, scale: 1 }}
                >
                    <div className={`audit-result ${progressData.success ? 'success' : 'failure'}`}>
                        <h3>
                            {progressData.success ? '🏆 Victory Recorded!' : '⚔️ Defeat Acknowledged'}
                        </h3>
                        <p>
                            {progressData.success 
                                ? 'Great job fighting entropy today!'
                                : 'Tomorrow is a new opportunity to fight back!'
                            }
                        </p>
                    </div>
                </motion.div>
            )}
        </div>
    );
};

export default DailyAudit;
