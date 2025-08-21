const mongoose = require('mongoose');

const progressSchema = new mongoose.Schema({
    user: {
        type: mongoose.Schema.Types.ObjectId,
        ref: 'User',
        required: true
    },
    date: {
        type: Date,
        required: true
    },
    success: {
        type: Boolean,
        required: true
    },
    totalTasks: {
        type: Number,
        required: true,
        default: 0
    },
    completedTasks: {
        type: Number,
        required: true,
        default: 0
    },
    completionRate: {
        type: Number,
        min: 0,
        max: 100
    }
}, {
    timestamps: true
});

progressSchema.index({ user: 1, date: -1 }, { unique: true });

module.exports = mongoose.model('Progress', progressSchema);