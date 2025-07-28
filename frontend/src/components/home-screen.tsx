"use client"

import { Header } from "./header"
import { Greeting } from "./greeting"
import { ActionCards } from "./action-cards"

interface HomeScreenProps {
  onActionSelect: (actionId: string) => void
  userName?: string
}

export function HomeScreen({ onActionSelect, userName = "there" }: HomeScreenProps) {
  const actionCards = [
    {
      id: "wardrobe",
      title: "Plan My Wardrobe",
      description: "Get personalized packing recommendations for your destination",
      emoji: "👗",
    },
    {
      id: "style",
      title: "Style Etiquette",
      description: "Learn local dress codes and cultural style guidelines",
      emoji: "🌍",
    },
    {
      id: "currency",
      title: "Currency Converter",
      description: "Convert currencies with up-to-date exchange rates",
      emoji: "💱",
    },
    {
      id: "chat",
      title: "Ask Anything",
      description: "Start a conversation about travel, style, or planning",
      emoji: "💬",
    },
  ]

  const proTips = [
    "Always check the weather and local customs before packing. I can help you with both!",
    "Pack versatile pieces that can be mixed and matched to create multiple outfits.",
    "Consider the climate and activities when choosing fabrics for your travel wardrobe.",
    "Don't forget essential accessories like a universal adapter and a portable charger.",
    "Research local style etiquette to ensure you dress appropriately for any occasion.",
  ]

  // List of greeting messages
  const greetings = [
    `Hello ${userName}! ✈️`,
    `Welcome back, ${userName}! ✈️`,
    `Good to see you, ${userName}! ✈️`,
    `Ready for your next adventure, ${userName}? ✈️`,
    `Where to next, ${userName}? ✈️`,
    `Greetings, traveler ${userName}! ✈️`,
    `Let's plan your style, ${userName}! ✈️`,
    `Looking stylish, ${userName}! ✈️`,
    `Travel in style, ${userName}! ✈️`,
    `Fashion meets travel, ${userName}! ✈️`,
    `Jet-setting today, ${userName}? ✈️`,
    `Your travel stylist awaits, ${userName}! ✈️`,
    `Pack smart with me, ${userName}! ✈️`,
    `Adventure awaits, ${userName}! ✈️`,
    `Your journey begins here, ${userName}! ✈️`,
  ]

  // Select a random tip once when the component mounts
  const randomTipIndex = Math.floor(Math.random() * proTips.length)
  const currentTip = proTips[randomTipIndex]

  // Select a random greeting once when the component mounts
  const randomGreetingIndex = Math.floor(Math.random() * greetings.length)
  const currentGreeting = greetings[randomGreetingIndex]

  return (
    <div className="flex flex-col h-full bg-[#F8F6FF]">
      <Header title="TravelStyle AI" />

      <div className="flex-1 overflow-y-auto">
        <Greeting
          mainText={currentGreeting}
          subText="I'm your AI travel stylist. I can help you pack smart, dress appropriately, and handle currency conversions for your next adventure."
        />

        <ActionCards cards={actionCards} onCardSelect={onActionSelect} />

        {/* Quick Tips Section */}
        <div className="px-4 mb-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-3">Quick Tips</h2>
          <div className="bg-white rounded-2xl p-4 shadow-soft border border-gray-100 min-h-[80px] flex items-center">
            <p className="text-sm text-gray-600 leading-relaxed">
              💡 <strong>Pro tip:</strong> {currentTip}
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
