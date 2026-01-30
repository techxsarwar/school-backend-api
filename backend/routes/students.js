const express = require('express');
const router = express.Router();
const Student = require('../models/Student');

// POST /api/students/bulk-upload
// Expects an array of student objects
router.post('/bulk-upload', async (req, res) => {
    try {
        const students = req.body;
        if (!Array.isArray(students)) {
            return res.status(400).json({ message: "Invalid data format. Expected an array." });
        }

        // insertMany with { ordered: false } ensures that if one duplicate fails, 
        // the rest continue to be inserted.
        try {
            const result = await Student.insertMany(students, { ordered: false });
            res.status(201).json({
                message: "Bulk upload successful",
                count: result.length,
                data: result
            });
        } catch (insertError) {
            // Partial success (some duplicates skipped)
            res.status(207).json({
                message: "Bulk upload completed with some skipped duplicates.",
                insertedCount: insertError.insertedDocs ? insertError.insertedDocs.length : 0,
                error: insertError.message
            });
        }

    } catch (err) {
        res.status(500).json({ message: "Server Error", error: err.message });
    }
});

// GET /api/students
// Returns all students sorted by Roll No
router.get('/', async (req, res) => {
    try {
        const students = await Student.find().sort({ rollNo: 1 });
        res.json(students);
    } catch (err) {
        res.status(500).json({ message: err.message });
    }
});

// DELETE /api/students/clear
// Deletes ALL data
router.delete('/clear', async (req, res) => {
    try {
        await Student.deleteMany({});
        res.json({ message: "All student data cleared successfully." });
    } catch (err) {
        res.status(500).json({ message: err.message });
    }
});

module.exports = router;
