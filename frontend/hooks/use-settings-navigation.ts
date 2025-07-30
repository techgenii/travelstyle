"use client"

import type React from "react"

import { useState } from "react"
import { User, Palette, Package, CreditCard, Bell, Plane, Ruler, MessageSquareText } from "lucide-react" // Import new icons

export type SettingSection =
  | "profile"
  | "style"
  | "packing"
  | "currency"
  | "travel-patterns" // New section
  | "size-info" // New section
  | "quick-reply" // New section
  | "notifications"

export interface SettingSectionConfig {
  id: SettingSection
  label: string
  icon: React.ComponentType<{ className?: string }>
}

export function useSettingsNavigation(initialSection: SettingSection = "profile") {
  const [activeSection, setActiveSection] = useState<SettingSection>(initialSection)

  const settingSections: SettingSectionConfig[] = [
    { id: "profile", label: "Profile", icon: User },
    { id: "style", label: "Style", icon: Palette },
    { id: "packing", label: "Packing", icon: Package },
    { id: "currency", label: "Currency", icon: CreditCard },
    { id: "travel-patterns", label: "Travel", icon: Plane }, // New
    { id: "size-info", label: "Sizes", icon: Ruler }, // New
    { id: "quick-reply", label: "Quick Replies", icon: MessageSquareText }, // New
    { id: "notifications", label: "Notifications", icon: Bell },
  ]

  return {
    activeSection,
    setActiveSection,
    settingSections,
  }
}
