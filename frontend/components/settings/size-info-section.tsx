"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Ruler } from "lucide-react"

interface SizeInfo {
  shirt_size?: string
  pant_size?: string
  shoe_size?: string
  dress_size?: string
  skirt_size?: string // New: Add skirt_size
  bathing_suit_size?: string // New: Add bathing_suit_size
}

interface SizeInfoSectionProps {
  sizeInfo: SizeInfo
  onSizeInfoChange: (key: keyof SizeInfo, value: string) => void
}

export function SizeInfoSection({ sizeInfo, onSizeInfoChange }: SizeInfoSectionProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Ruler className="h-5 w-5" />
          Size Information
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div>
          <Label htmlFor="shirt-size">Shirt Size</Label>
          <Input
            id="shirt-size"
            value={sizeInfo.shirt_size || ""}
            onChange={(e) => onSizeInfoChange("shirt_size", e.target.value)}
            placeholder="e.g., M, L, XL"
          />
        </div>
        <div>
          <Label htmlFor="pant-size">Pant Size</Label>
          <Input
            id="pant-size"
            value={sizeInfo.pant_size || ""}
            onChange={(e) => onSizeInfoChange("pant_size", e.target.value)}
            placeholder="e.g., 32x30, 8"
          />
        </div>
        <div>
          <Label htmlFor="shoe-size">Shoe Size</Label>
          <Input
            id="shoe-size"
            value={sizeInfo.shoe_size || ""}
            onChange={(e) => onSizeInfoChange("shoe_size", e.target.value)}
            placeholder="e.g., 10 US, 43 EU"
          />
        </div>
        <div>
          <Label htmlFor="dress-size">Dress Size</Label>
          <Input
            id="dress-size"
            value={sizeInfo.dress_size || ""}
            onChange={(e) => onSizeInfoChange("dress_size", e.target.value)}
            placeholder="e.g., S, M, L, 4, 6, 8"
          />
        </div>
        {/* New: Skirt Size Input */}
        <div>
          <Label htmlFor="skirt-size">Skirt Size</Label>
          <Input
            id="skirt-size"
            value={sizeInfo.skirt_size || ""}
            onChange={(e) => onSizeInfoChange("skirt_size", e.target.value)}
            placeholder="e.g., S, M, L, 4, 6, 8"
          />
        </div>
        {/* New: Bathing Suit Size Input */}
        <div>
          <Label htmlFor="bathing-suit-size">Bathing Suit Size</Label>
          <Input
            id="bathing-suit-size"
            value={sizeInfo.bathing_suit_size || ""}
            onChange={(e) => onSizeInfoChange("bathing_suit_size", e.target.value)}
            placeholder="e.g., S, M, L, 4, 6, 8"
          />
        </div>
      </CardContent>
    </Card>
  )
}
