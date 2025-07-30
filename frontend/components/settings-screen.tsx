"use client"

import type React from "react"

import { useState } from "react"
import { Header } from "./header"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Badge } from "@/components/ui/badge"
import { Switch } from "@/components/ui/switch"
import { User, Bell, Palette, Package, CreditCard, Camera, X, Save, Loader2, Check } from "lucide-react"
import { cn } from "@/lib/utils"
import { updateUserProfile } from "@/actions/user"
import { useActionState } from "react"
import { getAuthToken } from "@/lib/auth"

interface SettingsScreenProps {
  onBack: () => void
  user: {
    id: string
    firstName: string
    lastName?: string | null
    email: string
    profilePictureUrl?: string | null
    profileCompleted?: boolean
    stylePreferences?: Record<string, any>
    sizeInfo?: Record<string, any>
    travelPatterns?: Record<string, any>
    quickReplyPreferences?: Record<string, any>
    packingMethods?: Record<string, any>
    currencyPreferences?: Record<string, any>
    selectedStyleNames?: string[]
    createdAt?: string
    updatedAt?: string
    lastLogin?: string
    isPremium?: boolean // Add this field
  }
}

export function SettingsScreen({ onBack, user }: SettingsScreenProps) {
  const [activeSection, setActiveSection] = useState<string>("profile")

  // Simple form state
  const [firstName, setFirstName] = useState(user.firstName || "")
  const [lastName, setLastName] = useState(user.lastName || "")
  const [email, setEmail] = useState(user.email || "")
  const [selectedStyles, setSelectedStyles] = useState<string[]>(user.selectedStyleNames || [])
  const [selectedPackingMethods, setSelectedPackingMethods] = useState<string[]>(
    user.packingMethods?.selected_methods || [],
  )
  const [selectedCurrencies, setSelectedCurrencies] = useState<string[]>(
    user.currencyPreferences?.preferred_currencies || [],
  )

  // Create a wrapper function for the action that includes the token
  const updateProfileAction = async (prevState: any, formData: FormData) => {
    const token = getAuthToken()
    if (!token) {
      return { success: false, message: "", error: "No authentication token found" }
    }
    return updateUserProfile(token, prevState, formData)
  }

  const [updateState, updateAction, isUpdating] = useActionState(updateProfileAction, {
    success: false,
    message: "",
    error: "",
  })

  const settingSections = [
    { id: "profile", label: "Profile", icon: User },
    { id: "style", label: "Style", icon: Palette },
    { id: "packing", label: "Packing", icon: Package },
    { id: "currency", label: "Currency", icon: CreditCard },
    { id: "notifications", label: "Notifications", icon: Bell },
  ]

  // Simple hardcoded data
  const availableStyles = [
    "Business Casual",
    "Formal",
    "Casual",
    "Bohemian",
    "Minimalist",
    "Classic",
    "Trendy",
    "Sporty",
    "Elegant",
    "Vintage",
  ]

  const availablePackingMethods = [
    "5-4-3-2-1 Method",
    "3x3x3 Capsule",
    "Rule of 3s",
    "10×10 Challenge",
    "12-Piece Travel Capsule",
    "4x4 Wardrobe Grid",
    "1-2-3-4-5-6 Formula",
  ]

  const supportedCurrencies = [
    "USD",
    "EUR",
    "GBP",
    "JPY",
    "CAD",
    "AUD",
    "CHF",
    "CNY",
    "INR",
    "BRL",
    "MXN",
    "KRW",
    "SGD",
    "HKD",
    "NZD",
    "SEK",
    "NOK",
    "DKK",
    "PLN",
    "CZK",
    "HUF",
    "ILS",
    "ZAR",
    "THB",
    "PHP",
    "MYR",
    "IDR",
    "VND",
    "TRY",
    "RUB",
    "AED",
    "SAR",
    "QAR",
    "KWD",
    "BHD",
    "OMR",
    "JOD",
    "LBP",
    "EGP",
    "MAD",
  ]

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    const formData = new FormData()

    formData.append("firstName", firstName)
    formData.append("lastName", lastName)
    formData.append("email", email)
    formData.append("selectedStyleNames", JSON.stringify(selectedStyles))
    formData.append("packingMethods", JSON.stringify({ selected_methods: selectedPackingMethods }))
    formData.append("currencyPreferences", JSON.stringify({ preferred_currencies: selectedCurrencies }))

    updateAction(formData)
  }

  const toggleItem = (item: string, currentList: string[], setList: (list: string[]) => void) => {
    if (currentList.includes(item)) {
      setList(currentList.filter((i) => i !== item))
    } else {
      setList([...currentList, item])
    }
  }

  const renderProfileSection = () => (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <User className="h-5 w-5" />
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
            onChange={(e) => setEmail(e.target.value)}
            placeholder="Enter email address"
          />
        </div>

        {/* Account Information */}
        <div className="pt-4 border-t">
          <h4 className="font-medium mb-3 text-gray-800">Account Information</h4>
          <div className="grid grid-cols-1 gap-3 text-sm">
            <div className="flex justify-between items-center p-2 bg-gray-50 rounded-lg">
              <span className="text-gray-600">Member since:</span>
              <span className="font-medium text-gray-800">
                {user.createdAt
                  ? new Date(user.createdAt).toLocaleDateString("en-US", {
                      year: "numeric",
                      month: "long",
                      day: "numeric",
                    })
                  : "Not available"}
              </span>
            </div>
            <div className="flex justify-between items-center p-2 bg-gray-50 rounded-lg">
              <span className="text-gray-600">Last updated:</span>
              <span className="font-medium text-gray-800">
                {user.updatedAt
                  ? new Date(user.updatedAt).toLocaleDateString("en-US", {
                      year: "numeric",
                      month: "long",
                      day: "numeric",
                    })
                  : "Not available"}
              </span>
            </div>
            <div className="flex justify-between items-center p-2 bg-gray-50 rounded-lg">
              <span className="text-gray-600">Last login:</span>
              <span className="font-medium text-gray-800">
                {user.lastLogin
                  ? new Date(user.lastLogin).toLocaleDateString("en-US", {
                      year: "numeric",
                      month: "long",
                      day: "numeric",
                      hour: "2-digit",
                      minute: "2-digit",
                    })
                  : "Not available"}
              </span>
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
              <span className="font-medium text-purple-800">{user.isPremium ? "200 (Premium)" : "50 (Free)"}</span>
            </div>
            <div className="flex justify-between items-center p-2 bg-purple-50 rounded-lg">
              <span className="text-gray-600">Max Conversations:</span>
              <span className="font-medium text-purple-800">{user.isPremium ? "500 (Premium)" : "100 (Free)"}</span>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  )

  const renderStyleSection = () => (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Palette className="h-5 w-5" />
          Style Preferences
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="text-sm text-gray-600 mb-2">Select your preferred styles:</div>
        <div className="grid grid-cols-2 gap-2">
          {availableStyles.map((style) => {
            const isSelected = selectedStyles.includes(style)
            return (
              <button
                key={style}
                type="button"
                onClick={() => toggleItem(style, selectedStyles, setSelectedStyles)}
                className={`flex items-center justify-between p-3 rounded-lg border transition-colors ${
                  isSelected
                    ? "bg-purple-50 border-purple-200 text-purple-800"
                    : "bg-gray-50 border-gray-200 text-gray-700 hover:bg-gray-100"
                }`}
              >
                <span className="font-medium text-sm">{style}</span>
                {isSelected && <Check className="h-4 w-4 text-purple-600" />}
              </button>
            )
          })}
        </div>
        {selectedStyles.length > 0 && (
          <div className="mt-3">
            <div className="text-sm text-gray-600 mb-2">Selected styles:</div>
            <div className="flex flex-wrap gap-2">
              {selectedStyles.map((style, index) => (
                <Badge key={index} variant="secondary" className="flex items-center gap-1">
                  {style}
                  <X
                    className="h-3 w-3 cursor-pointer hover:text-red-500"
                    onClick={() => toggleItem(style, selectedStyles, setSelectedStyles)}
                  />
                </Badge>
              ))}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  )

  const renderPackingSection = () => (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Package className="h-5 w-5" />
          Packing Methods
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="text-sm text-gray-600 mb-2">Select your preferred packing methods:</div>
        <div className="grid grid-cols-1 gap-2">
          {availablePackingMethods.map((method) => {
            const isSelected = selectedPackingMethods.includes(method)
            return (
              <button
                key={method}
                type="button"
                onClick={() => toggleItem(method, selectedPackingMethods, setSelectedPackingMethods)}
                className={`flex items-center justify-between p-3 rounded-lg border transition-colors ${
                  isSelected
                    ? "bg-purple-50 border-purple-200 text-purple-800"
                    : "bg-gray-50 border-gray-200 text-gray-700 hover:bg-gray-100"
                }`}
              >
                <span className="font-medium text-sm">{method}</span>
                {isSelected && <Check className="h-4 w-4 text-purple-600" />}
              </button>
            )
          })}
        </div>
        {selectedPackingMethods.length > 0 && (
          <div className="mt-3">
            <div className="text-sm text-gray-600 mb-2">Selected methods:</div>
            <div className="flex flex-wrap gap-2">
              {selectedPackingMethods.map((method, index) => (
                <Badge key={index} variant="secondary" className="flex items-center gap-1">
                  {method}
                  <X
                    className="h-3 w-3 cursor-pointer hover:text-red-500"
                    onClick={() => toggleItem(method, selectedPackingMethods, setSelectedPackingMethods)}
                  />
                </Badge>
              ))}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  )

  const renderCurrencySection = () => (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <CreditCard className="h-5 w-5" />
          Currency Preferences
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="text-sm text-gray-600 mb-2">Select your preferred currencies:</div>
        <div className="grid grid-cols-5 gap-2">
          {supportedCurrencies.map((currency) => {
            const isSelected = selectedCurrencies.includes(currency)
            return (
              <button
                key={currency}
                type="button"
                onClick={() => toggleItem(currency, selectedCurrencies, setSelectedCurrencies)}
                className={`flex items-center justify-center p-2 rounded-lg border transition-colors text-xs font-medium ${
                  isSelected
                    ? "bg-purple-50 border-purple-200 text-purple-800"
                    : "bg-gray-50 border-gray-200 text-gray-700 hover:bg-gray-100"
                }`}
              >
                {currency}
              </button>
            )
          })}
        </div>
        {selectedCurrencies.length > 0 && (
          <div className="mt-3">
            <div className="text-sm text-gray-600 mb-2">Selected currencies ({selectedCurrencies.length}):</div>
            <div className="flex flex-wrap gap-2">
              {selectedCurrencies.map((currency, index) => (
                <Badge key={index} variant="secondary" className="flex items-center gap-1">
                  {currency}
                  <X
                    className="h-3 w-3 cursor-pointer hover:text-red-500"
                    onClick={() => toggleItem(currency, selectedCurrencies, setSelectedCurrencies)}
                  />
                </Badge>
              ))}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  )

  const renderNotificationsSection = () => (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Bell className="h-5 w-5" />
          Notifications
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <Label>Push Notifications</Label>
            <p className="text-sm text-gray-500">Receive notifications on your device</p>
          </div>
          <Switch defaultChecked />
        </div>
        <div className="flex items-center justify-between">
          <div>
            <Label>Email Updates</Label>
            <p className="text-sm text-gray-500">Get email updates about your account</p>
          </div>
          <Switch defaultChecked />
        </div>
        <div className="flex items-center justify-between">
          <div>
            <Label>Travel Reminders</Label>
            <p className="text-sm text-gray-500">Reminders about upcoming trips</p>
          </div>
          <Switch />
        </div>
      </CardContent>
    </Card>
  )

  const renderCurrentSection = () => {
    switch (activeSection) {
      case "profile":
        return renderProfileSection()
      case "style":
        return renderStyleSection()
      case "packing":
        return renderPackingSection()
      case "currency":
        return renderCurrencySection()
      case "notifications":
        return renderNotificationsSection()
      default:
        return renderProfileSection()
    }
  }

  return (
    <div className="flex flex-col h-full bg-[#F8F6FF]">
      <Header title="Settings" showBack onBack={onBack} />

      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {/* Section Navigation */}
        <Card>
          <CardContent className="p-2">
            <div className="grid grid-cols-3 gap-1">
              {settingSections.map((section) => {
                const Icon = section.icon
                return (
                  <Button
                    key={section.id}
                    variant={activeSection === section.id ? "default" : "ghost"}
                    size="sm"
                    onClick={() => setActiveSection(section.id)}
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

        {/* Current Section Content */}
        <form onSubmit={handleSubmit}>
          {renderCurrentSection()}

          {/* Save Button */}
          <Card>
            <CardContent className="p-4">
              {updateState?.error && <p className="text-red-500 text-sm mb-3">{updateState.error}</p>}
              {updateState?.success && <p className="text-green-500 text-sm mb-3">{updateState.message}</p>}
              <Button type="submit" className="w-full bg-purple-600 hover:bg-purple-700" disabled={isUpdating}>
                {isUpdating ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Saving...
                  </>
                ) : (
                  <>
                    <Save className="mr-2 h-4 w-4" />
                    Save Changes
                  </>
                )}
              </Button>
            </CardContent>
          </Card>
        </form>
      </div>
    </div>
  )
}
