
"use client"

import * as React from "react"
import { MessageSquareIcon, SendIcon, WifiOffIcon, XIcon } from "lucide-react"
import { AnimatePresence, motion } from "framer-motion"

import { ConnectionStatus, type ChatMessage, type SocketService, getSocketService } from "@/lib/socket-service"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardFooter, CardHeader } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip"

// Replace with your actual WebSocket server URL
const SOCKET_URL = process.env.NEXT_PUBLIC_WEBSOCKET_URL || "ws://localhost:8001/chat?user=John+Doe"

export function ChatButton() {
  const [isOpen, setIsOpen] = React.useState(false)
  const [messages, setMessages] = React.useState<ChatMessage[]>([
    {
      id: "1",
      content: "Hello! How can I help you today?",
      sender: "assistant",
      timestamp: new Date(),
    },
  ])
  const [input, setInput] = React.useState("")
  const [connectionStatus, setConnectionStatus] = React.useState<ConnectionStatus>(ConnectionStatus.DISCONNECTED)
  const [isTyping, setIsTyping] = React.useState(false)
  const [isThinking, setIsThinking] = React.useState(false)
  const scrollAreaRef = React.useRef<HTMLDivElement>(null)
  const socketRef = React.useRef<SocketService | null>(null)

  // Initialize socket connection
  React.useEffect(() => {
    if (!socketRef.current) {
      try {
        socketRef.current = getSocketService(SOCKET_URL)
        console.log("Socket service initialized")
      } catch (error) {
        console.error("Failed to initialize socket service:", error)
        return
      }
    }

    // Subscribe to status changes
    const unsubscribeStatus = socketRef.current.onStatusChange((status) => {
      console.log("Connection status changed:", status)
      setConnectionStatus(status)
    })

    // Subscribe to incoming messages
    const unsubscribeMessage = socketRef.current.onMessage((data) => {
      console.log("Raw message received:", data)
      
      // Parse the data if it's a string (JSON)
      let parsedData
      try {
        parsedData =  data
        console.log("Parsed message:", parsedData)
      } catch (error) {
        console.error("Error parsing message:", error)
        parsedData = { content: typeof data === 'string' ? data : "Received message" }
      }
      
      if (parsedData.type === "thinking") {
        setIsThinking(parsedData.isThinking)
        if (!parsedData.isThinking) {
          setIsTyping(true) // Start typing when thinking ends
        }
      } else if (parsedData.type === "typing") {
        setIsTyping(parsedData.isTyping)
      } else if (parsedData.type === "message") {
        setIsThinking(false)
        setIsTyping(false)
        
        setMessages((prev) => [
          ...prev,
          {
            id: parsedData.id || Date.now().toString(),
            content: parsedData.content || "Empty message", // Extract the actual content
            sender: "assistant",
            timestamp: new Date(),
          },
        ])
      } else {
        // Fallback for messages without a type (direct messages)
        // This handles legacy or simple message formats
        const messageContent = parsedData.content || parsedData.message || 
                             (typeof parsedData === 'string' ? parsedData : JSON.stringify(parsedData))
        
        setIsThinking(false)
        setIsTyping(false)
        
        setMessages((prev) => [
          ...prev,
          {
            id: parsedData.id || Date.now().toString(),
            content: messageContent,
            sender: "assistant",
            timestamp: new Date(),
          },
        ])
      }
    })

    // Connect to the socket server when the chat is opened
    if (isOpen) {
      console.log("Chat opened, connecting to socket server")
      socketRef.current.connect()
    } else {
      console.log("Chat closed, not connecting")
    }

    return () => {
      console.log("Cleaning up socket subscriptions")
      unsubscribeStatus()
      unsubscribeMessage()
    }
  }, [isOpen])

  const toggleChat = () => {
    const newIsOpen = !isOpen
    setIsOpen(newIsOpen)

    // Connect or disconnect based on chat state
    if (newIsOpen) {
      if (socketRef.current) {
        console.log("Opening chat, connecting to socket...")
        socketRef.current.connect()
      }
    } else {
      console.log("Closing chat")
      // Optionally disconnect when closing chat
      // socketRef.current?.disconnect()
    }
  }

  const handleSendMessage = (e: React.FormEvent) => {
    e.preventDefault()

    if (!input.trim()) return

    // Create message object
    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      content: input,
      sender: "user",
      timestamp: new Date(),
    }

    // Add to local state
    setMessages((prev) => [...prev, userMessage])
    setInput("")

    // Show thinking state immediately
    setIsThinking(true)

    // Send to server if connected
    if (socketRef.current) {
      if (connectionStatus === ConnectionStatus.CONNECTED) {
        console.log("Sending message to server:", userMessage)
        try {
          socketRef.current.sendMessage(userMessage)
        } catch (error) {
          console.error("Error sending message:", error)
          handleDisconnectedMessage()
        }
      } else {
        console.warn("Not connected, status:", connectionStatus)
        handleDisconnectedMessage()
      }
    } else {
      console.error("Socket reference is null")
      handleDisconnectedMessage()
    }
  }

  // Handle the case when disconnected
  const handleDisconnectedMessage = () => {
    setTimeout(() => {
      setIsThinking(false)
      setMessages((prev) => [
        ...prev,
        {
          id: (Date.now() + 1).toString(),
          content: "I'm currently offline. Please try again later.",
          sender: "assistant",
          timestamp: new Date(),
        },
      ])
    }, 1000)
  }

  // Scroll to bottom when messages change
  React.useEffect(() => {
    if (scrollAreaRef.current) {
      const scrollContainer = scrollAreaRef.current.querySelector("[data-radix-scroll-area-viewport]")
      if (scrollContainer) {
        scrollContainer.scrollTop = scrollContainer.scrollHeight
      }
    }
  }, [messages, isTyping, isThinking])

  // Add ping function to check connection
  const pingServer = React.useCallback(() => {
    if (socketRef.current && connectionStatus === ConnectionStatus.CONNECTED) {
      try {
        // Send a simple ping message
        socketRef.current.sendMessage({
          id: `ping-${Date.now()}`,
          content: "_ping",
          sender: "",
          timestamp: new Date(),
        })
        console.log("Ping sent to server")
      } catch (error) {
        console.error("Error sending ping:", error)
      }
    }
  }, [connectionStatus])

  // Set up periodic ping to keep connection alive
  React.useEffect(() => {
    if (!isOpen) return

    const pingInterval = setInterval(() => {
      pingServer()
    }, 30000) // Ping every 30 seconds

    return () => {
      clearInterval(pingInterval)
    }
  }, [isOpen, pingServer])

  // Handle connection status changes
  React.useEffect(() => {
    console.log("Connection status is now:", connectionStatus)
    
    if (connectionStatus === ConnectionStatus.ERROR || 
        connectionStatus === ConnectionStatus.DISCONNECTED) {
      // Try to reconnect when disconnected
      if (socketRef.current && isOpen) {
        console.log("Attempting to reconnect...")
        setTimeout(() => {
          try {
            socketRef.current?.connect()
          } catch (error) {
            console.error("Reconnection attempt failed:", error)
          }
        }, 2000)
      }
    }
  }, [connectionStatus, isOpen])

  return (
    <div className="fixed bottom-4 right-4 z-50">
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, scale: 0.9, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.9, y: 20 }}
            transition={{ type: "spring", damping: 25, stiffness: 300 }}
            className="absolute bottom-16 right-0"
          >
            <Card className="w-80 shadow-lg">
              <CardHeader className="flex flex-row items-center justify-between p-4 pb-2">
                <div className="flex items-center gap-2">
                  <Avatar className="h-8 w-8">
                    <AvatarImage src="/placeholder.svg?height=32&width=32" />
                    <AvatarFallback>EB</AvatarFallback>
                  </Avatar>
                  <div className="flex flex-col">
                    <div className="font-medium">ElBankeji Support Chat</div>
                    <div className="text-xs text-muted-foreground flex items-center gap-1">
                      {connectionStatus === ConnectionStatus.CONNECTED ? (
                        <span className="flex items-center">
                          <span className="h-2 w-2 rounded-full bg-green-500 mr-1"></span>
                          Online
                        </span>
                      ) : connectionStatus === ConnectionStatus.CONNECTING ? (
                        <span className="flex items-center">
                          <span className="h-2 w-2 rounded-full bg-yellow-500 mr-1"></span>
                          Connecting...
                        </span>
                      ) : (
                        <span className="flex items-center">
                          <span className="h-2 w-2 rounded-full bg-red-500 mr-1"></span>
                          Offline
                        </span>
                      )}
                    </div>
                  </div>
                </div>
                <Button variant="ghost" size="icon" onClick={toggleChat} className="h-8 w-8">
                  <XIcon className="h-4 w-4" />
                </Button>
              </CardHeader>
              <ScrollArea ref={scrollAreaRef} className="h-64">
                <CardContent className="p-4 pt-2">
                  <div className="flex flex-col gap-3">
                    {messages.map((message) => (
                      <div
                        key={message.id}
                        className={`flex ${message.sender === "user" ? "justify-end" : "justify-start"}`}
                      >
                        <div
                          className={`max-w-[80%] rounded-lg px-3 py-2 text-sm ${
                            message.sender === "user" ? "bg-primary text-primary-foreground" : "bg-muted"
                          }`}
                        >
                          {message.content}
                        </div>
                      </div>
                    ))}
                    {isThinking && (
                      <div className="flex justify-start">
                        <div className="max-w-[80%] rounded-lg px-3 py-2 text-sm bg-muted">
                          <span className="flex items-center gap-2">
                            <span className="text-xs text-muted-foreground">Thinking</span>
                            <span className="flex gap-1">
                              <span className="typing-dot animate-pulse">.</span>
                              <span className="typing-dot animate-pulse delay-75">.</span>
                              <span className="typing-dot animate-pulse delay-150">.</span>
                            </span>
                          </span>
                        </div>
                      </div>
                    )}
                    {isTyping && (
                      <div className="flex justify-start">
                        <div className="max-w-[80%] rounded-lg px-3 py-2 text-sm bg-muted">
                          <span className="flex gap-1">
                            <span className="typing-dot animate-pulse">.</span>
                            <span className="typing-dot animate-pulse delay-75">.</span>
                            <span className="typing-dot animate-pulse delay-150">.</span>
                          </span>
                        </div>
                      </div>
                    )}
                  </div>
                </CardContent>
              </ScrollArea>
              <CardFooter className="p-3">
                <form onSubmit={handleSendMessage} className="flex w-full gap-2">
                  <Input
                    placeholder="Type your message..."
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    className="flex-1"
                    disabled={connectionStatus === ConnectionStatus.ERROR}
                  />
                  <TooltipProvider>
                    <Tooltip>
                      <TooltipTrigger asChild>
                        <Button
                          type="submit"
                          size="icon"
                          className="shrink-0"
                          disabled={connectionStatus === ConnectionStatus.ERROR}
                        >
                          <SendIcon className="h-4 w-4" />
                        </Button>
                      </TooltipTrigger>
                      <TooltipContent side="top">
                        {connectionStatus === ConnectionStatus.CONNECTED ? "Send message" : "Reconnecting..."}
                      </TooltipContent>
                    </Tooltip>
                  </TooltipProvider>
                </form>
              </CardFooter>
            </Card>
          </motion.div>
        )}
      </AnimatePresence>

      <TooltipProvider>
        <Tooltip>
          <TooltipTrigger asChild>
            <Button
              onClick={toggleChat}
              size="icon"
              className={`h-12 w-12 rounded-full shadow-lg transition-all ${
                isOpen ? "bg-muted text-muted-foreground" : "bg-primary text-primary-foreground"
              }`}
            >
              {connectionStatus === ConnectionStatus.ERROR || connectionStatus === ConnectionStatus.DISCONNECTED ? (
                <WifiOffIcon className="h-5 w-5" />
              ) : (
                <MessageSquareIcon className="h-5 w-5" />
              )}
              {!isOpen && messages.length > 1 && (
                <span className="absolute -right-1 -top-1 flex h-5 w-5 items-center justify-center rounded-full bg-destructive text-xs text-destructive-foreground">
                  {messages.filter((m) => m.sender === "assistant" && !m.id.includes("1")).length}
                </span>
              )}
            </Button>
          </TooltipTrigger>
          <TooltipContent side="left">{isOpen ? "Close chat" : "Open ElBankeji support chat"}</TooltipContent>
        </Tooltip>
      </TooltipProvider>
    </div>
  )
}