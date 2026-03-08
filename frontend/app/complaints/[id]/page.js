'use client'

import { useState, useEffect } from 'react'
import { useParams } from 'next/navigation'
import { complaintsAPI, aiAPI } from '@/lib/api'
import { getSocket } from '@/lib/socket'
import { Clock, User, MessageSquare, Sparkles, FileText, AlertCircle } from 'lucide-react'

export default function ComplaintDetailPage() {
  const params = useParams()
  const [complaint, setComplaint] = useState(null)
  const [messages, setMessages] = useState([])
  const [newMessage, setNewMessage] = useState('')
  const [draftResponse, setDraftResponse] = useState(null)
  const [similarComplaints, setSimilarComplaints] = useState([])
  const [loading, setLoading] = useState(true)
  
  useEffect(() => {
    if (params.id) {
      loadComplaintData()
      
      const socket = getSocket()
      socket.emit('join_complaint', params.id)
      
      socket.on('new_message', (message) => {
        setMessages(prev => [...prev, message])
      })
      
      socket.on('complaint_update', (update) => {
        setComplaint(prev => ({ ...prev, ...update }))
      })
      
      return () => {
        socket.emit('leave_complaint', params.id)
        socket.off('new_message')
        socket.off('complaint_update')
      }
    }
  }, [params.id])
  
  const loadComplaintData = async () => {
    try {
      const [complaintRes, messagesRes] = await Promise.all([
        complaintsAPI.getById(params.id),
        complaintsAPI.getMessages(params.id)
      ])
      
      setComplaint(complaintRes.data)
      setMessages(messagesRes.data)
      
      // Load AI features
      loadAIFeatures(complaintRes.data)
    } catch (error) {
      console.error('Error loading complaint:', error)
    } finally {
      setLoading(false)
    }
  }
  
  const loadAIFeatures = async (complaint) => {
    try {
      // Generate draft response
      const draftRes = await aiAPI.generateDraft({
        complaint_text: complaint.raw_text,
        category: complaint.category,
        customer_name: complaint.customer_name || 'Customer'
      })
      setDraftResponse(draftRes.data)
      
      // Find similar complaints
      const similarRes = await aiAPI.findSimilar(complaint.raw_text)
      setSimilarComplaints(similarRes.data.similar_complaints || [])
    } catch (error) {
      console.error('Error loading AI features:', error)
    }
  }
  
  const handleSendMessage = async () => {
    if (!newMessage.trim()) return
    
    try {
      await complaintsAPI.addMessage(params.id, {
        sender: 'agent',
        message: newMessage,
        channel: complaint.channel
      })
      setNewMessage('')
      loadComplaintData()
    } catch (error) {
      console.error('Error sending message:', error)
    }
  }
  
  const handleEscalate = async () => {
    try {
      await complaintsAPI.escalate(params.id)
      loadComplaintData()
    } catch (error) {
      console.error('Error escalating:', error)
    }
  }
  
  const handleStatusChange = async (newStatus) => {
    try {
      await complaintsAPI.update(params.id, { status: newStatus })
      loadComplaintData()
    } catch (error) {
      console.error('Error updating status:', error)
    }
  }
  
  const useDraft = (version) => {
    setNewMessage(version === 'short' ? draftResponse.short_version : draftResponse.long_version)
  }
  
  if (loading) {
    return <div className="flex items-center justify-center h-64">
      <div className="text-lg">Loading complaint details...</div>
    </div>
  }
  
  if (!complaint) {
    return <div className="text-center py-12">
      <p className="text-xl text-gray-600">Complaint not found</p>
    </div>
  }
  
  const slaPercentage = complaint.sla_deadline 
    ? Math.min(100, ((new Date() - new Date(complaint.created_at)) / (new Date(complaint.sla_deadline) - new Date(complaint.created_at))) * 100)
    : 0
  
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">{complaint.complaint_id}</h1>
          <p className="text-gray-600 mt-1">{complaint.category} - {complaint.severity}</p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={handleEscalate}
            className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
          >
            Escalate
          </button>
          <select
            value={complaint.status}
            onChange={(e) => handleStatusChange(e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
          >
            <option value="pending">Pending</option>
            <option value="in_progress">In Progress</option>
            <option value="resolved">Resolved</option>
            <option value="escalated">Escalated</option>
          </select>
        </div>
      </div>
      
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column - Customer & Complaint Info */}
        <div className="space-y-6">
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-semibold mb-4">Customer Information</h2>
            <div className="space-y-3">
              <div>
                <p className="text-sm text-gray-600">Name</p>
                <p className="font-medium">{complaint.customer_name || 'Unknown'}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Phone</p>
                <p className="font-medium">{complaint.customer_phone || 'N/A'}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Account</p>
                <p className="font-medium">XXXX{complaint.customer_account_last4}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Tier</p>
                <span className={`px-2 py-1 text-xs font-medium rounded-full ${complaint.customer_tier === 'premium' ? 'bg-purple-100 text-purple-800' : 'bg-gray-100 text-gray-800'}`}>
                  {complaint.customer_tier}
                </span>
              </div>
            </div>
          </div>
          
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-semibold mb-4">Complaint Details</h2>
            <div className="space-y-3">
              <div>
                <p className="text-sm text-gray-600">Channel</p>
                <p className="font-medium capitalize">{complaint.channel}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Priority Score</p>
                <div className="flex items-center gap-2">
                  <div className="flex-1 bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-blue-600 h-2 rounded-full"
                      style={{ width: `${(complaint.priority_score / 10) * 100}%` }}
                    ></div>
                  </div>
                  <span className="font-bold">{complaint.priority_score?.toFixed(1)}</span>
                </div>
              </div>
              <div>
                <p className="text-sm text-gray-600">Sentiment</p>
                <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                  complaint.sentiment === 'Positive' ? 'bg-green-100 text-green-800' :
                  complaint.sentiment === 'Negative' ? 'bg-red-100 text-red-800' :
                  'bg-gray-100 text-gray-800'
                }`}>
                  {complaint.sentiment}
                </span>
              </div>
              <div>
                <p className="text-sm text-gray-600">Region</p>
                <p className="font-medium">{complaint.region}</p>
              </div>
            </div>
          </div>
          
          {/* SLA Timer */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
              <Clock className="w-5 h-5" />
              SLA Countdown
            </h2>
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span>Progress</span>
                <span className={slaPercentage > 80 ? 'text-red-600 font-semibold' : 'text-gray-600'}>
                  {slaPercentage.toFixed(0)}%
                </span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-3">
                <div
                  className={`h-3 rounded-full ${slaPercentage > 80 ? 'bg-red-500' : slaPercentage > 50 ? 'bg-yellow-500' : 'bg-green-500'}`}
                  style={{ width: `${Math.min(100, slaPercentage)}%` }}
                ></div>
              </div>
              <p className="text-sm text-gray-600">
                Deadline: {new Date(complaint.sla_deadline).toLocaleString()}
              </p>
            </div>
          </div>
        </div>
        
        {/* Center Column - Communication Timeline */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <MessageSquare className="w-5 h-5" />
            Communication Timeline
          </h2>
          
          <div className="space-y-4 mb-4 max-h-96 overflow-y-auto">
            {messages.map((msg) => (
              <div
                key={msg.id}
                className={`p-3 rounded-lg ${
                  msg.sender === 'customer' ? 'bg-blue-50 ml-0 mr-8' :
                  msg.sender === 'agent' ? 'bg-green-50 ml-8 mr-0' :
                  msg.sender === 'bot' ? 'bg-purple-50 ml-4 mr-4' :
                  'bg-gray-50 ml-4 mr-4'
                }`}
              >
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-xs font-semibold capitalize">{msg.sender}</span>
                  <span className="text-xs text-gray-500">
                    {new Date(msg.timestamp).toLocaleTimeString()}
                  </span>
                </div>
                <p className="text-sm">{msg.message}</p>
              </div>
            ))}
          </div>
          
          <div className="border-t pt-4">
            <textarea
              value={newMessage}
              onChange={(e) => setNewMessage(e.target.value)}
              placeholder="Type your response..."
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 resize-none"
              rows="3"
            />
            <div className="flex gap-2 mt-2">
              <button
                onClick={handleSendMessage}
                className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
              >
                Send
              </button>
              <button
                onClick={() => handleStatusChange('resolved')}
                className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
              >
                Send & Resolve
              </button>
            </div>
          </div>
        </div>
        
        {/* Right Column - AI Copilot */}
        <div className="space-y-6">
          {/* AI Summary */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
              <Sparkles className="w-5 h-5 text-yellow-500" />
              AI Summary
            </h2>
            <p className="text-sm text-gray-700">{complaint.ai_summary}</p>
          </div>
          
          {/* Similar Cases */}
          {similarComplaints.length > 0 && (
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-lg font-semibold mb-4">Similar Past Cases</h2>
              <div className="space-y-2">
                {similarComplaints.slice(0, 3).map((similar) => (
                  <div key={similar.complaint_id} className="p-2 bg-gray-50 rounded text-sm">
                    <p className="font-medium">Complaint #{similar.complaint_id}</p>
                    <p className="text-gray-600">Similarity: {(similar.similarity * 100).toFixed(0)}%</p>
                  </div>
                ))}
              </div>
            </div>
          )}
          
          {/* Draft Response */}
          {draftResponse && (
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
                <FileText className="w-5 h-5" />
                Draft Response
              </h2>
              
              <div className="space-y-4">
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <p className="text-sm font-medium text-gray-700">Short Version (SMS/WhatsApp)</p>
                    <button
                      onClick={() => useDraft('short')}
                      className="text-xs text-blue-600 hover:text-blue-800"
                    >
                      Use This
                    </button>
                  </div>
                  <p className="text-sm text-gray-600 bg-gray-50 p-3 rounded">
                    {draftResponse.short_version}
                  </p>
                </div>
                
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <p className="text-sm font-medium text-gray-700">Long Version (Email)</p>
                    <button
                      onClick={() => useDraft('long')}
                      className="text-xs text-blue-600 hover:text-blue-800"
                    >
                      Use This
                    </button>
                  </div>
                  <p className="text-sm text-gray-600 bg-gray-50 p-3 rounded whitespace-pre-wrap">
                    {draftResponse.long_version}
                  </p>
                </div>
              </div>
            </div>
          )}
          
          {/* Recommended Actions */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-semibold mb-4">Recommended Actions</h2>
            <ol className="list-decimal list-inside space-y-2 text-sm text-gray-700">
              <li>Verify customer account details</li>
              <li>Check transaction logs for {complaint.category}</li>
              <li>Initiate resolution process</li>
              <li>Update customer within 24 hours</li>
            </ol>
          </div>
        </div>
      </div>
    </div>
  )
}
