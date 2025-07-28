"use client"

import type React from "react"

import { Home, MessageCircle, User } from "lucide-react"
import { cn } from "@/lib/utils"

type NavigationTab = "home" | "recent" | "profile"

interface BottomNavigationProps {
  activeTab: NavigationTab
  onTabChange: (tab: NavigationTab) => void
}

interface NavItem {
  id: NavigationTab
  label: string
  icon: React.ComponentType<{ className?: string }>
}

const navItems: NavItem[] = [
  {
    id: "home",
    label: "Home",
    icon: Home,
  },
  {
    id: "recent",
    label: "Recent",
    icon: MessageCircle,
  },
  {
    id: "profile",
    label: "Profile",
    icon: User,
  },
]

export function BottomNavigation({ activeTab, onTabChange }: BottomNavigationProps) {
  return (
    <div className="sticky bottom-0 bg-white border-t border-gray-200 px-2 py-1 safe-area-pb">
      <div className="flex items-center justify-around">
        {navItems.map((item) => {
          const Icon = item.icon
          const isActive = activeTab === item.id

          return (
            <button
              key={item.id}
              onClick={() => onTabChange(item.id)}
              className={cn(
                "relative flex flex-col items-center justify-center py-2 px-3 rounded-lg transition-colors duration-200 min-w-[60px]",
                isActive ? "text-black" : "text-gray-500 hover:text-gray-700 hover:bg-gray-50",
              )}
            >
              <Icon className={cn("h-5 w-5 mb-1", isActive && "text-black")} />
              <span className={cn("text-xs font-medium", isActive ? "text-black" : "text-gray-500")}>{item.label}</span>
              {isActive && (
                <div className="absolute bottom-0 left-1/2 transform -translate-x-1/2 w-1 h-1 bg-black rounded-full"></div>
              )}
            </button>
          )
        })}
      </div>
    </div>
  )
}
