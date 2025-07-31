"use client"

import { useState, useEffect, useRef } from "react"
import { MobileFrame } from "@/components/mobile-frame"
import { HomeScreen } from "@/components/home-screen"
import { ChatInterface } from "@/components/chat-interface"
import { RecentChatsScreen } from "@/components/recent-chats-screen"
import { ProfileScreen } from "@/components/profile-screen"
import { SettingsScreenCloudinary } from "@/components/settings-screen-cloudinary"
import { BottomNavigation } from "@/components/bottom-navigation"
import { sendChatMessage, getChatHistory, createChatSession } from "@/lib/services/chat"
import type { ConversationContext as BackendConversationContext } from "@/lib/services/chat"
import { checkAuthStatus, redirectToLogin, type UserData } from "@/lib/auth"
import { useIsMobile } from "@/hooks/use-is-mobile"

type AppScreen = "home" | "chat" | "recent" | "profile" | "settings"
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

// Define the default greetings here, as this is where the greeting will be selected once per session.
const defaultGreetings = [
  "Hello",
  "Welcome back",
  "Ready for your next adventure",
  "Let's explore the world together",
  "Your travel companion is here",
  "Time to discover something amazing",
  "Adventure awaits",
  "Let's plan your perfect trip",
  "Ready to explore",
  "Your journey starts here",
  "Let's make travel magic happen",
  "Welcome to your travel hub",
  "Ready for wanderlust",
  "Let's create unforgettable memories",
  "Your next adventure begins now",
]

