import React, { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import axios from 'axios';
import { format } from 'date-fns';

const ProgressChart = () => {
    const [progressData, setProgressData] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        loadProgressData();
    }, []);

    const loadProgressData = async () => {
        try {
            setLoading(true);
            const response = await axios.get('/api/progress/history?days=30');
            
            const formattedData = response.data.reverse().map(item => ({
                ...item,
                date: format(new Date(item.date), 'MMM dd'),
                success: item.success ? 1 : 0
            }));
            
            setProgressData(formattedData);
        } catch (error) {
            console.error('Error loading progress data:', error);
        } finally {
            setLoading(false);
        }
    };

    if (loading) {
        return (
            <div className="loading-container">
                <div className="loading-spinner"></div>
                <p>Loading progress data...</p>
            </div>
        );
    }

    return (
        <div className="progress-chart">
            <div className="chart-header">
                <h2>Your Battle Against Entropy</h2>
            </div>

            {progressData.length > 0 ? (
                <div className="chart-container">
                    <ResponsiveContainer width="100%" height={300}>
                        <LineChart data={progressData}>
                            <CartesianGrid strokeDasharray="3 3" />
                            <XAxis dataKey="date" />
                            <YAxis domain={[0, 100]} />
                            <Tooltip />
                            <Line 
                                type="monotone" 
                                dataKey="completionRate" 
                                stroke="#3498db" 
                                strokeWidth={2}
                            />
                        </LineChart>
                    </ResponsiveContainer>
                </div>
            ) : (
                <div className="no-data">
                    <h3>No progress data yet</h3>
                    <p>Complete your daily audit to start tracking!</p>
                </div>
            )}
        </div>
    );
};

export default ProgressChart;
