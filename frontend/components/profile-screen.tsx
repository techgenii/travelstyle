"use client"

import { Header } from "./header"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Crown, Settings, HelpCircle, History, Bookmark, ChevronRight, LogOut } from "lucide-react"
import { WeatherWidget } from "./weather-widget"
import { cn } from "@/lib/utils"
import { colors } from "@/lib/design-system"
import { logout } from "@/lib/auth"

interface ProfileScreenProps {
  onBack?: () => void
  onSettingsClick?: () => void
  user: {
    id: string
    firstName: string
    lastName?: string | null
    email: string
    profilePictureUrl?: string | null
    defaultLocation?: string | null // New: Add defaultLocation to user prop
  }
}

export function ProfileScreen({ onBack, onSettingsClick, user }: ProfileScreenProps) {
  // Safety check to ensure user data is available
  if (!user) {
    return (
      <div className="flex flex-col h-full bg-[#F8F6FF]">
        <Header title="Profile" showBack onBack={onBack} />
        <div className="flex-1 flex items-center justify-center">
          <div className="text-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
            <p className="text-gray-600">Loading profile...</p>
          </div>
        </div>
      </div>
    )
  }

  const userFullName = `${user?.firstName || "Guest"} ${user?.lastName || ""}`.trim()
  const userEmail = user?.email || "guest@example.com"
  const userLocation = user?.defaultLocation || "Los Angeles" // Use defaultLocation from user, fallback to Los Angeles

  const profileStats = {
    tripsPlanned: 12,
    countriesVisited: 8,
    wardrobesCreated: 15,
  }

  const menuItems = [
    { id: "go-premium", label: "Go Premium", icon: Crown, hasChevron: true, accent: true },
    { id: "saved-places", label: "Saved Places", icon: Bookmark, hasChevron: true },
    { id: "trip-history", label: "Trip History", icon: History, hasChevron: true },
    { id: "settings", label: "Settings", icon: Settings, hasChevron: true },
    { id: "help", label: "Help & Support", icon: HelpCircle, hasChevron: true },
  ]

  const handleMenuItemClick = (itemId: string) => {
    switch (itemId) {
      case "settings":
        if (onSettingsClick) {
          onSettingsClick()
        }
        break
      case "go-premium":
        console.log("Navigate to premium page")
        break
      case "saved-places":
        console.log("Navigate to saved places")
        break
      case "trip-history":
        console.log("Navigate to trip history")
        break
      case "help":
        console.log("Navigate to help & support")
        break
      default:
        console.log(`Menu item clicked: ${itemId}`)
    }
  }

  const handleEditProfileClick = () => {
    // Navigate to settings when Edit Profile is clicked
    if (onSettingsClick) {
      onSettingsClick()
    }
  }

  const handleLogout = async () => {
    console.log("[ProfileScreen] Logging out...")

    try {
      // Call the logout function which handles both server and client cleanup
      await logout()
      console.log("[ProfileScreen] Logout successful")
    } catch (error) {
      console.error("[ProfileScreen] Logout error:", error)
    }
  }

  return (
    <div className="flex flex-col h-full bg-[#F8F6FF]">
      <Header title="Profile" showBack onBack={onBack} />
      <div className="flex-1 overflow-y-auto p-4 space-y-6 custom-scrollbar">
        {/* Profile Header Section */}
        <Card className="flex flex-col items-center p-4 bg-white rounded-2xl shadow-soft border border-gray-100">
          <Avatar className="w-24 h-24 mb-4 border-4 border-purple-500 shadow-lg">
            <AvatarImage
              src={user.profilePictureUrl || "/placeholder.svg?height=96&width=96&text=User"}
              alt={`${userFullName}'s avatar`}
            />
            <AvatarFallback className="bg-purple-500 text-white text-3xl">
              {user.firstName?.charAt(0) || ""}
              {user.lastName?.charAt(0) || ""}
            </AvatarFallback>
          </Avatar>
          <h2 className="text-2xl font-bold text-gray-800">{userFullName}</h2>
          <p className="text-gray-500">{userEmail}</p>
          <Button
            variant="outline"
            className="mt-4 rounded-full border-purple-500 text-purple-600 hover:bg-purple-50 bg-transparent"
            onClick={handleEditProfileClick}
          >
            Edit Profile
          </Button>
        </Card>
        {/* Travel Stats */}
        <Card className="bg-white rounded-2xl shadow-soft border border-gray-100">
          <CardHeader>
            <CardTitle className="text-lg text-gray-800">Travel Stats</CardTitle>
          </CardHeader>
          <CardContent className="grid grid-cols-3 gap-3">
            <div className="flex flex-col items-center text-center">
              <div className="text-2xl font-bold text-gray-900">{profileStats.tripsPlanned}</div>
              <div className="text-xs text-gray-600 mt-1">Trips Planned</div>
            </div>
            <div className="flex flex-col items-center text-center">
              <div className="text-2xl font-bold text-gray-900">{profileStats.countriesVisited}</div>
              <div className="text-xs text-gray-600 mt-1">Countries</div>
            </div>
            <div className="flex flex-col items-center text-center">
              <div className="text-2xl font-bold text-gray-900">{profileStats.wardrobesCreated}</div>
              <div className="text-xs text-gray-600 mt-1">Wardrobes</div>
            </div>
          </CardContent>
        </Card>
        {/* Weather Widget */}
        <WeatherWidget location={userLocation} /> {/* Pass userLocation */}
        {/* Menu Items */}
        <Card className="bg-white rounded-2xl shadow-soft border border-gray-100">
          <CardContent className="p-0">
            {menuItems.map((item, index) => {
              const Icon = item.icon
              return (
                <button
                  key={item.id}
                  onClick={() => handleMenuItemClick(item.id)}
                  className={cn(
                    "w-full flex items-center space-x-4 p-4 transition-colors",
                    item.accent
                      ? cn(colors.gradients.premium, "hover:brightness-105 text-yellow-900")
                      : "bg-white hover:bg-gray-50 text-gray-700",
                    index !== menuItems.length - 1 && "border-b border-gray-100",
                  )}
                >
                  <Icon size={20} className={item.accent ? "text-yellow-600" : "text-gray-600"} />
                  <span className={cn("font-medium", item.accent ? "text-yellow-900" : "text-gray-800")}>
                    {item.label}
                  </span>
                  {item.hasChevron && <ChevronRight className="h-5 w-5 text-gray-400 ml-auto" />}
                </button>
              )
            })}
          </CardContent>
        </Card>
        {/* Logout Button */}
        <div className="p-4">
          <Button
            onClick={handleLogout}
            className="w-full bg-red-500 hover:bg-red-600 text-white rounded-full py-3 shadow-md"
          >
            <LogOut className="h-5 w-5 mr-2" />
            Sign Out
          </Button>
        </div>
      </div>
    </div>
  )
}
