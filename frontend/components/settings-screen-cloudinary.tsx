"use client"

import { Header } from "./header"
import { Card, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Save, Loader2 } from "lucide-react"
import { useSettingsFormCloudinary } from "@/hooks/use-settings-form-cloudinary"
import { useSettingsNavigation } from "@/hooks/use-settings-navigation"
import { SettingsNavigation } from "./settings/settings-navigation"
import { ProfileSection } from "./settings/profile-section"
import { StyleSection } from "./settings/style-section"
import { PackingSection } from "./settings/packing-section"
import { CurrencySection } from "./settings/currency-section"
import { TravelPatternsSection } from "./settings/travel-patterns-section"
import { SizeInfoSection } from "./settings/size-info-section"
import { QuickReplySection } from "./settings/quick-reply-section"
import { NotificationsSection } from "./settings/notifications-section"
import { ProfilePictureUploadCloudinary } from "./profile-picture-upload-cloudinary"
import type React from "react"
import { useState, useEffect, startTransition } from "react"
import { useActionState } from "react"
import { updateUserProfile } from "@/actions/user"
import { getAuthToken, setUserData, getUserData } from "@/lib/auth"
import type { UserOut } from "@/lib/types/api"
import type { UserData } from "@/lib/auth"

interface SettingsScreenCloudinaryProps {
    onBack: () => void
    user: UserData
    onUserUpdate?: (updatedUser: UserData) => void
}

export function SettingsScreenCloudinary({ onBack, user, onUserUpdate }: SettingsScreenCloudinaryProps) {
    const { activeSection, setActiveSection, settingSections } = useSettingsNavigation()

    // Convert UserData to the expected type for ProfileSection
    const profileUser = {
        id: user.id,
        firstName: user.firstName,
        lastName: user.lastName,
        email: user.email,
        profilePictureUrl: user.profilePictureUrl,
        profileCompleted: user.profileCompleted,
        createdAt: user.createdAt,
        updatedAt: user.updatedAt,
        lastLogin: user.lastLogin || undefined,
        isPremium: user.isPremium || undefined,
        defaultLocation: user.defaultLocation,
        maxBookmarks: user.maxBookmarks,
        maxConversations: user.maxConversations,
        subscriptionTier: user.subscriptionTier,
        subscriptionExpiresAt: user.subscriptionExpiresAt,
    }

    const {
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
        handleSubmit,
        toggleItem,
        updateState,
        isUpdating,
        handlePictureUpdate,
        formAction,
        isUpdatingPicture,
    } = useSettingsFormCloudinary({ user, onUserUpdate })

    const renderCurrentSection = () => {
        switch (activeSection) {
            case "profile":
                return (
                    <ProfileSection
                        user={profileUser}
                        firstName={firstName}
                        setFirstName={setFirstName}
                        lastName={lastName}
                        setLastName={setLastName}
                        email={email}
                        setEmail={setEmail}
                        defaultLocation={defaultLocation}
                        setDefaultLocation={setDefaultLocation}
                        // Use the new Cloudinary component
                        profilePictureComponent={
                            <ProfilePictureUploadCloudinary
                                currentPictureUrl={user.profilePictureUrl}
                                onPictureUpdate={handlePictureUpdate}
                                onPictureDelete={() => {
                                    // Handle deletion through main profile update
                                    const comprehensivePayload: Partial<UserOut> = {
                                        profile_picture_url: null,
                                    }
                                    formAction(comprehensivePayload)
                                }}
                                isUpdating={isUpdating}
                                isUpdatingPicture={isUpdatingPicture}
                                isDeleting={false}
                            />
                        }
                    />
                )
            case "style":
                return (
                    <StyleSection
                        selectedStyles={selectedStyles}
                        onToggleStyle={(style) => toggleItem(style, selectedStyles, setSelectedStyles)}
                    />
                )
            case "packing":
                return (
                    <PackingSection
                        selectedPackingMethods={selectedPackingMethods}
                        onTogglePackingMethod={(method) => toggleItem(method, selectedPackingMethods, setSelectedPackingMethods)}
                    />
                )
            case "currency":
                return (
                    <CurrencySection
                        selectedCurrencies={selectedCurrencies}
                        onToggleCurrency={(currency) => toggleItem(currency, selectedCurrencies, setSelectedCurrencies)}
                    />
                )
            case "travel-patterns":
                return (
                    <TravelPatternsSection
                        selectedTravelPatterns={selectedTravelPatterns}
                        onToggleTravelPattern={(pattern) => toggleItem(pattern, selectedTravelPatterns, setSelectedTravelPatterns)}
                    />
                )
            case "size-info":
                return <SizeInfoSection sizeInfo={sizeInfo} onSizeInfoChange={handleSizeInfoChange} />
            case "quick-reply":
                return (
                    <QuickReplySection
                        quickReplyPreferences={quickReplyPreferences}
                        onToggleQuickReplies={handleToggleQuickReplies}
                    />
                )
            case "notifications":
                return <NotificationsSection />
            default:
                console.warn(`[SettingsScreen] Unknown section: ${activeSection}, falling back to profile`)
                return (
                    <ProfileSection
                        user={profileUser}
                        firstName={firstName}
                        setFirstName={setFirstName}
                        lastName={lastName}
                        setLastName={setLastName}
                        email={email}
                        setEmail={setEmail}
                        defaultLocation={defaultLocation}
                        setDefaultLocation={setDefaultLocation}
                        profilePictureComponent={
                            <ProfilePictureUploadCloudinary
                                currentPictureUrl={user.profilePictureUrl}
                                onPictureUpdate={handlePictureUpdate}
                                onPictureDelete={() => {
                                    // Handle deletion through main profile update
                                    const comprehensivePayload: Partial<UserOut> = {
                                        profile_picture_url: null,
                                    }
                                    formAction(comprehensivePayload)
                                }}
                                isUpdating={isUpdating}
                                isUpdatingPicture={isUpdatingPicture}
                                isDeleting={false}
                            />
                        }
                    />
                )
        }
    }

    return (
        <div className="flex flex-col h-full bg-[#F8F6FF]">
            <Header title="Settings" showBack onBack={onBack} />

            <div className="flex-1 overflow-y-auto p-4 space-y-4">
                <SettingsNavigation
                    activeSection={activeSection}
                    onSectionChange={setActiveSection}
                    sections={settingSections}
                />

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
