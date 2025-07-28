"use client"

import type React from "react"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Send } from "lucide-react"

interface ChatInputProps {
  onSendMessage: (message: string) => void
  disabled?: boolean
  placeholder?: string
}

export function ChatInput({ onSendMessage, disabled = false, placeholder = "Type your message..." }: ChatInputProps) {
  const [message, setMessage] = useState("")

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (message.trim() && !disabled) {
      onSendMessage(message.trim())
      setMessage("")
    }
  }

  return (
    <div className="sticky bottom-0 bg-white border-t border-gray-100 p-4">
      <form onSubmit={handleSubmit} className="flex gap-2">
        <Input
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          placeholder={placeholder}
          disabled={disabled}
          className="flex-1 bg-white border-gray-200 rounded-xl px-4 py-3 text-base focus:border-gray-300 focus:ring-0"
        />
        <Button
          type="submit"
          disabled={disabled || !message.trim()}
          className="bg-black text-white rounded-xl px-4 py-3 hover:bg-gray-800 disabled:bg-gray-300"
        >
          <Send className="h-4 w-4" />
        </Button>
      </form>
    </div>
  )
}
