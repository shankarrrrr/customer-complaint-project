const express = require('express');
const http = require('http');
const socketIo = require('socket.io');
const cors = require('cors');
const bodyParser = require('body-parser');
require('dotenv').config();

const whatsappRouter = require('./routes/whatsapp');
const emailRouter = require('./routes/email');
const { initSocket } = require('./socket/socketHandler');

const app = express();
const server = http.createServer(app);
const io = socketIo(server, {
  cors: {
    origin: ["http://localhost:3000", "http://localhost:8000"],
    methods: ["GET", "POST"]
  }
});

// Middleware
app.use(cors());
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true }));

// Initialize Socket.IO
initSocket(io);

// Routes
app.use('/webhook/whatsapp', whatsappRouter);
app.use('/webhook/email', emailRouter);

app.get('/health', (req, res) => {
  res.json({ status: 'healthy', service: 'node-backend' });
});

app.get('/', (req, res) => {
  res.json({
    message: 'Complaint Backend - Node.js',
    endpoints: [
      '/webhook/whatsapp',
      '/webhook/email',
      '/health'
    ]
  });
});

const PORT = process.env.NODE_API_PORT || 3001;

server.listen(PORT, () => {
  console.log(`✅ Node.js server running on port ${PORT}`);
  console.log(`✅ WebSocket server ready`);
});

module.exports = { io };
