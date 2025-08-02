"use client"

import type React from "react"
import { useState, useEffect, startTransition, useRef } from "react"
import { useActionState, useTransition } from "react"
import { updateUserProfile, updateProfilePictureUrl, getUserProfile } from "@/actions/user"
import { getAuthToken, setUserData, getUserData } from "@/lib/auth"
import type { UserOut } from "@/lib/types/api"
import type { UserData } from "@/lib/auth"

interface UseSettingsFormCloudinaryProps {
    user: UserData
    onUserUpdate?: (updatedUser: UserData) => void
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

    // Action specifically for profile picture updates
    const updateProfilePictureAction = async (prevState: any, profilePictureUrl: string) => {
        const token = getAuthToken()
        if (!token) {
            return { success: false, message: "", error: "No authentication token found" }
        }
        return updateProfilePictureUrl(token, prevState, profilePictureUrl)
    }

    const [updateState, formAction, isUpdating] = useActionState(updateProfileAndPreferencesAction, {
        success: false,
        message: "",
        error: "",
    })

    const [pictureUpdateState, pictureUpdateAction, isUpdatingPicture] = useActionState(updateProfilePictureAction, {
        success: false,
        message: "",
        error: "",
    })

    // Handle successful profile update
    useEffect(() => {
        console.log("Profile update effect triggered, updateState:", updateState)
        if (updateState?.success) {
            console.log("Profile update successful, updating local storage")
            // Update local storage user data with the new comprehensive preferences
            const currentUserData = getUserData()
            if (currentUserData) {
                const updatedUserData: UserData = {
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
                    // Ensure lastLogin is properly typed
                    lastLogin: currentUserData.lastLogin || undefined,
                    // Ensure isPremium is properly typed
                    isPremium: currentUserData.isPremium || undefined,
                }
                console.log("Setting updated user data:", updatedUserData)
                setUserData(updatedUserData)

                // Notify parent component with updated user data
                if (onUserUpdate) {
                    console.log("Calling onUserUpdate with updated data")
                    onUserUpdate(updatedUserData)
                }
            }
        }
    }, [updateState, firstName, lastName, email, defaultLocation, selectedStyles, selectedPackingMethods, selectedCurrencies, selectedTravelPatterns, sizeInfo, quickReplyPreferences, onUserUpdate])

    // Add ref to track if we've already processed a successful update
    const processedUpdateRef = useRef<string | null>(null)

    // Handle successful profile picture update
    useEffect(() => {
        console.log("Profile picture update effect triggered, pictureUpdateState:", pictureUpdateState)

        // Check if this is a new successful update we haven't processed yet
        const updateKey = `${pictureUpdateState?.success}-${pictureUpdateState?.message}`
        if (pictureUpdateState?.success && processedUpdateRef.current !== updateKey) {
            console.log("Profile picture update successful, updating local storage")
            processedUpdateRef.current = updateKey

            // Fetch the updated user data from the backend to get the new profile picture URL
            const fetchUpdatedUser = async () => {
                const token = getAuthToken()
                if (!token) {
                    console.error("No token available to fetch updated user data")
                    return
                }

                try {
                    const { user: updatedUser, error } = await getUserProfile(token)
                    if (error) {
                        console.error("Failed to fetch updated user data:", error)
                        return
                    }

                    if (updatedUser) {
                        // Convert UserOut to UserData format
                        const updatedUserData: UserData = {
                            id: updatedUser.id,
                            firstName: updatedUser.first_name,
                            lastName: updatedUser.last_name,
                            email: updatedUser.email,
                            profilePictureUrl: updatedUser.profile_picture_url,
                            profileCompleted: updatedUser.profile_completed || undefined,
                            stylePreferences: updatedUser.style_preferences || undefined,
                            sizeInfo: updatedUser.size_info || undefined,
                            travelPatterns: updatedUser.travel_patterns || undefined,
                            quickReplyPreferences: updatedUser.quick_reply_preferences || undefined,
                            packingMethods: updatedUser.packing_methods || undefined,
                            currencyPreferences: updatedUser.currency_preferences || undefined,
                            selectedStyleNames: updatedUser.selected_style_names || undefined,
                            defaultLocation: updatedUser.default_location,
                            maxBookmarks: updatedUser.max_bookmarks,
                            maxConversations: updatedUser.max_conversations,
                            subscriptionTier: updatedUser.subscription_tier,
                            subscriptionExpiresAt: updatedUser.subscription_expires_at,
                            isPremium: updatedUser.is_premium || undefined,
                            createdAt: updatedUser.created_at,
                            updatedAt: updatedUser.updated_at,
                            lastLogin: updatedUser.last_login,
                        }

                        console.log("Setting updated user data with new profile picture:", updatedUserData)
                        setUserData(updatedUserData)

                        // Notify parent component with updated user data
                        if (onUserUpdate) {
                            console.log("Calling onUserUpdate with updated profile picture data")
                            onUserUpdate(updatedUserData)
                        }
                    }
                } catch (error) {
                    console.error("Error fetching updated user data:", error)
                }
            }

            fetchUpdatedUser()
        }
    }, [pictureUpdateState?.success, pictureUpdateState?.message, onUserUpdate])

    // Reset the processed update ref when the component unmounts or user changes
    useEffect(() => {
        processedUpdateRef.current = null
    }, [user.id])

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

    // Handle profile picture update with Cloudinary URL
    const handlePictureUpdate = (imageUrl: string) => {
        console.log("handlePictureUpdate called with URL:", imageUrl)
        // Use the dedicated profile picture update action
        startTransition(() => {
            console.log("Calling pictureUpdateAction with URL:", imageUrl)
            console.log("Token available:", !!getAuthToken())
            pictureUpdateAction(imageUrl)
        })
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
        formAction,

        // Profile picture actions (Cloudinary approach)
        handlePictureUpdate,
        pictureUpdateState,
        isUpdatingPicture,
    }
}
