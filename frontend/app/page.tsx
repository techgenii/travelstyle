"use client"

import { useState, useEffect } from "react"
import { MobileFrame } from "@/components/mobile-frame"
import { HomeScreen } from "@/components/home-screen"
import { ChatInterface } from "@/components/chat-interface"
import { RecentChatsScreen } from "@/components/recent-chats-screen"
import { ProfileScreen } from "@/components/profile-screen"
import { SettingsScreen } from "@/components/settings-screen"
import { BottomNavigation } from "@/components/bottom-navigation"
import { sendChatMessage, getChatHistory, createChatSession } from "@/lib/services/chat"
import type { ConversationContext as BackendConversationContext } from "@/lib/services/chat"
import { checkAuthStatus, redirectToLogin } from "@/lib/auth" // Import auth utilities
import { useIsMobile } from "@/hooks/use-is-mobile"

type AppScreen = "home" | "chat" | "recent" | "profile" | "settings" // Removed "currency"
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
  const [user, setUser] = useState<{ id: string; firstName: string; email: string } | null>(null)
  const [currentSessionId, setCurrentSessionId] = useState<string | null>(null) // Track current session

  const isMobile = useIsMobile()

  useEffect(() => {
    // Check authentication status on mount
    const checkAuth = async () => {
      const { isAuthenticated: authenticated, user: userData } = await checkAuthStatus()
      if (!authenticated) {
        redirectToLogin()
      } else {
        setUser(userData)
        setIsAuthChecked(true)
      }
    }
    checkAuth()
  }, [])

  if (!isAuthChecked || !user) {
    // Optionally render a loading spinner or null while checking auth
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading application...</p>
        </div>
      </div>
    )
  }

  const generateResponse = async (userMessage: string, context: ChatContext): Promise<Message> => {
    try {
      const backendContext: BackendConversationContext = {
        user_id: user.id, // Use actual user ID from auth
        session_id: currentSessionId || undefined, // Include session ID if available
        // Map frontend context to backend context if needed
        // For example, if context is 'wardrobe', you might add:
        // trip_purpose: context === 'wardrobe' ? 'wardrobe_planning' : undefined,
      }

      const response = await sendChatMessage(userMessage, backendContext)

      return {
        id: response.message_id, // Use message_id from backend
        text: response.message,
        isUser: false,
        timestamp: new Date(response.timestamp).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
        quickReplies: response.quick_replies.map((qr) => ({
          id: qr.action || qr.text,
          text: qr.text,
          emoji: "💬", // Default emoji, can be customized
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
      setCurrentSessionId(null) // Clear session when leaving chat
    }
  }

  const handleActionSelect = async (actionId: string) => {
    if (actionId === "recent") {
      setActiveTab("recent")
      setCurrentScreen("recent")
      return
    }

    // Create a new chat session when starting a conversation (including currency)
    try {
      const sessionResponse = await createChatSession() // This calls /chat/start
      setCurrentSessionId(sessionResponse.session_id)
      console.log(`Created new chat session: ${sessionResponse.session_id}`)
    } catch (error) {
      console.error("Failed to create chat session:", error)
      // Continue without session ID - the backend might handle this gracefully
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
      case "currency": // Currency converter starts a chat session
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
    // Here you would send feedback to your backend
  }

  const handleBackToHome = () => {
    setCurrentScreen("home")
    setActiveTab("home")
    setMessages([])
    setChatContext("general")
    setCurrentSessionId(null) // Clear session when going back to home
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

  const handleChatSelect = async (chatId: string) => {
    console.log(`Loading chat: ${chatId}`)
    setCurrentScreen("chat")
    setActiveTab("home")
    setChatContext("general") // Reset context for loaded chat, or infer from chat history
    setIsLoading(true)
    try {
      // In a real scenario, you'd fetch messages for this specific chatId
      // For now, we'll just simulate loading and clear messages
      const history = await getChatHistory(user.id) // This would ideally fetch history for a specific conversation ID
      // For demonstration, let's just clear and add a placeholder
      setMessages([
        {
          id: "loaded-chat-1",
          text: `Welcome back to chat ${chatId}!`,
          isUser: false,
          timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
        },
      ])
    } catch (error) {
      console.error("Failed to load chat history:", error)
      setMessages([
        {
          id: "error-load",
          text: "Failed to load chat history. Please try again.",
          isUser: false,
          timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
        },
      ])
    } finally {
      setIsLoading(false)
    }
  }

  // Centralized settings navigation handler
  const handleSettingsNavClick = () => {
    setCurrentScreen("settings")
    setActiveTab("home") // Keep home tab active when in settings
  }

  const renderCurrentScreen = () => {
    switch (currentScreen) {
      case "home":
        return (
          <HomeScreen
            onActionSelect={handleActionSelect}
            userName={user.firstName}
            onProfileClick={handleProfileNavClick}
            onSettingsClick={handleSettingsNavClick}
          />
        )
      case "recent":
        return <RecentChatsScreen onBack={() => handleTabChange("home")} onChatSelect={handleChatSelect} />
      case "profile":
        return (
          <ProfileScreen onBack={() => handleTabChange("home")} onSettingsClick={handleSettingsNavClick} user={user} />
        )
      case "settings":
        return <SettingsScreen onBack={() => setCurrentScreen("home")} user={user} />
      case "chat":
        return (
          <ChatInterface
            title={getScreenTitle()}
            onBack={handleBackToHome}
            messages={messages}
            onSendMessage={handleSendMessage}
            onQuickReply={handleQuickReply}
            onFeedback={handleFeedback}
            isLoading={isLoading}
          />
        )
      default:
        return <HomeScreen onActionSelect={handleActionSelect} userName={user.firstName} />
    }
  }

  const handleProfileNavClick = () => {
    setCurrentScreen("profile")
    setActiveTab("profile")
  }

  // Pass handleProfileNavClick to HomeScreen
  return (
    <div className="min-h-screen bg-gray-100 flex items-center justify-center p-4">
      {isMobile ? (
        <MobileFrame>
          <div className="flex flex-col h-full">
            {/* Main Content */}
            <div className="flex-1 overflow-hidden">{renderCurrentScreen()}</div>

            {/* Bottom Navigation - Only show on main screens, not in chat */}
            {currentScreen !== "chat" && currentScreen !== "settings" && (
              <BottomNavigation activeTab={activeTab} onTabChange={handleTabChange} />
            )}
          </div>
        </MobileFrame>
      ) : (
        // Desktop view: Render content directly, allowing it to expand
        <div className="flex flex-col h-full w-full max-w-screen-lg mx-auto bg-[#F8F6FF] rounded-2xl shadow-lg overflow-hidden h-[800px]">
          {/* Main Content */}
          <div className="flex-1 overflow-hidden">{renderCurrentScreen()}</div>

          {/* Bottom Navigation - Only show on main screens, not in chat */}
          {currentScreen !== "chat" && currentScreen !== "settings" && (
            <BottomNavigation activeTab={activeTab} onTabChange={handleTabChange} />
          )}
        </div>
      )}
    </div>
  )
}
