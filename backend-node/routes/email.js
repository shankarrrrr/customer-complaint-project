const express = require('express');
const router = express.Router();
const Imap = require('imap');
const { simpleParser } = require('mailparser');
const axios = require('axios');

const FASTAPI_URL = process.env.FASTAPI_URL || 'http://localhost:8000';

// IMAP configuration
const imapConfig = {
  user: process.env.IMAP_USER,
  password: process.env.IMAP_PASSWORD,
  host: process.env.IMAP_HOST || 'imap.gmail.com',
  port: parseInt(process.env.IMAP_PORT) || 993,
  tls: true,
  tlsOptions: { rejectUnauthorized: false }
};

let isPolling = false;

// Start email polling
function startEmailPolling() {
  if (isPolling || !imapConfig.user || !imapConfig.password) {
    console.log('⚠️ Email polling not started (missing credentials or already running)');
    return;
  }
  
  isPolling = true;
  console.log('✅ Email polling started');
  
  setInterval(() => {
    checkNewEmails();
  }, 60000); // Check every 60 seconds
}

async function checkNewEmails() {
  const imap = new Imap(imapConfig);
  
  imap.once('ready', () => {
    imap.openBox('INBOX', false, (err, box) => {
      if (err) {
        console.error('Error opening inbox:', err);
        return;
      }
      
      // Search for unseen emails
      imap.search(['UNSEEN'], (err, results) => {
        if (err || !results || results.length === 0) {
          imap.end();
          return;
        }
        
        const fetch = imap.fetch(results, { bodies: '' });
        
        fetch.on('message', (msg) => {
          msg.on('body', (stream) => {
            simpleParser(stream, async (err, parsed) => {
              if (err) {
                console.error('Error parsing email:', err);
                return;
              }
              
              // Extract complaint data
              const complaintData = {
                raw_text: `${parsed.subject}\n\n${parsed.text}`,
                channel: 'email',
                customer_name: parsed.from.text,
                customer_phone: null,
                customer_account_last4: extractAccountNumber(parsed.text),
                region: 'Unknown'
              };
              
              try {
                // Submit to FastAPI
                const response = await axios.post(
                  `${FASTAPI_URL}/api/complaints/`,
                  complaintData
                );
                
                console.log(`✅ Email complaint created: ${response.data.complaint_id}`);
              } catch (error) {
                console.error('Error creating complaint from email:', error.message);
              }
            });
          });
        });
        
        fetch.once('end', () => {
          imap.end();
        });
      });
    });
  });
  
  imap.once('error', (err) => {
    console.error('IMAP error:', err);
  });
  
  imap.connect();
}

function extractAccountNumber(text) {
  // Try to extract 4-digit account number from text
  const match = text.match(/\b\d{4}\b/);
  return match ? match[0] : '0000';
}

// Manual trigger endpoint for testing
router.post('/', async (req, res) => {
  try {
    const { subject, body, from } = req.body;
    
    const complaintData = {
      raw_text: `${subject}\n\n${body}`,
      channel: 'email',
      customer_name: from,
      customer_phone: null,
      customer_account_last4: extractAccountNumber(body),
      region: 'Unknown'
    };
    
    const response = await axios.post(
      `${FASTAPI_URL}/api/complaints/`,
      complaintData
    );
    
    res.json({
      success: true,
      complaint_id: response.data.complaint_id
    });
  } catch (error) {
    console.error('Error processing email complaint:', error);
    res.status(500).json({ error: error.message });
  }
});

// Start polling when module loads
startEmailPolling();

module.exports = router;
