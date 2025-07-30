"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Label } from "@/components/ui/label"
import { Switch } from "@/components/ui/switch"
import { MessageSquareText } from "lucide-react"

interface QuickReplyPreferences {
  enabled?: boolean
  // Add more fields if needed, e.g., custom_replies: string[]
}

interface QuickReplySectionProps {
  quickReplyPreferences: QuickReplyPreferences
  onToggleQuickReplies: (enabled: boolean) => void
}

export function QuickReplySection({ quickReplyPreferences, onToggleQuickReplies }: QuickReplySectionProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <MessageSquareText className="h-5 w-5" />
          Quick Reply Preferences
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <Label htmlFor="enable-quick-replies">Enable Quick Replies</Label>
            <p className="text-sm text-gray-500">Show suggested quick replies in chat conversations</p>
          </div>
          <Switch
            id="enable-quick-replies"
            checked={quickReplyPreferences.enabled || false}
            onCheckedChange={onToggleQuickReplies}
          />
        </div>
      </CardContent>
    </Card>
  )
}
