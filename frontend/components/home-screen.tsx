"use client"

import { useEffect, useState } from "react"
import { Header } from "./header"
import { Greeting } from "./greeting"
import { ActionCards } from "./action-cards"
import { Card, CardContent } from "@/components/ui/card"
import { Lightbulb } from "lucide-react"
import { cn } from "@/lib/utils"

// Move these arrays outside the component to prevent recreation on every render
const proTips = [
  "Pack versatile clothing items that can be mixed and matched for different occasions.",
  "Always carry a portable charger for your devices, especially when traveling.",
  "Research local customs and etiquette to ensure a respectful travel experience.",
  "Use packing cubes to organize your luggage and maximize space.",
  "Keep digital copies of important documents (passport, tickets) on your phone and cloud storage.",
  "Learn a few basic phrases in the local language – it goes a long way!",
  "Invest in comfortable walking shoes; you'll be doing a lot of exploring!",
  "Check the weather forecast for your destination regularly before and during your trip.",
  "Inform your bank of your travel plans to avoid issues with your cards abroad.",
  "Consider travel insurance for unexpected situations.",
  "Try local street food, but choose vendors with long lines and good hygiene.",
  "Always have some local currency cash for small purchases or emergencies.",
  "Pack a small first-aid kit with essentials like pain relievers and band-aids.",
  "Take advantage of free walking tours to get acquainted with a new city.",
  "Leave some space in your luggage for souvenirs and new purchases!",
]

const greetings = [
  "Hello",
  "Hi there",
  "Greetings",
  "Welcome",
  "Hey",
  "Nice to see you",
  "Howdy",
  "Aloha",
  "Bonjour",
  "Hola",
  "Ciao",
  "G'day",
  "Salutations",
  "What's up",
  "Good to have you",
]

interface HomeScreenProps {
  onActionSelect: (actionId: string) => void
  userName: string
  onProfileClick?: () => void
  onSettingsClick?: () => void
}

export function HomeScreen({ onActionSelect, userName, onProfileClick, onSettingsClick }: HomeScreenProps) {
  const [currentProTip, setCurrentProTip] = useState("")

  useEffect(() => {
    // Select a random pro tip when the component mounts
    const randomIndex = Math.floor(Math.random() * proTips.length)
    setCurrentProTip(proTips[randomIndex])
  }, []) // Empty dependency array means this runs once on mount

  const [currentGreeting, setCurrentGreeting] = useState("")
  const [animateGreeting, setAnimateGreeting] = useState(false)

  useEffect(() => {
    // Select a random greeting when the component mounts
    const randomIndex = Math.floor(Math.random() * greetings.length)
    setCurrentGreeting(greetings[randomIndex])
    setAnimateGreeting(true) // Trigger animation on mount
  }, [greetings])

  return (
    <div className="flex flex-col h-full bg-[#F8F6FF]">
      <Header
        title="TravelStyle AI"
        showProfile
        showSettings
        onProfileClick={onProfileClick}
        onSettingsClick={onSettingsClick}
      />
      <div className="flex-1 overflow-y-auto">
        <Greeting userName={userName} greetings={greetings} />

        {/* Pro Tip Card */}
        <Card className="m-4 pro-tip-gradient text-white shadow-lg rounded-xl">
          <CardContent className="p-4 flex items-start">
            <Lightbulb size={24} className="mr-3 mt-1 flex-shrink-0" />
            <div>
              <h3 className="text-lg font-semibold mb-1">Pro Tip:</h3>
              <p key={currentProTip} className={cn("text-sm opacity-90")}>
                {currentProTip}
              </p>
            </div>
          </CardContent>
        </Card>

        <ActionCards onActionSelect={onActionSelect} />
      </div>
    </div>
  )
}
