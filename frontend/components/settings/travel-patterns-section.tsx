"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Plane } from "lucide-react"
import { ToggleableList } from "./toggleable-list"

interface TravelPatternsSectionProps {
  selectedTravelPatterns: string[]
  onToggleTravelPattern: (pattern: string) => void
}

const availableTravelPatterns = [
  "Business",
  "Leisure",
  "Adventure",
  "Family",
  "Solo",
  "Romantic",
  "Cultural",
  "Relaxation",
  "Road Trip",
  "Cruise",
]

export function TravelPatternsSection({ selectedTravelPatterns, onToggleTravelPattern }: TravelPatternsSectionProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Plane className="h-5 w-5" />
          Travel Patterns
        </CardTitle>
      </CardHeader>
      <CardContent>
        <ToggleableList
          title="Travel Types"
          description="Select your common travel types:"
          items={availableTravelPatterns}
          selectedItems={selectedTravelPatterns}
          onToggle={onToggleTravelPattern}
          columns={2}
        />
      </CardContent>
    </Card>
  )
}
