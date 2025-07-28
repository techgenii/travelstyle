"use client"

import { MessageCircle, Calendar, ChevronRight } from "lucide-react"

interface ChatListItemProps {
  id: string
  title: string
  lastMessage: string
  timestamp: string
  type: "wardrobe" | "style" | "currency" | "general"
  messageCount: number
  onSelect: (chatId: string) => void
}

const getChatTypeIcon = (type: string) => {
  switch (type) {
    case "wardrobe":
      return "👗"
    case "style":
      return "🌍"
    case "currency":
      return "💱"
    default:
      return "💬"
  }
}

const getChatTypeLabel = (type: string) => {
  switch (type) {
    case "wardrobe":
      return "Wardrobe Planning"
    case "style":
      return "Style Etiquette"
    case "currency":
      return "Currency Converter"
    default:
      return "General Chat"
  }
}

export function ChatListItem({ id, title, lastMessage, timestamp, type, messageCount, onSelect }: ChatListItemProps) {
  return (
    <button
      onClick={() => onSelect(id)}
      className="w-full p-4 bg-white border-b border-gray-100 hover:bg-gray-50 transition-colors duration-200 text-left"
    >
      <div className="flex items-start justify-between">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <span className="text-lg">{getChatTypeIcon(type)}</span>
            <span className="text-xs font-medium text-gray-500 uppercase tracking-wide">{getChatTypeLabel(type)}</span>
          </div>

          <h3 className="text-base font-medium text-gray-900 mb-1 truncate">{title}</h3>

          <p className="text-sm text-gray-600 line-clamp-2 leading-relaxed mb-2">{lastMessage}</p>

          <div className="flex items-center gap-4 text-xs text-gray-500">
            <div className="flex items-center gap-1">
              <Calendar className="h-3 w-3" />
              <span>{timestamp}</span>
            </div>
            <div className="flex items-center gap-1">
              <MessageCircle className="h-3 w-3" />
              <span>{messageCount} messages</span>
            </div>
          </div>
        </div>

        <ChevronRight className="h-5 w-5 text-gray-400 ml-3 flex-shrink-0" />
      </div>
    </button>
  )
}
