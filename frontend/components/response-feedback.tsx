"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { ThumbsUp, ThumbsDown } from "lucide-react"

interface ResponseFeedbackProps {
  messageId: string
  onFeedback: (messageId: string, type: "positive" | "negative") => void
}

export function ResponseFeedback({ messageId, onFeedback }: ResponseFeedbackProps) {
  const [feedback, setFeedback] = useState<"positive" | "negative" | null>(null)

  const handleFeedback = (type: "positive" | "negative") => {
    setFeedback(type)
    onFeedback(messageId, type)
  }

  return (
    <div className="flex gap-2 mt-2 mb-4">
      <Button
        variant="ghost"
        size="sm"
        onClick={() => handleFeedback("positive")}
        disabled={feedback !== null}
        className={`h-8 w-8 p-0 rounded-full ${
          feedback === "positive" ? "bg-green-100 text-green-600" : "hover:bg-gray-100"
        }`}
      >
        <ThumbsUp className="h-4 w-4" />
      </Button>
      <Button
        variant="ghost"
        size="sm"
        onClick={() => handleFeedback("negative")}
        disabled={feedback !== null}
        className={`h-8 w-8 p-0 rounded-full ${
          feedback === "negative" ? "bg-red-100 text-red-600" : "hover:bg-gray-100"
        }`}
      >
        <ThumbsDown className="h-4 w-4" />
      </Button>
      {feedback && <span className="text-xs text-gray-500 self-center ml-2">Thank you for your feedback!</span>}
    </div>
  )
}
