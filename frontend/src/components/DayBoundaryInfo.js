import React, { useState, useEffect } from 'react';
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

export default DayBoundaryInfo;