const mongoose = require('mongoose');

const templateSchema = new mongoose.Schema({
    user: {
        type: mongoose.Schema.Types.ObjectId,
        ref: 'User',
        required: true
    },
    name: {
        type: String,
        required: true,
        trim: true,
        maxLength: 100
    },
    description: {
        type: String,
        trim: true,
        maxLength: 500
    },
    category: {
        type: mongoose.Schema.Types.ObjectId,
        ref: 'Category',
        required: true
    },
    taskTemplate: {
        title: {
            type: String,
            required: true,
            trim: true,
            maxLength: 200
        },
        description: {
            type: String,
            trim: true,
            maxLength: 1000
        },
        priority: {
            type: Number,
            required: true,
            min: 1,
            max: 3,
            default: 2
        }
    },
    recurrence: {
        type: {
            type: String,
            required: true,
            enum: ['daily', 'weekly', 'monthly', 'custom']
        },
        interval: {
            type: Number,
            default: 1,
            min: 1
        },
        daysOfWeek: [{
            type: Number,
            min: 0,
            max: 6
        }], // 0 = Sunday, 1 = Monday, etc.
        dayOfMonth: {
            type: Number,
            min: 1,
            max: 31
        },
        time: {
            hour: {
                type: Number,
                default: 5,
                min: 0,
                max: 23
            },
            minute: {
                type: Number,
                default: 0,
                min: 0,
                max: 59
            }
        }
    },
    isActive: {
        type: Boolean,
        default: true
    },
    nextRun: {
        type: Date,
        required: true
    },
    lastRun: {
        type: Date
    },
    createdTasksCount: {
        type: Number,
        default: 0
    }
}, {
    timestamps: true
});

// Index for better query performance
templateSchema.index({ isActive: 1, nextRun: 1 });
templateSchema.index({ category: 1, isActive: 1 });

// Method to calculate next run date
templateSchema.methods.calculateNextRun = function() {
    const now = new Date();
    const next = new Date();
    
    // Set to the specified time (default 5 AM for 5 AM day boundary)
    next.setHours(this.recurrence.time.hour, this.recurrence.time.minute, 0, 0);
    
    switch (this.recurrence.type) {
        case 'daily':
            if (next <= now) {
                next.setDate(next.getDate() + this.recurrence.interval);
            }
            break;
            
        case 'weekly':
            // Find next occurrence of specified days
            const targetDays = this.recurrence.daysOfWeek || [1]; // Default Monday
            let found = false;
            
            for (let i = 0; i < 14; i++) { // Check next 2 weeks
                const checkDate = new Date(next);
                checkDate.setDate(checkDate.getDate() + i);
                
                if (targetDays.includes(checkDate.getDay()) && checkDate > now) {
                    next.setDate(next.getDate() + i);
                    found = true;
                    break;
                }
            }
            
            if (!found) {
                next.setDate(next.getDate() + 7 * this.recurrence.interval);
            }
            break;
            
        case 'monthly':
            const targetDay = this.recurrence.dayOfMonth || 1;
            next.setDate(targetDay);
            
            if (next <= now) {
                next.setMonth(next.getMonth() + this.recurrence.interval);
                next.setDate(targetDay);
            }
            break;
            
        default:
            // Custom - add interval days
            if (next <= now) {
                next.setDate(next.getDate() + this.recurrence.interval);
            }
    }
    
    return next;
};

module.exports = mongoose.model('Template', templateSchema);