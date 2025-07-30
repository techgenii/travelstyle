"use client"

import { Card, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { cn } from "@/lib/utils"
import type { SettingSection, SettingSectionConfig } from "@/hooks/use-settings-navigation"

interface SettingsNavigationProps {
  activeSection: SettingSection
  onSectionChange: (section: SettingSection) => void
  sections: SettingSectionConfig[]
}

export function SettingsNavigation({ activeSection, onSectionChange, sections }: SettingsNavigationProps) {
  return (
    <Card>
      <CardContent className="p-2">
        <div className="grid grid-cols-3 gap-1">
          {sections.map((section) => {
            const Icon = section.icon
            return (
              <Button
                key={section.id}
                variant={activeSection === section.id ? "default" : "ghost"}
                size="sm"
                onClick={() => onSectionChange(section.id)}
                className={cn("justify-start text-xs", activeSection === section.id && "bg-purple-600 text-white")}
              >
                <Icon className="h-4 w-4 mr-1" />
                {section.label}
              </Button>
            )
          })}
        </div>
      </CardContent>
    </Card>
  )
}
