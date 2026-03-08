let io;

function initSocket(socketIo) {
  io = socketIo;
  
  io.on('connection', (socket) => {
    console.log('✅ Client connected:', socket.id);
    
    socket.on('disconnect', () => {
      console.log('❌ Client disconnected:', socket.id);
    });
    
    socket.on('join_complaint', (complaintId) => {
      socket.join(`complaint_${complaintId}`);
      console.log(`Socket ${socket.id} joined complaint_${complaintId}`);
    });
    
    socket.on('leave_complaint', (complaintId) => {
      socket.leave(`complaint_${complaintId}`);
    });
  });
  
  console.log('✅ Socket.IO initialized');
}

function emitNewComplaint(complaint) {
  if (io) {
    io.emit('new_complaint', complaint);
    console.log('📢 Emitted new_complaint event');
  }
}

function emitComplaintUpdate(complaintId, update) {
  if (io) {
    io.to(`complaint_${complaintId}`).emit('complaint_update', update);
    io.emit('complaint_list_update', { complaintId, update });
  }
}

function emitSLAAlert(complaint) {
  if (io) {
    io.emit('sla_alert', {
      complaint_id: complaint.complaint_id,
      type: 'breach',
      message: `SLA breach for ${complaint.complaint_id}`
    });
  }
}

function emitNewMessage(complaintId, message) {
  if (io) {
    io.to(`complaint_${complaintId}`).emit('new_message', message);
  }
}

module.exports = {
  initSocket,
  emitNewComplaint,
  emitComplaintUpdate,
  emitSLAAlert,
  emitNewMessage
};
