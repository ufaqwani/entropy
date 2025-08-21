// Date utilities for 5 AM day boundary system
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
};