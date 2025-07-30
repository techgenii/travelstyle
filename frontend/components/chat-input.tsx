"use client"

import type React from "react"

import { useState } from "react"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { Send, Mic } from "lucide-react"
import { cn } from "@/lib/utils"

interface ChatInputProps {
  onSendMessage: (message: string) => void
  isLoading: boolean
}

export function ChatInput({ onSendMessage, isLoading }: ChatInputProps) {
  const [message, setMessage] = useState("")

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (message.trim() && !isLoading) {
      onSendMessage(message.trim())
      setMessage("")
    }
  }

  return (
    <form onSubmit={handleSubmit} className="flex items-center p-4 bg-white border-t border-gray-100 shadow-md">
      <Input
        type="text"
        placeholder={isLoading ? "AI is typing..." : "Type your message..."}
        value={message}
        onChange={(e) => setMessage(e.target.value)}
        className={cn(
          "flex-1 mr-3 rounded-full px-4 py-2 border border-gray-200 focus:ring-2 focus:ring-purple-300 focus:border-purple-400",
          isLoading && "bg-gray-100 cursor-not-allowed",
        )}
        disabled={isLoading}
      />
      <Button
        type="submit"
        size="icon"
        className={cn(
          "rounded-full w-10 h-10 bg-purple-600 hover:bg-purple-700 transition-colors",
          isLoading && "opacity-60 cursor-not-allowed",
        )}
        disabled={isLoading}
      >
        <Send className="h-5 w-5 text-white" />
      </Button>
      <Button
        type="button"
        size="icon"
        variant="ghost"
        className="ml-2 rounded-full w-10 h-10 text-gray-600 hover:bg-gray-100"
        onClick={() => console.log("Voice input")}
        disabled={isLoading}
      >
        <Mic className="h-5 w-5" />
      </Button>
    </form>
  )
}
