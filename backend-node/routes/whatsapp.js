const express = require('express');
const router = express.Router();
const twilio = require('twilio');
const axios = require('axios');

const FASTAPI_URL = process.env.FASTAPI_URL || 'http://localhost:8000';

// In-memory session store (use Redis in production)
const sessions = new Map();

// WhatsApp bot states
const STATES = {
  INIT: 'INIT',
  AWAIT_ACCOUNT: 'AWAIT_ACCOUNT',
  AWAIT_SCREENSHOT: 'AWAIT_SCREENSHOT',
  CONFIRM: 'CONFIRM',
  DONE: 'DONE'
};

router.post('/', async (req, res) => {
  try {
    const { From, Body, MediaUrl0 } = req.body;
    const phoneNumber = From.replace('whatsapp:', '');
    
    console.log(`📱 WhatsApp message from ${phoneNumber}: ${Body}`);
    
    // Get or create session
    let session = sessions.get(phoneNumber) || {
      state: STATES.INIT,
      data: {}
    };
    
    let responseMessage = '';
    
    // Handle commands
    if (Body.toLowerCase().startsWith('status ')) {
      const complaintId = Body.split(' ')[1];
      responseMessage = await getComplaintStatus(complaintId);
      return sendWhatsAppMessage(res, responseMessage);
    }
    
    if (Body.toLowerCase() === 'help') {
      responseMessage = `📋 *Help Menu*\n\n` +
        `• Type your complaint to file a new issue\n` +
        `• "status CMP1042" - Check complaint status\n` +
        `• "cancel" - Cancel current operation`;
      return sendWhatsAppMessage(res, responseMessage);
    }
    
    if (Body.toLowerCase() === 'cancel') {
      sessions.delete(phoneNumber);
      responseMessage = 'Operation cancelled. Type "help" for assistance.';
      return sendWhatsAppMessage(res, responseMessage);
    }
    
    // State machine
    switch (session.state) {
      case STATES.INIT:
        session.data.complaint = Body;
        session.state = STATES.AWAIT_ACCOUNT;
        responseMessage = '📝 Thank you. Please provide the last 4 digits of your account number:';
        break;
      
      case STATES.AWAIT_ACCOUNT:
        if (!/^\d{4}$/.test(Body)) {
          responseMessage = '❌ Please enter exactly 4 digits of your account number:';
        } else {
          session.data.accountLast4 = Body;
          session.state = STATES.AWAIT_SCREENSHOT;
          responseMessage = '📸 You can send a screenshot (optional) or type "skip" to continue:';
        }
        break;
      
      case STATES.AWAIT_SCREENSHOT:
        if (MediaUrl0) {
          session.data.screenshot = MediaUrl0;
        }
        session.state = STATES.CONFIRM;
        
        responseMessage = `✅ *Complaint Summary*\n\n` +
          `Issue: ${session.data.complaint}\n` +
          `Account: XXXX${session.data.accountLast4}\n\n` +
          `Type "confirm" to submit or "cancel" to restart.`;
        break;
      
      case STATES.CONFIRM:
        if (Body.toLowerCase() === 'confirm') {
          // Submit complaint to FastAPI
          const complaint = await submitComplaint({
            raw_text: session.data.complaint,
            channel: 'whatsapp',
            customer_phone: phoneNumber,
            customer_account_last4: session.data.accountLast4,
            region: 'Unknown'
          });
          
          session.state = STATES.DONE;
          sessions.delete(phoneNumber);
          
          responseMessage = `🎉 *Complaint Registered*\n\n` +
            `Ticket ID: *${complaint.complaint_id}*\n` +
            `Category: ${complaint.category}\n` +
            `Priority: ${complaint.severity}\n\n` +
            `We'll resolve this within ${getSLAHours(complaint.category)} hours.\n\n` +
            `Track status: "status ${complaint.complaint_id}"`;
        } else {
          responseMessage = 'Please type "confirm" to submit or "cancel" to restart.';
        }
        break;
      
      default:
        session.state = STATES.INIT;
        responseMessage = 'Please describe your issue:';
    }
    
    sessions.set(phoneNumber, session);
    sendWhatsAppMessage(res, responseMessage);
    
  } catch (error) {
    console.error('WhatsApp webhook error:', error);
    res.status(500).send('Error processing message');
  }
});

async function submitComplaint(data) {
  try {
    const response = await axios.post(`${FASTAPI_URL}/api/complaints/`, data);
    return response.data;
  } catch (error) {
    console.error('Error submitting complaint:', error.message);
    throw error;
  }
}

async function getComplaintStatus(complaintId) {
  try {
    // Extract numeric ID from CMP1042 format
    const complaints = await axios.get(`${FASTAPI_URL}/api/complaints/`);
    const complaint = complaints.data.find(c => c.complaint_id === complaintId);
    
    if (!complaint) {
      return `❌ Complaint ${complaintId} not found.`;
    }
    
    return `📊 *Status: ${complaintId}*\n\n` +
      `Status: ${complaint.status.toUpperCase()}\n` +
      `Category: ${complaint.category}\n` +
      `Priority: ${complaint.severity}\n` +
      `Created: ${new Date(complaint.created_at).toLocaleDateString()}\n\n` +
      `We're working on it! 💪`;
  } catch (error) {
    return '❌ Error fetching status. Please try again.';
  }
}

function getSLAHours(category) {
  const slaMap = {
    'ATM Failure': 24,
    'UPI Failure': 12,
    'Mobile App': 48,
    'Loan': 72,
    'Card': 24,
    'Net Banking': 48
  };
  return slaMap[category] || 48;
}

function sendWhatsAppMessage(res, message) {
  const twiml = new twilio.twiml.MessagingResponse();
  twiml.message(message);
  res.writeHead(200, { 'Content-Type': 'text/xml' });
  res.end(twiml.toString());
}

module.exports = router;
