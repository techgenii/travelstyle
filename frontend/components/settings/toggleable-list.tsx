"use client"

import { Badge } from "@/components/ui/badge"
import { Check, X } from "lucide-react"
import { cn } from "@/lib/utils"

interface ToggleableListProps {
  title: string
  description: string
  items: string[]
  selectedItems: string[]
  onToggle: (item: string) => void
  columns?: number
  compact?: boolean
}

export function ToggleableList({
  title,
  description,
  items,
  selectedItems,
  onToggle,
  columns = 2,
  compact = false,
}: ToggleableListProps) {
  return (
    <div className="space-y-4">
      <div>
        <h4 className="font-medium mb-1 text-gray-800">{title}</h4>
        <div className="text-sm text-gray-600 mb-2">{description}</div>
      </div>

      <div className={cn("grid gap-2", `grid-cols-${columns}`)}>
        {items.map((item) => {
          const isSelected = selectedItems.includes(item)
          return (
            <button
              key={item}
              type="button"
              onClick={() => onToggle(item)}
              className={cn(
                "flex items-center justify-between p-3 rounded-lg border transition-colors",
                compact && "p-2",
                isSelected
                  ? "bg-purple-50 border-purple-200 text-purple-800"
                  : "bg-gray-50 border-gray-200 text-gray-700 hover:bg-gray-100",
              )}
            >
              <span className={cn("font-medium", compact ? "text-xs" : "text-sm")}>{item}</span>
              {isSelected && <Check className="h-4 w-4 text-purple-600" />}
            </button>
          )
        })}
      </div>

      {selectedItems.length > 0 && (
        <div className="mt-3">
          <div className="text-sm text-gray-600 mb-2">
            Selected {title.toLowerCase()} ({selectedItems.length}):
          </div>
          <div className="flex flex-wrap gap-2">
            {selectedItems.map((item, index) => (
              <Badge key={index} variant="secondary" className="flex items-center gap-1">
                {item}
                <X className="h-3 w-3 cursor-pointer hover:text-red-500" onClick={() => onToggle(item)} />
              </Badge>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
