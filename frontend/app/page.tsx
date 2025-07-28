"use client"

import { useState, useEffect } from "react"
import { MobileFrame } from "@/components/mobile-frame"
import { HomeScreen } from "@/components/home-screen"
import { ChatInterface } from "@/components/chat-interface"
import { Header } from "@/components/header"
import { RecentChatsScreen } from "@/components/recent-chats-screen"
import { ProfileScreen } from "@/components/profile-screen"
import { BottomNavigation } from "@/components/bottom-navigation"
import { sendChatMessage } from "@/lib/services/chat"
import type { ConversationContext as BackendConversationContext } from "@/lib/services/chat"
import { isAuthenticated, redirectToLogin } from "@/lib/auth" // Import auth utilities
import { useIsMobile } from "@/hooks/use-is-mobile"

type AppScreen = "home" | "chat" | "recent" | "profile"
type NavigationTab = "home" | "recent" | "profile"
type ChatContext = "wardrobe" | "style" | "currency" | "general"

interface Message {
  id: string
  text: string
  isUser: boolean
  timestamp: string
  quickReplies?: Array<{ id: string; text: string; emoji?: string }>
  showFeedback?: boolean
}

export default function TravelStyleApp() {
  const [currentScreen, setCurrentScreen] = useState<AppScreen>("home")
  const [activeTab, setActiveTab] = useState<NavigationTab>("home")
  const [chatContext, setChatContext] = useState<ChatContext>("general")
  const [messages, setMessages] = useState<Message[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [isAuthChecked, setIsAuthChecked] = useState(false) // New state for auth check

  const fullName = "Sarah Johnson" // This would come from user context after login
  const firstName = fullName.split(" ")[0]

  const isMobile = useIsMobile()

  useEffect(() => {
    // Check authentication status on mount
    if (!isAuthenticated()) {
      redirectToLogin()
    } else {
      setIsAuthChecked(true)
    }
  }, [])

  if (!isAuthChecked) {
    // Optionally render a loading spinner or null while checking auth
    return null
  }

  const generateResponse = async (userMessage: string, context: ChatContext): Promise<Message> => {
    try {
      const backendContext: BackendConversationContext = {
        user_id: "mock_user_id", // Replace with actual user ID from auth
        // Map frontend context to backend context if needed
      }

      const response = await sendChatMessage(userMessage, backendContext)

      return {
        id: Date.now().toString(),
        text: response.message,
        isUser: false,
        timestamp: new Date(response.timestamp).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
        quickReplies: response.quick_replies.map((qr) => ({
          id: qr.action || qr.text,
          text: qr.text,
          emoji: "💬",
        })),
        showFeedback: true,
      }
    } catch (error: any) {
      console.error("Failed to get AI response from backend:", error)
      // Handle 401 Unauthorized specifically
      if (error.message && error.message.includes("401")) {
        redirectToLogin() // Redirect to login if unauthorized
        return {
          id: Date.now().toString(),
          text: "Your session has expired. Please log in again.",
          isUser: false,
          timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
          quickReplies: [],
          showFeedback: false,
        }
      }
      return {
        id: Date.now().toString(),
        text: "I'm sorry, I couldn't connect to the AI service. Please try again later.",
        isUser: false,
        timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
        quickReplies: [],
        showFeedback: false,
      }
    }
  }

  const handleTabChange = (tab: NavigationTab) => {
    setActiveTab(tab)
    setCurrentScreen(tab)

    if (tab !== "home" && currentScreen === "chat") {
      setMessages([])
      setChatContext("general")
    }
  }

  const handleActionSelect = (actionId: string) => {
    if (actionId === "recent") {
      setActiveTab("recent")
      setCurrentScreen("recent")
      return
    }

    let context: ChatContext = "general"
    let initialMessage = ""

    switch (actionId) {
      case "wardrobe":
        context = "wardrobe"
        initialMessage = "I'd like help planning my travel wardrobe"
        break
      case "style":
        context = "style"
        initialMessage = "I want to learn about style etiquette"
        break
      case "currency":
        context = "currency"
        initialMessage = "I need help with currency conversion"
        break
      case "chat":
        context = "general"
        initialMessage = "Hi! I'd like to start a conversation"
        break
    }

    setChatContext(context)
    setCurrentScreen("chat")
    setActiveTab("home")

    const userMessage: Message = {
      id: Date.now().toString(),
      text: initialMessage,
      isUser: true,
      timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
    }

    setMessages([userMessage])

    setIsLoading(true)
    generateResponse(initialMessage, context).then((aiResponse) => {
      setMessages((prev) => [...prev, aiResponse])
      setIsLoading(false)
    })
  }

  const handleSendMessage = (message: string) => {
    const userMessage: Message = {
      id: Date.now().toString(),
      text: message,
      isUser: true,
      timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
    }

    setMessages((prev) => [...prev, userMessage])

    setIsLoading(true)
    generateResponse(message, chatContext).then((aiResponse) => {
      setMessages((prev) => [...prev, aiResponse])
      setIsLoading(false)
    })
  }

  const handleQuickReply = (buttonId: string, text: string) => {
    if (["wardrobe", "style", "currency"].includes(buttonId)) {
      setChatContext(buttonId as ChatContext)
    }

    handleSendMessage(text)
  }

  const handleFeedback = (messageId: string, type: "positive" | "negative") => {
    console.log(`Feedback for message ${messageId}: ${type}`)
  }

  const handleBackToHome = () => {
    setCurrentScreen("home")
    setActiveTab("home")
    setMessages([])
    setChatContext("general")
  }

  const getScreenTitle = () => {
    switch (chatContext) {
      case "wardrobe":
        return "Wardrobe Planning"
      case "style":
        return "Style Etiquette"
      case "currency":
        return "Currency Converter"
      default:
        return "TravelStyle AI"
    }
  }

  const handleChatSelect = (chatId: string) => {
    console.log(`Loading chat: ${chatId}`)
    setCurrentScreen("chat")
    setActiveTab("home")
    setChatContext("general")
    setMessages([])
  }

  const renderCurrentScreen = () => {
    switch (currentScreen) {
      case "home":
        return <HomeScreen onActionSelect={handleActionSelect} userName={firstName} />
      case "recent":
        return <RecentChatsScreen onBack={() => handleTabChange("home")} onChatSelect={handleChatSelect} />
      case "profile":
        return <ProfileScreen onBack={() => handleTabChange("home")} />
      case "chat":
        return (
          <div className="flex flex-col h-full bg-[#F8F6FF]">
            <Header title={getScreenTitle()} showBack={true} onBack={handleBackToHome} />
            <ChatInterface
              messages={messages}
              onSendMessage={handleSendMessage}
              onQuickReply={handleQuickReply}
              onFeedback={handleFeedback}
              isLoading={isLoading}
            />
          </div>
        )
      default:
        return <HomeScreen onActionSelect={handleActionSelect} userName={firstName} />
    }
  }

  return (
    <div className="min-h-screen bg-gray-100 flex items-center justify-center p-4">
      {isMobile ? (
        <MobileFrame>
          <div className="flex flex-col h-full">
            {/* Main Content */}
            <div className="flex-1 overflow-hidden">{renderCurrentScreen()}</div>

            {/* Bottom Navigation - Only show on main screens, not in chat */}
            {currentScreen !== "chat" && <BottomNavigation activeTab={activeTab} onTabChange={handleTabChange} />}
          </div>
        </MobileFrame>
      ) : (
        // Desktop view: Render content directly, allowing it to expand
        <div className="flex flex-col h-full w-full max-w-screen-lg mx-auto bg-[#F8F6FF] rounded-2xl shadow-lg overflow-hidden">
          {/* Main Content */}
          <div className="flex-1 overflow-hidden">{renderCurrentScreen()}</div>

          {/* Bottom Navigation - Only show on main screens, not in chat */}
          {currentScreen !== "chat" && <BottomNavigation activeTab={activeTab} onTabChange={handleTabChange} />}
        </div>
      )}
    </div>
  )
}
