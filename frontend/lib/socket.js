import { io } from 'socket.io-client'

const WS_URL = process.env.NEXT_PUBLIC_WS_URL || 'http://localhost:3001'

let socket = null

export const initSocket = () => {
  if (!socket) {
    socket = io(WS_URL, {
      transports: ['websocket'],
      reconnection: true,
      reconnectionDelay: 1000,
      reconnectionAttempts: 5,
    })
    
    socket.on('connect', () => {
      console.log('✅ WebSocket connected')
    })
    
    socket.on('disconnect', () => {
      console.log('❌ WebSocket disconnected')
    })
    
    socket.on('connect_error', (error) => {
      console.error('WebSocket connection error:', error)
    })
  }
  
  return socket
}

export const getSocket = () => {
  if (!socket) {
    return initSocket()
  }
  return socket
}

export const disconnectSocket = () => {
  if (socket) {
    socket.disconnect()
    socket = null
  }
}
