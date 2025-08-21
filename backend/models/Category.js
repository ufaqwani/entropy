const mongoose = require('mongoose');

const categorySchema = new mongoose.Schema({
    user: {
        type: mongoose.Schema.Types.ObjectId,
        ref: 'User',
        required: true
    },
    name: {
        type: String,
        required: true,
        trim: true,
        maxLength: 50
    },
    description: {
        type: String,
        trim: true,
        maxLength: 200
    },
    color: {
        type: String,
        default: '#000000',
        match: /^#[0-9A-F]{6}$/i
    },
    icon: {
        type: String,
        trim: true,
        maxLength: 50,
        default: '📁'
    },
    isActive: {
        type: Boolean,
        default: true
    }
}, {
    timestamps: true
});

// Index for better query performance
categorySchema.index({ user: 1, name: 1 }, { unique: true });
categorySchema.index({ name: 1, isActive: 1 });

module.exports = mongoose.model('Category', categorySchema);