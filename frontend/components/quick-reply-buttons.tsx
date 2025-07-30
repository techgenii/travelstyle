"use client"

import { Button } from "@/components/ui/button"
import { cn } from "@/lib/utils"

interface QuickReplyButton {
  id: string
  text: string
  emoji?: string
}

interface QuickReplyButtonsProps {
  buttons: QuickReplyButton[]
  onQuickReply: (id: string, text: string) => void
}

export function QuickReplyButtons({ buttons, onQuickReply }: QuickReplyButtonsProps) {
  return (
    <div className="flex flex-wrap gap-2 p-4 justify-center">
      {buttons.map((button) => (
        <Button
          key={button.id}
          variant="outline"
          size="sm"
          className={cn(
            "rounded-full px-4 py-2 text-sm font-medium",
            "bg-white text-gray-700 border-gray-200 hover:bg-gray-100",
            "shadow-sm transition-all duration-200 ease-in-out",
          )}
          onClick={() => onQuickReply(button.id, button.text)}
        >
          {button.emoji && <span className="mr-1">{button.emoji}</span>}
          {button.text}
        </Button>
      ))}
    </div>
  )
}
