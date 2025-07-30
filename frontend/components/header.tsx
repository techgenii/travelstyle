"use client"

import { ChevronLeft, Settings, User } from "lucide-react"
import { useRouter } from "next/navigation"
import { cn } from "@/lib/utils"
import { colors } from "@/lib/design-system"

interface HeaderProps {
  title: string
  showBack?: boolean
  onBack?: () => void
  showProfile?: boolean
  onProfileClick?: () => void
  showSettings?: boolean
  onSettingsClick?: () => void // New prop for settings click handler
}

export function Header({
  title,
  showBack,
  onBack,
  showProfile,
  onProfileClick,
  showSettings,
  onSettingsClick,
}: HeaderProps) {
  const router = useRouter()

  const handleBackClick = () => {
    if (onBack) {
      onBack()
    } else {
      router.back()
    }
  }

  const handleProfileClick = () => {
    if (onProfileClick) {
      onProfileClick()
    } else {
      router.push("/profile") // Fallback
    }
  }

  const handleSettingsClick = () => {
    if (onSettingsClick) {
      onSettingsClick()
    } else {
      router.push("/settings") // Fallback
    }
  }

  return (
    <header
      className={cn(
        "flex items-center justify-between p-4 h-16",
        colors.gradients.header, // Apply the header gradient
      )}
    >
      <div className="flex items-center">
        {showBack && (
          <button onClick={handleBackClick} className="mr-2 p-1 rounded-full hover:bg-white/20 transition-colors">
            <ChevronLeft className="h-6 w-6 text-white" />
          </button>
        )}
        <h1 className="text-xl font-semibold text-white">{title}</h1>
      </div>
      <div className="flex items-center space-x-2">
        {showProfile && (
          <button onClick={handleProfileClick} className="p-1 rounded-full hover:bg-white/20 transition-colors">
            <User className="h-6 w-6 text-white" />
          </button>
        )}
        {showSettings && (
          <button onClick={handleSettingsClick} className="p-1 rounded-full hover:bg-white/20 transition-colors">
            <Settings className="h-6 w-6 text-white" />
          </button>
        )}
      </div>
    </header>
  )
}
