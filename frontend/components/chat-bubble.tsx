import { cn } from "@/lib/utils"
import { colors } from "@/lib/design-system"

interface ChatBubbleProps {
  message: string
  isUser: boolean
  timestamp: string
}

export function ChatBubble({ message, isUser, timestamp }: ChatBubbleProps) {
  return (
    <div className={cn("flex w-full", isUser ? "justify-end" : "justify-start")}>
      <div
        className={cn(
          "max-w-[70%] p-3 rounded-lg shadow-md",
          isUser
            ? cn(colors.gradients.chatBubbleUser, "rounded-br-none")
            : cn(colors.gradients.chatBubbleAI, "rounded-bl-none"),
        )}
      >
        <p className={cn("text-sm", isUser ? "text-white" : "text-gray-800")}>{message}</p>
        <span className={cn("block text-right text-xs mt-1", isUser ? "text-white/80" : "text-gray-600")}>
          {timestamp}
        </span>
      </div>
    </div>
  )
}
