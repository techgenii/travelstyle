"use client"

import { useRef, useEffect } from "react"
import { ChatBubble } from "./chat-bubble"
import { ChatInput } from "./chat-input"
import { QuickReplyButtons } from "./quick-reply-buttons"
import { ResponseFeedback } from "./response-feedback"

interface Message {
  id: string
  text: string
  isUser: boolean
  timestamp: string
  quickReplies?: Array<{ id: string; text: string; emoji?: string }>
  showFeedback?: boolean
}

interface ChatInterfaceProps {
  messages: Message[]
  onSendMessage: (message: string) => void
  onQuickReply: (buttonId: string, text: string) => void
  onFeedback: (messageId: string, type: "positive" | "negative") => void
  isLoading?: boolean
}

export function ChatInterface({
  messages,
  onSendMessage,
  onQuickReply,
  onFeedback,
  isLoading = false,
}: ChatInterfaceProps) {
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  return (
    <div className="flex flex-col h-full">
      {/* Messages Container */}
      <div className="flex-1 overflow-y-auto px-4 py-4 space-y-1">
        {messages.map((message) => (
          <div key={message.id}>
            <ChatBubble message={message.text} isUser={message.isUser} timestamp={message.timestamp} />

            {!message.isUser && message.quickReplies && (
              <QuickReplyButtons buttons={message.quickReplies} onSelect={onQuickReply} disabled={isLoading} />
            )}

            {!message.isUser && message.showFeedback && (
              <ResponseFeedback messageId={message.id} onFeedback={onFeedback} />
            )}
          </div>
        ))}

        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-[#F0EFFF] rounded-[20px] rounded-bl-[8px] px-4 py-3 max-w-[75%]">
              <div className="flex space-x-1">
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                <div
                  className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"
                  style={{ animationDelay: "0.1s" }}
                ></div>
                <div
                  className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"
                  style={{ animationDelay: "0.2s" }}
                ></div>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input Container */}
      <ChatInput
        onSendMessage={onSendMessage}
        disabled={isLoading}
        placeholder="Ask me about travel, style, or currency..."
      />
    </div>
  )
}
