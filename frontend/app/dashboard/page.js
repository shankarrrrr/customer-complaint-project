'use client'

import { useState, useEffect } from 'react'
import { analyticsAPI } from '@/lib/api'
import { 
  AlertCircle, 
  CheckCircle, 
  Clock, 
  TrendingUp,
  AlertTriangle
} from 'lucide-react'
import { BarChart, Bar, LineChart, Line, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'

export default function DashboardPage() {
  const [summary, setSummary] = useState(null)
  const [trends, setTrends] = useState(null)
  const [loading, setLoading] = useState(true)
  
  useEffect(() => {
    loadData()
  }, [])
  
  const loadData = async () => {
    try {
      const [summaryRes, trendsRes] = await Promise.all([
        analyticsAPI.getSummary(),
        analyticsAPI.getTrends(30)
      ])
      setSummary(summaryRes.data)
      setTrends(trendsRes.data)
    } catch (error) {
      console.error('Error loading dashboard data:', error)
    } finally {
      setLoading(false)
    }
  }
  
  if (loading) {
    return <div className="flex items-center justify-center h-64">
      <div className="text-lg">Loading dashboard...</div>
    </div>
  }
  
  const kpiCards = [
    {
      title: 'Total Today',
      value: summary?.total_today || 0,
      icon: TrendingUp,
      color: 'blue',
      change: '+12%'
    },
    {
      title: 'Pending',
      value: summary?.pending || 0,
      icon: Clock,
      color: 'yellow',
    },
    {
      title: 'Resolved',
      value: summary?.resolved || 0,
      icon: CheckCircle,
      color: 'green',
    },
    {
      title: 'SLA Breached',
      value: summary?.sla_breached || 0,
      icon: AlertTriangle,
      color: 'red',
    },
  ]
  
  const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899']
  
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-gray-600 mt-1">Overview of complaint management system</p>
      </div>
      
      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {kpiCards.map((kpi) => {
          const Icon = kpi.icon
          return (
            <div key={kpi.title} className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">{kpi.title}</p>
                  <p className="text-3xl font-bold mt-2">{kpi.value}</p>
                  {kpi.change && (
                    <p className="text-sm text-green-600 mt-1">{kpi.change}</p>
                  )}
                </div>
                <div className={`p-3 rounded-lg bg-${kpi.color}-100`}>
                  <Icon className={`w-6 h-6 text-${kpi.color}-600`} />
                </div>
              </div>
            </div>
          )
        })}
      </div>
      
      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Category Distribution */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold mb-4">Complaints by Category</h2>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={trends?.by_category || []}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="category" angle={-45} textAnchor="end" height={100} />
              <YAxis />
              <Tooltip />
              <Bar dataKey="count" fill="#3b82f6" />
            </BarChart>
          </ResponsiveContainer>
        </div>
        
        {/* Channel Distribution */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold mb-4">Channel Distribution</h2>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={trends?.by_channel || []}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ channel, percent }) => `${channel}: ${(percent * 100).toFixed(0)}%`}
                outerRadius={80}
                fill="#8884d8"
                dataKey="count"
                nameKey="channel"
              >
                {(trends?.by_channel || []).map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>
      
      {/* Daily Volume Trend */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-semibold mb-4">Daily Complaint Volume (Last 30 Days)</h2>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={trends?.daily_volume || []}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="date" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Line type="monotone" dataKey="count" stroke="#3b82f6" strokeWidth={2} />
          </LineChart>
        </ResponsiveContainer>
      </div>
      
      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-sm font-medium text-gray-600">Avg Resolution Time</h3>
          <p className="text-2xl font-bold mt-2">{summary?.avg_resolution_time || 0}h</p>
        </div>
        
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-sm font-medium text-gray-600">Top Category</h3>
          <p className="text-2xl font-bold mt-2">{summary?.top_category || 'N/A'}</p>
        </div>
        
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-sm font-medium text-gray-600">This Week</h3>
          <p className="text-2xl font-bold mt-2">{summary?.total_week || 0}</p>
        </div>
      </div>
    </div>
  )
}
