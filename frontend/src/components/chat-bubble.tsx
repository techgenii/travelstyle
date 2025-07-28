import { cn } from "@/lib/utils"

interface ChatBubbleProps {
  message: string
  isUser: boolean
  timestamp?: string
}

export function ChatBubble({ message, isUser, timestamp }: ChatBubbleProps) {
  return (
    <div className={cn("flex mb-2", isUser ? "justify-end" : "justify-start")}>
      <div
        className={cn(
          "max-w-[75%] px-4 py-3 rounded-[20px] text-base leading-relaxed",
          isUser
            ? "bg-[#E8E5FF] text-gray-900 rounded-br-[8px] ml-auto"
            : "bg-[#F0EFFF] text-gray-900 rounded-bl-[8px] mr-auto",
        )}
      >
        <p className="whitespace-pre-wrap">{message}</p>
        {timestamp && <p className="text-xs text-gray-500 mt-1">{timestamp}</p>}
      </div>
    </div>
  )
}
