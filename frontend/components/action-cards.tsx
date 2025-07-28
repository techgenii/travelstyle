"use client"

interface ActionCard {
  id: string
  title: string
  description: string
  emoji: string
}

interface ActionCardsProps {
  cards: ActionCard[]
  onCardSelect: (cardId: string) => void
}

export function ActionCards({ cards, onCardSelect }: ActionCardsProps) {
  return (
    <div className="grid grid-cols-2 gap-3 px-4 mb-6">
      {cards.map((card) => (
        <button
          key={card.id}
          onClick={() => onCardSelect(card.id)}
          className="bg-white rounded-2xl p-5 shadow-soft text-left min-h-[100px] hover:shadow-medium transition-shadow duration-200 border border-gray-100"
        >
          <div className="text-2xl mb-2">{card.emoji}</div>
          <h3 className="font-medium text-gray-900 text-sm leading-tight mb-1">{card.title}</h3>
          <p className="text-xs text-gray-600 leading-relaxed">{card.description}</p>
        </button>
      ))}
    </div>
  )
}
