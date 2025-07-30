"use client"

import { Home, MessageSquare, User } from "lucide-react"
import { Button } from "@/components/ui/button"
import { cn } from "@/lib/utils"

interface BottomNavigationProps {
  activeTab: "home" | "recent" | "profile"
  onTabChange: (tab: "home" | "recent" | "profile") => void
}

export function BottomNavigation({ activeTab, onTabChange }: BottomNavigationProps) {
  const navItems = [
    { id: "home", icon: Home, label: "Home" },
    { id: "recent", icon: MessageSquare, label: "Recent" },
    { id: "profile", icon: User, label: "Profile" },
  ]

  return (
    <nav className="flex justify-around items-center h-16 bg-white border-t border-gray-200 shadow-lg">
      {navItems.map((item) => {
        const Icon = item.icon
        const isActive = activeTab === item.id
        return (
          <Button
            key={item.id}
            variant="ghost"
            className={cn(
              "relative flex flex-col items-center justify-center h-full w-full text-gray-500 transition-colors duration-200",
              isActive ? "text-[#8A2BE2]" : "hover:text-gray-700",
            )}
            onClick={() => onTabChange(item.id as "home" | "recent" | "profile")}
          >
            <Icon size={24} className="mb-1" />
            <span className="text-xs font-medium">{item.label}</span>
            {isActive && <div className="absolute bottom-1 w-1.5 h-1.5 bg-[#8A2BE2] rounded-full"></div>}
          </Button>
        )
      })}
    </nav>
  )
}
