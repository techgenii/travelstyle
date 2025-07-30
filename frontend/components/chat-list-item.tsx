"use client"

import { MessageSquare, Tag } from "lucide-react"
import { cn } from "@/lib/utils"

interface ChatHistory {
  id: string
  title: string
  lastMessage: string
  timestamp: string
  type: "wardrobe" | "style" | "currency" | "general"
  messageCount: number
  createdAt: Date // Assuming this is available for sorting/grouping
}

interface ChatListItemProps {
  chat: ChatHistory
  onClick: (chatId: string) => void
  isLast: boolean // To control bottom border
}

export function ChatListItem({ chat, onClick, isLast }: ChatListItemProps) {
  const getTypeIcon = (type: ChatHistory["type"]) => {
    switch (type) {
      case "wardrobe":
        return "👗"
      case "style":
        return "🌍"
      case "currency":
        return "💱"
      case "general":
      default:
        return "💬"
    }
  }

  const getTypeColorClass = (type: ChatHistory["type"]) => {
    switch (type) {
      case "wardrobe":
        return "bg-pink-100 text-pink-700"
      case "style":
        return "bg-blue-100 text-blue-700"
      case "currency":
        return "bg-green-100 text-green-700"
      case "general":
      default:
        return "bg-gray-100 text-gray-700"
    }
  }

  return (
    <button
      onClick={() => onClick(chat.id)}
      className={cn(
        "flex items-center p-4 w-full text-left bg-white hover:bg-gray-50 transition-colors",
        !isLast && "border-b border-gray-100",
      )}
    >
      <div className="flex-shrink-0 w-10 h-10 rounded-full bg-gray-100 flex items-center justify-center mr-3">
        <span className="text-xl">{getTypeIcon(chat.type)}</span>
      </div>
      <div className="flex-1 min-w-0">
        <div className="flex items-center justify-between mb-1">
          <h3 className="font-semibold text-gray-900 truncate">{chat.title}</h3>
          <span className="text-xs text-gray-500 flex-shrink-0 ml-2">{chat.timestamp}</span>
        </div>
        <p className="text-sm text-gray-600 truncate mb-1">{chat.lastMessage}</p>
        <div className="flex items-center text-xs text-gray-500">
          <MessageSquare className="h-3 w-3 mr-1" />
          <span>{chat.messageCount} messages</span>
          <Tag className={cn("h-3 w-3 ml-3 mr-1", getTypeColorClass(chat.type))} />
          <span className={cn("font-medium", getTypeColorClass(chat.type))}>{chat.type}</span>
        </div>
      </div>
    </button>
  )
}
