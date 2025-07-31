"use client"

import { useEffect, useRef } from "react"
import { Header } from "./header"
import { ChatBubble } from "./chat-bubble"
import { ChatInput } from "./chat-input"
import { QuickReplyButtons } from "./quick-reply-buttons"
import { ResponseFeedback } from "./response-feedback"
import { Loader2 } from "lucide-react"

interface Message {
  id: string
  text: string
  isUser: boolean
  timestamp: string
  quickReplies?: Array<{ id: string; text: string; emoji?: string }>
  showFeedback?: boolean
}

interface ChatInterfaceProps {
  title: string
  onBack: () => void
  messages: Message[]
  onSendMessage: (message: string) => void
  onQuickReply: (buttonId: string, text: string) => void
  onFeedback: (messageId: string, type: "positive" | "negative") => void
  isLoading: boolean
}

export function ChatInterface({
  title,
  onBack,
  messages,
  onSendMessage,
  onQuickReply,
  onFeedback,
  isLoading,
}: ChatInterfaceProps) {
  const messagesEndRef = useRef<HTMLDivElement>(null)



  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const lastAIMessage = messages
    .slice()
    .reverse()
    .find((m) => !m.isUser)

  return (
    <div className="flex flex-col h-full bg-[#F8F6FF]">
      <Header title={title} showBack onBack={onBack} />

      <div className="flex-1 overflow-y-auto p-4 space-y-4 custom-scrollbar">
        {messages.map((msg, index) => (
          <div key={msg.id || `message-${index}-${Date.now()}`}>
            <ChatBubble message={msg.text} isUser={msg.isUser} timestamp={msg.timestamp} />
            {msg.showFeedback && !msg.isUser && <ResponseFeedback messageId={msg.id} onFeedback={onFeedback} />}
          </div>
        ))}
        {isLoading && (
          <div className="flex justify-start">
            <div className="max-w-[70%] p-3 rounded-lg rounded-bl-none shadow-md bg-gray-200 text-gray-700 flex items-center space-x-2">
              <Loader2 className="h-5 w-5 animate-spin" />
              <span>AI is typing...</span>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {lastAIMessage?.quickReplies && lastAIMessage.quickReplies.length > 0 && (
        <QuickReplyButtons buttons={lastAIMessage.quickReplies} onQuickReply={onQuickReply} />
      )}

      <ChatInput onSendMessage={onSendMessage} isLoading={isLoading} />
    </div>
  )
}
