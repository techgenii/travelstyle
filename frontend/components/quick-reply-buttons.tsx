"use client"

import { Button } from "@/components/ui/button"

interface QuickReplyButton {
  id: string
  text: string
  emoji?: string
}

interface QuickReplyButtonsProps {
  buttons: QuickReplyButton[]
  onSelect: (buttonId: string, text: string) => void
  disabled?: boolean
}

export function QuickReplyButtons({ buttons, onSelect, disabled = false }: QuickReplyButtonsProps) {
  if (buttons.length === 0) return null

  return (
    <div className="flex flex-wrap gap-2 mt-3 mb-4">
      {buttons.map((button) => (
        <Button
          key={button.id}
          variant="outline"
          size="sm"
          onClick={() => onSelect(button.id, button.text)}
          disabled={disabled}
          className="bg-white border-gray-200 text-gray-700 hover:bg-gray-50 rounded-full px-4 py-2 text-sm font-medium"
        >
          {button.emoji && <span className="mr-1">{button.emoji}</span>}
          {button.text}
        </Button>
      ))}
    </div>
  )
}
