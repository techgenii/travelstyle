"use client"

import { useState } from "react"
import { Header } from "./header"
import { ChatListItem } from "./chat-list-item"
import { Input } from "@/components/ui/input"
import { Search } from "lucide-react"
import { Button } from "@/components/ui/button"
import { MessageCircle } from "lucide-react"

interface ChatHistory {
  id: string
  title: string
  lastMessage: string
  timestamp: string
  type: "wardrobe" | "style" | "currency" | "general"
  messageCount: number
  createdAt: Date
}

interface RecentChatsScreenProps {
  onBack: () => void
  onChatSelect: (chatId: string) => void
}

// Mock data for recent chats
const mockChatHistory: ChatHistory[] = [
  {
    id: "1",
    title: "Paris Business Trip",
    lastMessage: "Perfect! Here's your 5-day business wardrobe for Paris in November...",
    timestamp: "2 hours ago",
    type: "wardrobe",
    messageCount: 12,
    createdAt: new Date(Date.now() - 2 * 60 * 60 * 1000),
  },
  {
    id: "2",
    title: "Tokyo Style Etiquette",
    lastMessage: "In Tokyo, business attire tends to be more conservative. Here are the key guidelines...",
    timestamp: "Yesterday",
    type: "style",
    messageCount: 8,
    createdAt: new Date(Date.now() - 24 * 60 * 60 * 1000),
  },
  {
    id: "3",
    title: "USD to EUR Conversion",
    lastMessage: "$500 USD equals approximately €462.50 EUR at today's rate...",
    timestamp: "2 days ago",
    type: "currency",
    messageCount: 4,
    createdAt: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000),
  },
  {
    id: "4",
    title: "London Weekend Getaway",
    lastMessage: "For a London weekend in autumn, I recommend the 3x3x3 capsule method...",
    timestamp: "3 days ago",
    type: "wardrobe",
    messageCount: 15,
    createdAt: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000),
  },
  {
    id: "5",
    title: "Italian Dining Etiquette",
    lastMessage: "When dining in Italy, especially at upscale restaurants, here's what to wear...",
    timestamp: "5 days ago",
    type: "style",
    messageCount: 6,
    createdAt: new Date(Date.now() - 5 * 24 * 60 * 60 * 1000),
  },
  {
    id: "6",
    title: "General Travel Questions",
    lastMessage: "I'd be happy to help you with any travel-related questions! What's on your mind?",
    timestamp: "1 week ago",
    type: "general",
    messageCount: 3,
    createdAt: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000),
  },
  {
    id: "7",
    title: "New York Fashion Week",
    lastMessage: "For Fashion Week events, you'll want to balance trendy with professional...",
    timestamp: "1 week ago",
    type: "wardrobe",
    messageCount: 20,
    createdAt: new Date(Date.now() - 8 * 24 * 60 * 60 * 1000),
  },
  {
    id: "8",
    title: "GBP Currency Check",
    lastMessage: "£200 GBP converts to approximately $248.60 USD...",
    timestamp: "2 weeks ago",
    type: "currency",
    messageCount: 2,
    createdAt: new Date(Date.now() - 14 * 24 * 60 * 60 * 1000),
  },
]

export function RecentChatsScreen({ onBack, onChatSelect }: RecentChatsScreenProps) {
  const [searchQuery, setSearchQuery] = useState("")
  const [filterType, setFilterType] = useState<"all" | "wardrobe" | "style" | "currency" | "general">("all")

  // Filter chats from last 30 days
  const thirtyDaysAgo = new Date(Date.now() - 30 * 24 * 60 * 60 * 1000)
  const recentChats = mockChatHistory.filter((chat) => chat.createdAt >= thirtyDaysAgo)

  // Apply search and filter
  const filteredChats = recentChats.filter((chat) => {
    const matchesSearch =
      chat.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      chat.lastMessage.toLowerCase().includes(searchQuery.toLowerCase())
    const matchesFilter = filterType === "all" || chat.type === filterType
    return matchesSearch && matchesFilter
  })

  // Group chats by date
  const groupedChats = filteredChats.reduce(
    (groups, chat) => {
      const today = new Date()
      const yesterday = new Date(today.getTime() - 24 * 60 * 60 * 1000)
      const chatDate = chat.createdAt

      let groupKey = ""
      if (chatDate.toDateString() === today.toDateString()) {
        groupKey = "Today"
      } else if (chatDate.toDateString() === yesterday.toDateString()) {
        groupKey = "Yesterday"
      } else if (chatDate >= new Date(today.getTime() - 7 * 24 * 60 * 60 * 1000)) {
        groupKey = "This Week"
      } else {
        groupKey = "Earlier"
      }

      if (!groups[groupKey]) {
        groups[groupKey] = []
      }
      groups[groupKey].push(chat)
      return groups
    },
    {} as Record<string, ChatHistory[]>,
  )

  const filterButtons = [
    { key: "all", label: "All", emoji: "📱" },
    { key: "wardrobe", label: "Wardrobe", emoji: "👗" },
    { key: "style", label: "Style", emoji: "🌍" },
    { key: "currency", label: "Currency", emoji: "💱" },
    { key: "general", label: "General", emoji: "💬" },
  ]

  return (
    <div className="flex flex-col h-full bg-[#F8F6FF]">
      <Header title="Recent Chats" showBack onBack={onBack} />

      {/* Search and Filter Section */}
      <div className="px-4 py-3 bg-gray-50 border-b border-gray-100">
        {/* Search Bar */}
        <div className="relative mb-3">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
          <Input
            placeholder="Search conversations..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-10 bg-white border-gray-200 rounded-xl"
          />
        </div>

        {/* Filter Buttons */}
        <div className="flex gap-2 overflow-x-auto pb-1">
          {filterButtons.map((filter) => (
            <Button
              key={filter.key}
              variant={filterType === filter.key ? "default" : "outline"}
              size="sm"
              onClick={() => setFilterType(filter.key as typeof filterType)}
              className={`flex-shrink-0 rounded-full px-3 py-1 text-xs font-medium ${
                filterType === filter.key
                  ? "bg-black text-white"
                  : "bg-white text-gray-600 border-gray-200 hover:bg-gray-50"
              }`}
            >
              <span className="mr-1">{filter.emoji}</span>
              {filter.label}
            </Button>
          ))}
        </div>
      </div>

      {/* Chat List */}
      <div className="flex-1 overflow-y-auto p-4">
        {filteredChats.length > 0 ? (
          <div className="bg-white rounded-2xl shadow-soft overflow-hidden">
            {Object.entries(groupedChats).map(([groupName, chats]) => (
              <div key={groupName}>
                <div className="px-4 py-2 bg-gray-50 border-b border-gray-100">
                  <h2 className="text-sm font-medium text-gray-700">{groupName}</h2>
                </div>
                {chats.map((chat, index) => (
                  <ChatListItem
                    key={chat.id}
                    chat={chat}
                    onClick={() => onChatSelect(chat.id)}
                    isLast={index === chats.length - 1}
                  />
                ))}
              </div>
            ))}
          </div>
        ) : (
          <div className="flex flex-col items-center justify-center h-full text-center text-gray-500">
            <MessageCircle size={48} className="mb-4" />
            <p className="text-lg font-semibold">No recent chats</p>
            <p className="text-sm">Start a new conversation to see it here!</p>
          </div>
        )}
      </div>
    </div>
  )
}
