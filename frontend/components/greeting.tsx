"use client"

import { useEffect, useState } from "react"
import { cn } from "@/lib/utils"

interface GreetingProps {
  userName: string
  greetings?: string[] // Optional prop for custom greetings
}

export function Greeting({ userName, greetings }: GreetingProps) {
  const defaultGreetings = [
    "Hello",
    "Welcome back",
    "Ready for your next adventure",
    "Let's explore the world together",
    "Your travel companion is here",
    "Time to discover something amazing",
    "Adventure awaits",
    "Let's plan your perfect trip",
    "Ready to explore",
    "Your journey starts here",
    "Let's make travel magic happen",
    "Welcome to your travel hub",
    "Ready for wanderlust",
    "Let's create unforgettable memories",
    "Your next adventure begins now",
  ]

  const effectiveGreetings = greetings && greetings.length > 0 ? greetings : defaultGreetings

  const [currentGreeting, setCurrentGreeting] = useState("")
  const [animate, setAnimate] = useState(false)

  useEffect(() => {
    const randomIndex = Math.floor(Math.random() * effectiveGreetings.length)
    setCurrentGreeting(effectiveGreetings[randomIndex])
    setAnimate(true) // Trigger animation on mount
  }, []) // Remove the greetings dependency to prevent infinite loop

  return (
    <div className="p-4 text-center">
      <h2
        className={cn(
          "text-3xl font-bold text-gray-900 mb-2",
          animate && "animate-fade-in-slide-up", // Apply animation class
        )}
      >
        {currentGreeting} {userName}! ✈️
      </h2>
      <p className="text-gray-600 text-md">
        I'm your AI travel stylist. I can help you pack smart, dress appropriately, and handle currency conversions for
        your next adventure.
      </p>
    </div>
  )
}
