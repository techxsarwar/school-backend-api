const mongoose = require('mongoose');

const studentSchema = new mongoose.Schema({
    rollNo: {
        type: Number,
        required: true,
        unique: true
    },
    name: {
        type: String,
        required: true
    },
    fatherName: {
        type: String
    },
    marks: {
        physics: Number,
        chemistry: Number,
        math: Number,
        total: Number
    },
    resultStatus: {
        type: String,
        enum: ['PASS', 'FAIL'],
        default: 'PASS'
    }
});

module.exports = mongoose.model('Student', studentSchema);
