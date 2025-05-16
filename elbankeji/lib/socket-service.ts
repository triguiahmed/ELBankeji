/* eslint-disable @typescript-eslint/no-explicit-any, @typescript-eslint/no-unused-vars */
type MessageCallback = (message: any) => void
type StatusCallback = (status: ConnectionStatus) => void

export enum ConnectionStatus {
  CONNECTING = "connecting",
  CONNECTED = "connected",
  DISCONNECTED = "disconnected",
  ERROR = "error",
}

export interface ChatMessage {
  id: string
  content: string
  sender: "user" | "assistant"
  timestamp: Date
}

export class SocketService {
  private socket: WebSocket | null = null
  private url: string = "ws://localhost:8001/chat?user=John+Doe"
  private messageCallbacks: MessageCallback[] = []
  private statusCallbacks: StatusCallback[] = []
  private reconnectAttempts = 0
  private maxReconnectAttempts = 5
  private reconnectTimeout: NodeJS.Timeout | null = null
  private status: ConnectionStatus = ConnectionStatus.DISCONNECTED

  constructor(url: string) {
    this.url = url
  }

  // Connect to the WebSocket server
  connect(): void {
    if (this.socket?.readyState === WebSocket.OPEN) return

    this.updateStatus(ConnectionStatus.CONNECTING)

    try {
      this.socket = new WebSocket(this.url)

      this.socket.onopen = this.handleOpen.bind(this)
      this.socket.onmessage = this.handleMessage.bind(this)
      this.socket.onclose = this.handleClose.bind(this)
      this.socket.onerror = this.handleError.bind(this)
    } catch (error) {
      this.updateStatus(ConnectionStatus.ERROR)
      this.attemptReconnect()
    }
  }

  // Disconnect from the WebSocket server
  disconnect(): void {
    if (this.socket) {
      this.socket.close()
      this.socket = null
    }

    if (this.reconnectTimeout) {
      clearTimeout(this.reconnectTimeout)
      this.reconnectTimeout = null
    }

    this.updateStatus(ConnectionStatus.DISCONNECTED)
  }

  // Send a message to the server
  sendMessage(message: ChatMessage): void {
    if (this.socket?.readyState === WebSocket.OPEN) {
      this.socket.send(JSON.stringify(message))
    } else {
      console.error("Cannot send message, socket is not connected")
      // Queue message for when connection is restored
      this.connect()
    }
  }

  // Subscribe to incoming messages
  onMessage(callback: MessageCallback): () => void {
    this.messageCallbacks.push(callback)
    return () => {
      this.messageCallbacks = this.messageCallbacks.filter((cb) => cb !== callback)
    }
  }

  // Subscribe to connection status changes
  onStatusChange(callback: StatusCallback): () => void {
    this.statusCallbacks.push(callback)
    // Immediately call with current status
    callback(this.status)
    return () => {
      this.statusCallbacks = this.statusCallbacks.filter((cb) => cb !== callback)
    }
  }

  // Get current connection status
  getStatus(): ConnectionStatus {
    return this.status
  }

  // Private methods
  private handleOpen(event: Event): void {
    this.reconnectAttempts = 0
    this.updateStatus(ConnectionStatus.CONNECTED)
    console.log("WebSocket connection established")
  }

  private handleMessage(event: MessageEvent): void {
    try {
      console.log("Received message:", event.data)
      const data = event.data
      this.messageCallbacks.forEach((callback) => callback(data))
    } catch (error) {
      console.error("Error parsing message:", error)
    }
  }

  private handleClose(event: CloseEvent): void {
    this.updateStatus(ConnectionStatus.DISCONNECTED)
    console.log(`WebSocket connection closed: ${event.code} ${event.reason}`)
    this.attemptReconnect()
  }

  private handleError(event: Event): void {
    this.updateStatus(ConnectionStatus.ERROR)
    console.error("WebSocket error:", event)
    this.attemptReconnect()
  }

  private attemptReconnect(): void {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.log("Max reconnect attempts reached")
      return
    }

    const delay = Math.min(1000 * 2 ** this.reconnectAttempts, 30000)
    console.log(`Attempting to reconnect in ${delay}ms`)

    this.reconnectTimeout = setTimeout(() => {
      this.reconnectAttempts++
      this.connect()
    }, delay)
  }

  private updateStatus(status: ConnectionStatus): void {
    this.status = status
    this.statusCallbacks.forEach((callback) => callback(status))
  }
}

// Create a singleton instance
let socketInstance: SocketService | null = null

export const getSocketService = (url?: string): SocketService => {
  if (!socketInstance && url) {
    socketInstance = new SocketService(url)
  } else if (!socketInstance && !url) {
    throw new Error("Socket service not initialized. Provide a URL.")
  }

  return socketInstance as SocketService
}
