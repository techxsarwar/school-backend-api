const express = require('express');
const mongoose = require('mongoose');
const http = require('http');
const { Server } = require('socket.io');
const cors = require('cors');

const app = express();
const server = http.createServer(app);

// 1. Config & Middleware
app.use(cors());
app.use(express.json());

// 2. Database Connection
// REPLACE WITH YOUR ACTUAL CONNECTION STRING
const MONGO_URI = "mongodb+srv://<username>:<password>@cluster0.mongodb.net/school_db?retryWrites=true&w=majority";

mongoose.connect(MONGO_URI)
    .then(() => console.log('✅ MongoDB Connected'))
    .catch(err => console.error('❌ DB Connection Error:', err));

// 3. Database Model (Inline)
const studentSchema = new mongoose.Schema({
    rollNo: { type: Number, required: true, unique: true },
    name: { type: String, required: true },
    class: { type: String }, // Flexible field
    fatherName: String,
    marks: {
        physics: Number,
        chemistry: Number,
        math: Number,
        total: Number
    },
    resultStatus: { type: String, enum: ['PASS', 'FAIL'], default: 'PASS' }
});

const Student = mongoose.model('Student', studentSchema);

// 4. Socket.io Setup
const io = new Server(server, {
    cors: {
        origin: "*", // Allow all origins for simplicity
        methods: ["GET", "POST"]
    }
});

io.on('connection', (socket) => {
    console.log('⚡ New Client Connected:', socket.id);

    socket.on('disconnect', () => {
        console.log('Client Disconnected');
    });
});

// 5. API Routes

// GET /api/students - Fetch all students
app.get('/api/students', async (req, res) => {
    try {
        const students = await Student.find().sort({ rollNo: 1 });
        res.json(students);
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
});

// POST /api/upload - Bulk Upload
app.post('/api/upload', async (req, res) => {
    try {
        const students = req.body;
        if (!Array.isArray(students)) {
            return res.status(400).json({ error: "Expected an array of students" });
        }

        // Drop duplicates logic is handled by 'unique: true' in schema usually,
        // but 'insertMany' with 'ordered: false' allows partial success.
        // We will clear existing data first OR try to upsert.
        // For this 'Command Center' demo, let's keep it simple: insertNew.
        // To avoid duplicate key errors halting everything:

        const result = await Student.insertMany(students, { ordered: false });

        // 🚀 REAL-TIME TRIGGER
        // Fetch the updated full list (or just send the new ones)
        // Sending the full list ensures absolute sync for the dashboard
        const allStudents = await Student.find().sort({ rollNo: 1 });

        io.emit('database_update', allStudents);
        console.log(`📢 Emitted database_update with ${allStudents.length} records`);

        res.status(201).json({ message: "Upload Successful", count: result.length });

    } catch (err) {
        // Handle partial success (duplicates ignored)
        if (err.writeErrors) {
            // Even if some failed, we probably added some. Emit update!
            const allStudents = await Student.find().sort({ rollNo: 1 });
            io.emit('database_update', allStudents);

            res.status(201).json({
                message: "Partial Upload (Duplicates skipped)",
                inserted: err.insertedDocs.length
            });
        } else {
            res.status(500).json({ error: err.message });
        }
    }
});

// Start Server
const PORT = process.env.PORT || 5000;
server.listen(PORT, () => {
    console.log(`🚀 Server running on http://localhost:${PORT}`);
});
