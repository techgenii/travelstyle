"use client"

import type React from "react"

import { useState, useEffect, startTransition } from "react"
import { useActionState } from "react"
import { updateUserProfile } from "@/actions/user" // Only import updateUserProfile
import { getAuthToken, setUserData, getUserData } from "@/lib/auth"
import type { UserOut } from "@/lib/types/api" // Import UserOut for the payload type

interface User {
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
  defaultLocation?: string | null
  createdAt?: string
  updatedAt?: string
  lastLogin?: string
  isPremium?: boolean
}

export function useSettingsForm(user: User) {
  // General profile fields
  const [firstName, setFirstName] = useState(user.firstName || "")
  const [lastName, setLastName] = useState(user.lastName || "")
  const [email, setEmail] = useState(user.email || "")
  const [defaultLocation, setDefaultLocation] = useState(user.defaultLocation || "")

  // Preference fields - transform nested structures to flat arrays
  const [selectedStyles, setSelectedStyles] = useState<string[]>(
    user.selectedStyleNames || user.stylePreferences?.selected_styles || []
  )
  const [selectedPackingMethods, setSelectedPackingMethods] = useState<string[]>(
    user.packingMethods?.selected_methods || []
  )
  const [selectedCurrencies, setSelectedCurrencies] = useState<string[]>(
    user.currencyPreferences?.preferred_currencies || []
  )
  const [selectedTravelPatterns, setSelectedTravelPatterns] = useState<string[]>(
    user.travelPatterns?.selected_patterns || []
  )
  const [sizeInfo, setSizeInfo] = useState<Record<string, any>>(user.sizeInfo || {})
  const [quickReplyPreferences, setQuickReplyPreferences] = useState<Record<string, any>>(
    user.quickReplyPreferences || { enabled: true },
  )

  // Action for comprehensive profile updates
  const updateProfileAndPreferencesAction = async (prevState: any, payload: Partial<UserOut>) => {
    const token = getAuthToken()
    if (!token) {
      return { success: false, message: "", error: "No authentication token found" }
    }
    return updateUserProfile(token, prevState, payload)
  }

  const [updateState, formAction, isUpdating] = useActionState(updateProfileAndPreferencesAction, {
    success: false,
    message: "",
    error: "",
  })

  // Handle successful profile update
  useEffect(() => {
    if (updateState?.success) {
      // Update local storage user data with the new comprehensive preferences
      const currentUserData = getUserData()
      if (currentUserData) {
        setUserData({
          ...currentUserData,
          firstName,
          lastName,
          email,
          defaultLocation,
          selectedStyleNames: selectedStyles,
          packingMethods: { selected_methods: selectedPackingMethods },
          currencyPreferences: { preferred_currencies: selectedCurrencies },
          travelPatterns: { selected_patterns: selectedTravelPatterns },
          sizeInfo: sizeInfo,
          quickReplyPreferences: quickReplyPreferences,
        })
      }
    }
  }, [updateState, firstName, lastName, email, defaultLocation, selectedStyles, selectedPackingMethods, selectedCurrencies, selectedTravelPatterns, sizeInfo, quickReplyPreferences])

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    const token = getAuthToken()
    if (!token) {
      console.error("No authentication token found for submission.")
      return // Or set an error state
    }

    // Construct the comprehensive payload for PUT /users/me
    const comprehensivePayload: Partial<UserOut> = {
      // General profile fields
      first_name: firstName,
      last_name: lastName,
      email: email,
      profile_picture_url: user.profilePictureUrl, // Keep existing if not changed via form
      default_location: defaultLocation,

      // Preference fields (ensure they match backend's expected structure for UserOut)
      style_preferences: { selected_styles: selectedStyles },
      packing_methods: { selected_methods: selectedPackingMethods },
      currency_preferences: { preferred_currencies: selectedCurrencies },
      travel_patterns: { selected_patterns: selectedTravelPatterns },
      size_info: sizeInfo,
      quick_reply_preferences: quickReplyPreferences,

      // Include other necessary fields from the original user object that are not being edited
      // This is crucial for PUT, as it replaces the entire resource.
      // Only include if they are part of the UserOut schema and required by the PUT endpoint.
      // For simplicity, we'll assume the backend handles merging or that these are the only fields sent.
      // If the backend strictly requires ALL fields, you'd merge with `user` object.
      // For now, we'll send only the fields we manage in the form.
      // If the API requires all fields, you'd do:
      // ...user, // Spread existing user data
      // first_name: firstName,
      // ...
    }

    // Remove empty/null values from the payload if the backend expects it for PUT
    // (though for PUT, it often expects all fields, even if null/empty)
    Object.keys(comprehensivePayload).forEach((key) => {
      const value = comprehensivePayload[key as keyof typeof comprehensivePayload]
      if (value === "" || value === null || (Array.isArray(value) && value.length === 0)) {
        // Optionally remove empty strings, nulls, or empty arrays
        // delete comprehensivePayload[key as keyof typeof comprehensivePayload];
      }
    })

    // Call the form action within a transition
    startTransition(() => {
      formAction(comprehensivePayload)
    })
  }

  const toggleItem = (item: string, currentList: string[], setList: (list: string[]) => void) => {
    if (currentList.includes(item)) {
      setList(currentList.filter((i) => i !== item))
    } else {
      setList([...currentList, item])
    }
  }

  const handleSizeInfoChange = (key: keyof typeof sizeInfo, value: string) => {
    setSizeInfo((prev) => ({ ...prev, [key]: value }))
  }

  const handleToggleQuickReplies = (enabled: boolean) => {
    setQuickReplyPreferences((prev) => ({ ...prev, enabled }))
  }

  return {
    // Form state
    firstName,
    setFirstName,
    lastName,
    setLastName,
    email,
    setEmail,
    defaultLocation,
    setDefaultLocation,
    selectedStyles,
    setSelectedStyles,
    selectedPackingMethods,
    setSelectedPackingMethods,
    selectedCurrencies,
    setSelectedCurrencies,
    selectedTravelPatterns,
    setSelectedTravelPatterns,
    sizeInfo,
    handleSizeInfoChange,
    quickReplyPreferences,
    handleToggleQuickReplies,

    // Form actions
    handleSubmit,
    toggleItem,
    updateState, // This now reflects the single action's state
    isUpdating, // This now reflects the single action's pending status
  }
}
