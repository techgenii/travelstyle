"use client"

import { Header } from "./header"
import { Settings, HelpCircle, LogOut, MapPin, Calendar, ChevronRight, Star } from "lucide-react" // Import Star icon for premium
import { WeatherWidget } from "./weather-widget"
import { logout } from "@/actions/auth"
import { useActionState } from "react"

interface ProfileScreenProps {
  onBack?: () => void
  showBack?: boolean
}

export function ProfileScreen({ onBack, showBack = false }: ProfileScreenProps) {
  const [logoutState, logoutAction, isLoggingOut] = useActionState(logout, undefined)

  const profileData = {
    name: "Sarah Johnson",
    email: "sarah.johnson@email.com",
    memberSince: "March 2023",
    avatar: "/placeholder.svg?height=80&width=80",
    stats: {
      tripsPlanned: 12,
      countriesVisited: 8,
      wardrobesCreated: 15,
    },
  }

  const recentTrips = [
    { destination: "Paris, France", date: "Nov 2024", type: "Business" },
    { destination: "Tokyo, Japan", date: "Oct 2024", type: "Leisure" },
    { destination: "London, UK", date: "Sep 2024", type: "Weekend" },
  ]

  const menuItems = [
    { id: "go-premium", label: "Go Premium", icon: Star, hasChevron: true, accent: true }, // New Premium option
    { id: "saved-places", label: "Saved Places", icon: MapPin, hasChevron: true },
    { id: "trip-history", label: "Trip History", icon: Calendar, hasChevron: true },
    { id: "settings", label: "Settings", icon: Settings, hasChevron: true },
    { id: "help", label: "Help & Support", icon: HelpCircle, hasChevron: true },
  ]

  return (
    <div className="flex flex-col h-full bg-[#F8F6FF]">
      <Header title="Profile" />

      <div className="flex-1 overflow-y-auto">
        {/* Profile Header */}
        <div className="px-4 py-6 bg-white mx-4 mt-4 rounded-2xl shadow-soft">
          <div className="flex items-center gap-4 mb-4">
            <img
              src={profileData.avatar || "/placeholder.svg"}
              alt="Profile"
              className="w-16 h-16 rounded-full bg-gray-200"
            />
            <div className="flex-1">
              <h2 className="text-xl font-semibold text-gray-900">{profileData.name}</h2>
              <p className="text-sm text-gray-600">{profileData.email}</p>
              <p className="text-xs text-gray-500 mt-1">Member since {profileData.memberSince}</p>
            </div>
          </div>
        </div>

        {/* Weather Widget */}
        <div className="px-4 py-4">
          <WeatherWidget />
        </div>

        {/* Travel Stats */}
        <div className="px-4 py-4">
          <h3 className="text-lg font-semibold text-gray-900 mb-3">Travel Stats</h3>
          <div className="grid grid-cols-3 gap-3">
            <div className="bg-white rounded-xl p-4 text-center shadow-soft">
              <div className="text-2xl font-bold text-gray-900">{profileData.stats.tripsPlanned}</div>
              <div className="text-xs text-gray-600 mt-1">Trips Planned</div>
            </div>
            <div className="bg-white rounded-xl p-4 text-center shadow-soft">
              <div className="text-2xl font-bold text-gray-900">{profileData.stats.countriesVisited}</div>
              <div className="text-xs text-gray-600 mt-1">Countries</div>
            </div>
            <div className="bg-white rounded-xl p-4 text-center shadow-soft">
              <div className="text-2xl font-bold text-gray-900">{profileData.stats.wardrobesCreated}</div>
              <div className="text-xs text-gray-600 mt-1">Wardrobes</div>
            </div>
          </div>
        </div>

        {/* Recent Trips */}
        <div className="px-4 py-4">
          <h3 className="text-lg font-semibold text-gray-900 mb-3">Recent Trips</h3>
          <div className="bg-white rounded-2xl shadow-soft overflow-hidden">
            {recentTrips.map((trip, index) => (
              <div
                key={index}
                className={`p-4 flex items-center justify-between ${index !== recentTrips.length - 1 ? "border-b border-gray-100" : ""}`}
              >
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 bg-gray-100 rounded-full flex items-center justify-center">
                    <MapPin className="h-5 w-5 text-gray-600" />
                  </div>
                  <div>
                    <div className="font-medium text-gray-900">{trip.destination}</div>
                    <div className="text-sm text-gray-600">
                      {trip.date} • {trip.type}
                    </div>
                  </div>
                </div>
                <ChevronRight className="h-5 w-5 text-gray-400" />
              </div>
            ))}
          </div>
        </div>

        {/* Menu Items */}
        <div className="px-4 py-4">
          <div className="bg-white rounded-2xl shadow-soft overflow-hidden">
            {menuItems.map((item, index) => {
              const Icon = item.icon
              return (
                <button
                  key={item.id}
                  // Add a distinct style for the premium option
                  className={`w-full p-4 flex items-center justify-between hover:bg-gray-50 transition-colors ${index !== menuItems.length - 1 ? "border-b border-gray-100" : ""} ${item.accent ? "bg-[#E8E5FF] text-gray-900 font-semibold" : ""}`}
                >
                  <div className="flex items-center gap-3">
                    <Icon className={`h-5 w-5 ${item.accent ? "text-black" : "text-gray-600"}`} />
                    <span className="font-medium text-gray-900">{item.label}</span>
                  </div>
                  {item.hasChevron && <ChevronRight className="h-5 w-5 text-gray-400" />}
                </button>
              )
            })}
          </div>
        </div>

        {/* Sign Out */}
        <div className="px-4 py-4 pb-8">
          <form action={logoutAction}>
            <button
              type="submit"
              className="w-full bg-white rounded-2xl shadow-soft p-4 flex items-center justify-center gap-3 hover:bg-gray-50 transition-colors"
              disabled={isLoggingOut}
            >
              <LogOut className="h-5 w-5 text-red-600" />
              <span className="font-medium text-red-600">{isLoggingOut ? "Signing Out..." : "Sign Out"}</span>
            </button>
          </form>
        </div>
      </div>
    </div>
  )
}
