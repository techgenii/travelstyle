"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { ProfilePictureUpload } from "@/components/profile-picture-upload"
import { ReactNode } from "react"

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
  defaultLocation: string
  setDefaultLocation: (value: string) => void
  onPictureUpdate?: (formData: FormData) => void
  onPictureDelete?: () => void
  isUploading?: boolean
  isDeleting?: boolean
  profilePictureComponent?: ReactNode
}

export function ProfileSection({
  user,
  firstName,
  setFirstName,
  lastName,
  setLastName,
  email,
  setEmail,
  defaultLocation,
  setDefaultLocation,
  onPictureUpdate,
  onPictureDelete,
  isUploading = false,
  isDeleting = false,
  profilePictureComponent,
}: ProfileSectionProps) {
  const formatLastSeen = (lastLogin?: string) => {
    if (!lastLogin) return "Never"

    const lastLoginDate = new Date(lastLogin)
    const now = new Date()
    const diffInMs = now.getTime() - lastLoginDate.getTime()
    const diffInHours = diffInMs / (1000 * 60 * 60)
    const diffInDays = diffInHours / 24
    const diffInMonths = diffInDays / 30
    const diffInYears = diffInDays / 365

    if (diffInHours < 24) {
      const hours = Math.floor(diffInHours)
      return `${hours} hour${hours !== 1 ? 's' : ''} ago`
    } else if (diffInDays < 30) {
      const days = Math.floor(diffInDays)
      return `${days} day${days !== 1 ? 's' : ''} ago`
    } else if (diffInDays < 365) {
      const months = Math.floor(diffInMonths)
      return `${months} month${months !== 1 ? 's' : ''} ago`
    } else {
      const years = Math.floor(diffInYears)
      return `${years} year${years !== 1 ? 's' : ''} ago`
    }
  }
  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-lg font-semibold text-gray-800">
          Personal Information
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {profilePictureComponent || (
          onPictureUpdate && onPictureDelete ? (
            <ProfilePictureUpload
              currentPictureUrl={user.profilePictureUrl}
              firstName={firstName}
              lastName={lastName}
              onPictureUpdate={onPictureUpdate}
              onPictureDelete={onPictureDelete}
              isUploading={isUploading}
              isDeleting={isDeleting}
            />
          ) : null
        )}

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
          <h4 className="font-medium text-gray-700 mb-2">Account Information</h4>
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <span className="text-gray-500">Account Type:</span>
              <span className="ml-2 font-medium">
                {user.isPremium ? "Premium" : "Free"}
              </span>
            </div>
            <div>
              <span className="text-gray-500">Member Since:</span>
              <span className="ml-2 font-medium">
                {user.createdAt ? new Date(user.createdAt).toLocaleDateString('en-US', {
                  year: 'numeric',
                  month: 'short',
                  day: '2-digit'
                }) : "N/A"}
              </span>
            </div>
            <div>
              <span className="text-gray-500">Last Seen:</span>
              <span className="ml-2 font-medium">
                {formatLastSeen(user.lastLogin)}
              </span>
            </div>
            {user.maxBookmarks && (
              <div>
                <span className="text-gray-500">Bookmarks Limit:</span>
                <span className="ml-2 font-medium">{user.maxBookmarks}</span>
              </div>
            )}
            {user.maxConversations && (
              <div>
                <span className="text-gray-500">Conversations Limit:</span>
                <span className="ml-2 font-medium">{user.maxConversations}</span>
              </div>
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
