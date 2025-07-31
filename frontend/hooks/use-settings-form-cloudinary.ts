"use client"

import type React from "react"
import { useState, useEffect, startTransition } from "react"
import { useActionState } from "react"
import { updateUserProfile, deleteProfilePicture } from "@/actions/user"
import { updateProfilePictureUrl } from "@/actions/user-cloudinary"
import { getAuthToken, setUserData, getUserData } from "@/lib/auth"
import type { UserOut } from "@/lib/types/api"

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

interface UseSettingsFormCloudinaryProps {
    user: User
    onUserUpdate?: (updatedUser: User) => void
}

export function useSettingsFormCloudinary({ user, onUserUpdate }: UseSettingsFormCloudinaryProps) {
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

    // Action for profile picture deletion
    const deleteProfilePictureAction = async (prevState: any) => {
        const token = getAuthToken()
        if (!token) {
            return { success: false, message: "", error: "No authentication token found" }
        }
        return deleteProfilePicture(token, prevState)
    }

    const [updateState, formAction, isUpdating] = useActionState(updateProfileAndPreferencesAction, {
        success: false,
        message: "",
        error: "",
    })

    const [deleteState, deleteAction, isDeleting] = useActionState(deleteProfilePictureAction, {
        success: false,
        message: "",
        error: "",
    })

    // Action for simple profile picture URL update
    const updateProfilePictureUrlAction = async (prevState: any, profilePictureUrl: string) => {
        const token = getAuthToken()
        if (!token) {
            return { success: false, message: "", error: "No authentication token found" }
        }
        return updateProfilePictureUrl(token, prevState, profilePictureUrl)
    }

    const [pictureUrlState, pictureUrlAction, isUpdatingPicture] = useActionState(updateProfilePictureUrlAction, {
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

    // Handle successful profile picture URL update
    useEffect(() => {
        if (pictureUrlState?.success) {
            // Update local storage user data with the new profile picture URL
            const currentUserData = getUserData()
            if (currentUserData) {
                console.log("Profile picture URL updated successfully, updating local storage")
                // Notify parent component to refresh user data
                if (onUserUpdate) {
                    // We need to get the updated profile picture URL
                    // For now, we'll trigger a refresh by calling the callback
                    onUserUpdate(user)
                }
            }
        }
    }, [pictureUrlState, onUserUpdate, user])

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault()
        const token = getAuthToken()
        if (!token) {
            console.error("No authentication token found for submission.")
            return
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
        }

        // Call the form action within a transition
        startTransition(() => {
            formAction(comprehensivePayload)
        })
    }

    // Handle profile picture update with Cloudinary URL
    const handlePictureUpdate = (imageUrl: string) => {
        startTransition(() => {
            pictureUrlAction(imageUrl)
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
        updateState,
        isUpdating,

        // Profile picture actions (Cloudinary approach)
        handlePictureUpdate,
        deleteAction,
        deleteState,
        isDeleting,
        pictureUrlState,
        isUpdatingPicture,
    }
}
