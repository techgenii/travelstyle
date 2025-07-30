"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Palette } from "lucide-react"
import { ToggleableList } from "./toggleable-list"

interface StyleSectionProps {
  selectedStyles: string[]
  onToggleStyle: (style: string) => void
}

const availableStyles = [
  "Business Casual",
  "Formal",
  "Casual",
  "Bohemian",
  "Minimalist",
  "Classic",
  "Trendy",
  "Sporty",
  "Elegant",
  "Vintage",
]

export function StyleSection({ selectedStyles, onToggleStyle }: StyleSectionProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Palette className="h-5 w-5" />
          Style Preferences
        </CardTitle>
      </CardHeader>
      <CardContent>
        <ToggleableList
          title="Styles"
          description="Select your preferred styles:"
          items={availableStyles}
          selectedItems={selectedStyles}
          onToggle={onToggleStyle}
          columns={2}
        />
      </CardContent>
    </Card>
  )
}
