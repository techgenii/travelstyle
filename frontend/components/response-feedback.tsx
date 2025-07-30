"use client"

import { useState } from "react"
import { ThumbsUp, ThumbsDown } from "lucide-react"
import { cn } from "@/lib/utils"

interface ResponseFeedbackProps {
  messageId: string
  onFeedback: (messageId: string, type: "positive" | "negative") => void
}

export function ResponseFeedback({ messageId, onFeedback }: ResponseFeedbackProps) {
  const [feedbackGiven, setFeedbackGiven] = useState<"positive" | "negative" | null>(null)

  const handleFeedbackClick = (type: "positive" | "negative") => {
    if (!feedbackGiven) {
      setFeedbackGiven(type)
      onFeedback(messageId, type)
    }
  }

  return (
    <div className="flex items-center justify-end space-x-2 mt-2">
      <button
        className={cn(
          "p-1 rounded-full transition-colors",
          feedbackGiven === "positive" ? "bg-green-100 text-green-600" : "text-gray-400 hover:bg-gray-100",
        )}
        onClick={() => handleFeedbackClick("positive")}
        disabled={!!feedbackGiven}
        aria-label="Give positive feedback"
      >
        <ThumbsUp className="h-4 w-4" />
      </button>
      <button
        className={cn(
          "p-1 rounded-full transition-colors",
          feedbackGiven === "negative" ? "bg-red-100 text-red-600" : "text-gray-400 hover:bg-gray-100",
        )}
        onClick={() => handleFeedbackClick("negative")}
        disabled={!!feedbackGiven}
        aria-label="Give negative feedback"
      >
        <ThumbsDown className="h-4 w-4" />
      </button>
    </div>
  )
}