export default function TravelStyleApp() {
  const [currentScreen, setCurrentScreen] = useState<AppScreen>("home")
  const [activeTab, setActiveTab] = useState<NavigationTab>("home")
  const [chatContext, setChatContext] = useState<ChatContext>("general")
  const [messages, setMessages] = useState<Message[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [isAuthChecked, setIsAuthChecked] = useState(false)
  const [mounted, setMounted] = useState(false)
  const [user, setUser] = useState<UserData | null>(null)
  const [currentSessionId, setCurrentSessionId] = useState<string | null>(null)
  const [sessionGreeting, setSessionGreeting] = useState<string | null>(null) // New state for session greeting
  const hasSetSessionGreeting = useRef(false) // Ref to ensure greeting is set only once
  const messageIdCounterRef = useRef(0)

  const generateMessageId = () => {
    messageIdCounterRef.current += 1
    return `${Date.now()}-${messageIdCounterRef.current}`
  }

  const isMobile = useIsMobile()

  useEffect(() => {
    setMounted(true)
    const checkAuth = async () => {
      const { isAuthenticated: authenticated, user: userData } = await checkAuthStatus()
      if (!authenticated) {
        redirectToLogin()
      } else {
        setUser(userData)
        setIsAuthChecked(true)

        // Set the session greeting only once after successful authentication
        if (userData && !hasSetSessionGreeting.current) {
          const randomIndex = Math.floor(Math.random() * defaultGreetings.length)
          setSessionGreeting(defaultGreetings[randomIndex])
          hasSetSessionGreeting.current = true
        }
      }
    }
    checkAuth()
  }, []) // Empty dependency array means this runs once on mount

  if (!isAuthChecked || !user || !sessionGreeting) {
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
        user_id: user.id,
        session_id: currentSessionId || undefined,
      }

      const response = await sendChatMessage(userMessage, backendContext)

      console.log('Backend response:', response)
      console.log('Response message_id:', response.message_id)
      console.log('Quick replies from backend:', response.quick_replies)

      const processedQuickReplies = response.quick_replies.map((qr) => ({
        id: qr.action || qr.text,
        text: qr.text,
        emoji: "💬",
      }))

      console.log('Processed quick replies:', processedQuickReplies)

      return {
        id: response.message_id || generateMessageId(),
        text: response.message,
        isUser: false,
        timestamp: new Date(response.timestamp).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
        quickReplies: processedQuickReplies,
        showFeedback: true,
      }
    } catch (error: any) {
      console.error("Failed to get AI response from backend:", error)
      if (error.message && error.message.includes("401")) {
        redirectToLogin()
        return {
          id: generateMessageId(),
          text: "Your session has expired. Please log in again.",
          isUser: false,
          timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
          quickReplies: [],
          showFeedback: false,
        }
      }
      return {
        id: generateMessageId(),
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
      setCurrentSessionId(null)
    }
  }

  const handleActionSelect = async (actionId: string) => {
    if (actionId === "recent") {
      setActiveTab("recent")
      setCurrentScreen("recent")
      return
    }

    try {
      let sessionOptions = {}

      switch (actionId) {
        case "currency":
          sessionOptions = {
            destination: "Currency Converter",
            context: "currency"
          }
          break
        case "wardrobe":
          sessionOptions = {
            destination: "Wardrobe Planning",
            context: "wardrobe"
          }
          break
        case "style":
          sessionOptions = {
            destination: "Style Etiquette",
            context: "style"
          }
          break
        default:
          sessionOptions = {}
      }

      const sessionResponse = await createChatSession(sessionOptions)
      setCurrentSessionId(sessionResponse.session_id)
      console.log(`Created new chat session: ${sessionResponse.session_id}`)
    } catch (error) {
      console.error("Failed to create chat session:", error)
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
      case "currency_quick":
        context = "currency"
        initialMessage = "What's the current exchange rate?"
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
      id: generateMessageId(),
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
      id: generateMessageId(),
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
    setCurrentSessionId(null)
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
    setChatContext("general")
    setIsLoading(true)
    try {
      const history = await getChatHistory(user.id)
      setMessages([
        {
          id: generateMessageId(),
          text: `Welcome back to chat ${chatId}!`,
          isUser: false,
          timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
        },
      ])
    } catch (error) {
      console.error("Failed to load chat history:", error)
      setMessages([
        {
          id: generateMessageId(),
          text: "Failed to load chat history. Please try again.",
          isUser: false,
          timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
        },
      ])
    } finally {
      setIsLoading(false)
    }
  }

  const handleSettingsNavClick = () => {
    setCurrentScreen("settings")
    setActiveTab("home")
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
            sessionGreeting={sessionGreeting}
          />
        )
      case "recent":
        return <RecentChatsScreen onBack={() => handleTabChange("home")} onChatSelect={handleChatSelect} />
      case "profile":
        return (
          <ProfileScreen onBack={() => handleTabChange("home")} onSettingsClick={handleSettingsNavClick} user={user} />
        )
      case "settings":
        return (
          <SettingsScreenCloudinary
            onBack={() => setCurrentScreen("home")}
            user={user}
            onUserUpdate={(updatedUser) => setUser(updatedUser)}
          />
        )
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
        return (
          <HomeScreen onActionSelect={handleActionSelect} userName={user.firstName} sessionGreeting={sessionGreeting} />
        )
    }
  }

  const handleProfileNavClick = () => {
    setCurrentScreen("profile")
    setActiveTab("profile")
  }

  // Prevent hydration mismatch by not rendering mobile frame until mounted
  if (!mounted) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center p-4">
        <div className="flex flex-col h-full w-full max-w-screen-lg mx-auto bg-[#F8F6FF] rounded-2xl shadow-lg overflow-hidden h-[800px]">
          <div className="flex-1 overflow-hidden">{renderCurrentScreen()}</div>
          {currentScreen !== "chat" && currentScreen !== "settings" && (
            <BottomNavigation activeTab={activeTab} onTabChange={handleTabChange} />
          )}
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-100 flex items-center justify-center p-4">
      {isMobile ? (
        <MobileFrame>
          <div className="flex flex-col h-full">
            <div className="flex-1 overflow-hidden">{renderCurrentScreen()}</div>
            {currentScreen !== "chat" && currentScreen !== "settings" && (
              <BottomNavigation activeTab={activeTab} onTabChange={handleTabChange} />
            )}
          </div>
        </MobileFrame>
      ) : (
        <div className="flex flex-col h-full w-full max-w-screen-lg mx-auto bg-[#F8F6FF] rounded-2xl shadow-lg overflow-hidden h-[800px]">
          <div className="flex-1 overflow-hidden">{renderCurrentScreen()}</div>
          {currentScreen !== "chat" && currentScreen !== "settings" && (
            <BottomNavigation activeTab={activeTab} onTabChange={handleTabChange} />
          )}
        </div>
      )}
    </div>
  )
}
