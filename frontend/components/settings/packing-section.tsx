"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Package } from "lucide-react"
import { ToggleableList } from "./toggleable-list"

interface PackingSectionProps {
  selectedPackingMethods: string[]
  onTogglePackingMethod: (method: string) => void
}

const availablePackingMethods = [
  "5-4-3-2-1 Method",
  "3x3x3 Capsule",
  "Rule of 3s",
  "10×10 Challenge",
  "12-Piece Travel Capsule",
  "4x4 Wardrobe Grid",
  "1-2-3-4-5-6 Formula",
]

export function PackingSection({ selectedPackingMethods, onTogglePackingMethod }: PackingSectionProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Package className="h-5 w-5" />
          Packing Methods
        </CardTitle>
      </CardHeader>
      <CardContent>
        <ToggleableList
          title="Methods"
          description="Select your preferred packing methods:"
          items={availablePackingMethods}
          selectedItems={selectedPackingMethods}
          onToggle={onTogglePackingMethod}
          columns={1}
        />
      </CardContent>
    </Card>
  )
}
