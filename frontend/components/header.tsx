"use client"

import { ChevronLeft, MoreHorizontal } from "lucide-react"
import { Button } from "@/components/ui/button"

interface HeaderProps {
  title: string
  onBack?: () => void
  showBack?: boolean
  onMore?: () => void
}

export function Header({ title, onBack, showBack = false, onMore }: HeaderProps) {
  return (
    <div className="flex items-center justify-between h-15 px-4 bg-transparent">
      <div className="w-6">
        {showBack && (
          <Button variant="ghost" size="icon" onClick={onBack} className="h-6 w-6 p-0 hover:bg-gray-100">
            <ChevronLeft className="h-6 w-6 text-gray-900" />
          </Button>
        )}
      </div>

      <h1 className="text-lg font-semibold text-gray-900 text-center">{title}</h1>

      <div className="w-6">
        {onMore && (
          <Button variant="ghost" size="icon" onClick={onMore} className="h-6 w-6 p-0 hover:bg-gray-100">
            <MoreHorizontal className="h-6 w-6 text-gray-900" />
          </Button>
        )}
      </div>
    </div>
  )
}
