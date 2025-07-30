"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Camera } from "lucide-react"

interface ProfileSectionProps {
  user: {
    id: string
    firstName: string
    lastName?: string | null
    email: string
    profilePictureUrl?: string | null
    profileCompleted?: boolean
    createdAt?: string
    updatedAt?: string
    lastLogin?: string
    isPremium?: boolean
    defaultLocation?: string | null
    maxBookmarks?: number | null
    maxConversations?: number | null
    subscriptionTier?: string | null
    subscriptionExpiresAt?: string | null
  }
  firstName: string
  setFirstName: (value: string) => void
  lastName: string
  setLastName: (value: string) => void
  email: string
  setEmail: (value: string) => void
  defaultLocation: string // New: Add defaultLocation state
  setDefaultLocation: (value: string) => void // New: Add setDefaultLocation setter
}

export function ProfileSection({
  user,
  firstName,
  setFirstName,
  lastName,
  setLastName,
  email,
  setEmail,
  defaultLocation, // Destructure new props
  setDefaultLocation, // Destructure new props
}: ProfileSectionProps) {
  const formatDate = (dateString?: string) => {
    if (!dateString) return "Not available"
    return new Date(dateString).toLocaleDateString("en-US", {
      year: "numeric",
      month: "long",
      day: "numeric",
    })
  }

  const formatDateTime = (dateString?: string) => {
    if (!dateString) return "Not available"
    return new Date(dateString).toLocaleDateString("en-US", {
      year: "numeric",
      month: "long",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    })
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Camera className="h-5 w-5" />
          Personal Information
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="flex items-center gap-4">
          <Avatar className="w-20 h-20">
            <AvatarImage src={user.profilePictureUrl || "/placeholder.svg?height=80&width=80&text=User"} />
            <AvatarFallback className="bg-purple-500 text-white text-2xl">
              {firstName.charAt(0)}
              {lastName.charAt(0)}
            </AvatarFallback>
          </Avatar>
          <Button variant="outline" size="sm" className="flex items-center gap-2 bg-transparent">
            <Camera className="h-4 w-4" />
            Change Photo
          </Button>
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <Label htmlFor="firstName">First Name</Label>
            <Input
              id="firstName"
              value={firstName}
              onChange={(e) => setFirstName(e.target.value)}
              placeholder="Enter first name"
            />
          </div>
          <div>
            <Label htmlFor="lastName">Last Name</Label>
            <Input
              id="lastName"
              value={lastName}
              onChange={(e) => setLastName(e.target.value)}
              placeholder="Enter last name"
            />
          </div>
        </div>

        <div>
          <Label htmlFor="email">Email Address</Label>
          <Input
            id="email"
            type="email"
            value={email}
            readOnly
            className="bg-gray-50 cursor-not-allowed"
            placeholder="Email address"
          />
        </div>

        {/* New: Default Location Input */}
        <div>
          <Label htmlFor="default-location">Default Weather Location</Label>
          <Input
            id="default-location"
            value={defaultLocation}
            onChange={(e) => setDefaultLocation(e.target.value)}
            placeholder="e.g., New York, London, Tokyo"
          />
        </div>

        {/* Account Information */}
        <div className="pt-4 border-t">
          <h4 className="font-medium mb-3 text-gray-800">Account Information</h4>
          <div className="grid grid-cols-1 gap-3 text-sm">
            <div className="flex justify-between items-center p-2 bg-gray-50 rounded-lg">
              <span className="text-gray-600">Member since:</span>
              <span className="font-medium text-gray-800">{formatDate(user.createdAt)}</span>
            </div>
            <div className="flex justify-between items-center p-2 bg-gray-50 rounded-lg">
              <span className="text-gray-600">Last updated:</span>
              <span className="font-medium text-gray-800">{formatDate(user.updatedAt)}</span>
            </div>
            <div className="flex justify-between items-center p-2 bg-gray-50 rounded-lg">
              <span className="text-gray-600">Last login:</span>
              <span className="font-medium text-gray-800">{formatDateTime(user.lastLogin)}</span>
            </div>
            <div className="flex justify-between items-center p-2 bg-gray-50 rounded-lg">
              <span className="text-gray-600">Profile completed:</span>
              <span className={`font-medium ${user.profileCompleted ? "text-green-600" : "text-orange-600"}`}>
                {user.profileCompleted ? "Yes" : "No"}
              </span>
            </div>
          </div>
        </div>

        {/* Account Limits */}
        <div className="pt-4 border-t">
          <h4 className="font-medium mb-3 text-gray-800">Account Limits</h4>
          <div className="grid grid-cols-1 gap-3 text-sm">
            <div className="flex justify-between items-center p-2 bg-purple-50 rounded-lg">
              <span className="text-gray-600">Max Bookmarks:</span>
              <span className="font-medium text-purple-800">
                {user.maxBookmarks || 50} ({user.subscriptionTier || 'free'})
              </span>
            </div>
            <div className="flex justify-between items-center p-2 bg-purple-50 rounded-lg">
              <span className="text-gray-600">Max Conversations:</span>
              <span className="font-medium text-purple-800">
                {user.maxConversations || 100} ({user.subscriptionTier || 'free'})
              </span>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
