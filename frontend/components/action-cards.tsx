"use client"

import { Card, CardContent } from "@/components/ui/card"
import { cn } from "@/lib/utils"
import { colors } from "@/lib/design-system"

interface ActionCardProps {
  id: string
  title: string
  description: string
  emoji: string
}

interface ActionCardsProps {
  cards?: ActionCardProps[]
  onActionSelect: (id: string) => void // Changed from onCardSelect to onActionSelect
}

export function ActionCards({ onActionSelect }: ActionCardsProps) {
  // Updated parameter name
  const cards = [
    {
      id: "wardrobe",
      title: "Plan My Wardrobe",
      description: "Get personalized packing recommendations for your destination",
      emoji: "👗",
      gradient: colors.gradients.actionCard1,
    },
    {
      id: "style",
      title: "Style Etiquette",
      description: "Learn local dress codes and cultural style guidelines",
      emoji: "🌍",
      gradient: colors.gradients.actionCard2,
    },
    {
      id: "currency",
      title: "Currency Converter",
      description: "Convert currencies with up-to-date exchange rates",
      emoji: "💱",
      gradient: colors.gradients.actionCard3,
    },
    {
      id: "chat",
      title: "Ask Anything",
      description: "Start a conversation about travel, style, or planning",
      emoji: "💬",
      gradient: colors.gradients.actionCard4,
    },
  ]

  return (
    <div className="grid grid-cols-2 gap-4 p-4">
      {cards.map((card) => (
        <Card
          key={card.id}
          className={cn(
            "cursor-pointer hover:scale-[1.02] transition-transform duration-200 ease-in-out",
            "shadow-lg rounded-xl",
            card.gradient, // Apply the specific gradient class
          )}
          onClick={() => onActionSelect(card.id)} // Updated function call
        >
          <CardContent className="flex flex-col items-start p-4 h-full">
            <div className="text-4xl mb-2">{card.emoji}</div>
            <h3 className="font-semibold text-lg mb-1 text-white">{card.title}</h3>
            <p className="text-sm opacity-90 text-white">{card.description}</p>
          </CardContent>
        </Card>
      ))}
    </div>
  )
}
