"use client"

import { useEffect, useState } from "react"
import { cn } from "@/lib/utils"

interface GreetingProps {
  userName: string
  greetingMessage: string // Changed to a single message prop
}

export function Greeting({ userName, greetingMessage }: GreetingProps) {
  const [animate, setAnimate] = useState(false)

  useEffect(() => {
    setAnimate(true) // Trigger animation on mount
  }, [])

  return (
    <div className="p-4 text-center">
      <h2 className={cn("text-3xl font-bold text-gray-900 mb-2", animate && "animate-fade-in-slide-up")}>
        {greetingMessage} {userName}! ✈️
      </h2>
      <p className="text-gray-600 text-md">
        I'm your AI travel stylist. I can help you pack smart, dress appropriately, and handle currency conversions for
        your next adventure.
      </p>
    </div>
  )
}
