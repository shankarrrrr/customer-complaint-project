'use client'

import { useState, useEffect } from 'react'
import { analyticsAPI } from '@/lib/api'

export default function AnalyticsPage() {
  const [slaData, setSlaData] = useState(null)
  const [rootCause, setRootCause] = useState(null)
  const [loading, setLoading] = useState(true)
  
  useEffect(() => {
    loadAnalytics()
  }, [])
  
  const loadAnalytics = async () => {
    try {
      const [slaRes, rootCauseRes] = await Promise.all([
        analyticsAPI.getSLA(),
        analyticsAPI.getRootCause()
      ])
      setSlaData(slaRes.data)
      setRootCause(rootCauseRes.data)
    } catch (error) {
      console.error('Error loading analytics:', error)
    } finally {
      setLoading(false)
    }
  }
  
  if (loading) {
    return <div className="flex items-center justify-center h-64">
      <div className="text-lg">Loading analytics...</div>
    </div>
  }
  
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Analytics</h1>
        <p className="text-gray-600 mt-1">Detailed insights and performance metrics</p>
      </div>
      
      {/* SLA Performance */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold mb-4">SLA Performance by Category</h2>
        <div className="space-y-4">
          {slaData?.by_category?.map((item) => (
            <div key={item.category} className="border-b pb-4 last:border-b-0">
              <div className="flex items-center justify-between mb-2">
                <span className="font-medium">{item.category}</span>
                <span className={`text-sm ${item.compliance_rate >= 90 ? 'text-green-600' : item.compliance_rate >= 70 ? 'text-yellow-600' : 'text-red-600'}`}>
                  {item.compliance_rate}% Compliance
                </span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className={`h-2 rounded-full ${item.compliance_rate >= 90 ? 'bg-green-500' : item.compliance_rate >= 70 ? 'bg-yellow-500' : 'bg-red-500'}`}
                  style={{ width: `${item.compliance_rate}%` }}
                ></div>
              </div>
              <div className="flex justify-between text-sm text-gray-600 mt-1">
                <span>Total: {item.total}</span>
                <span>Breached: {item.breached}</span>
              </div>
            </div>
          ))}
        </div>
      </div>
      
      {/* Root Cause Insights */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold mb-4">AI Root Cause Insights</h2>
        <div className="space-y-4">
          {rootCause?.insights?.length === 0 ? (
            <p className="text-gray-500">No insights available yet. Patterns will appear as complaints accumulate.</p>
          ) : (
            rootCause?.insights?.map((insight) => (
              <div key={insight.cluster_id} className="border border-gray-200 rounded-lg p-4">
                <div className="flex items-start justify-between mb-2">
                  <h3 className="font-semibold text-lg">{insight.label}</h3>
                  <span className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm font-medium">
                    {insight.count} complaints
                  </span>
                </div>
                <div className="text-sm text-gray-600 mb-2">
                  <span className="font-medium">Region:</span> {insight.region} | 
                  <span className="font-medium ml-2">Category:</span> {insight.category}
                </div>
                <div className="bg-yellow-50 border-l-4 border-yellow-400 p-3 mt-3">
                  <p className="text-sm text-gray-700">{insight.root_cause}</p>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
      
      {/* Near Breach Alerts */}
      {slaData?.near_breach_count > 0 && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-6">
          <h2 className="text-xl font-semibold text-red-800 mb-4">
            ⚠️ Near SLA Breach ({slaData.near_breach_count} complaints)
          </h2>
          <div className="space-y-2">
            {slaData.near_breach_complaints.map((complaint) => (
              <div key={complaint.id} className="bg-white rounded p-3 flex items-center justify-between">
                <div>
                  <span className="font-medium">{complaint.complaint_id}</span>
                  <span className="text-sm text-gray-600 ml-3">{complaint.category}</span>
                </div>
                <span className="text-sm text-red-600">
                  Deadline: {new Date(complaint.sla_deadline).toLocaleString()}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
