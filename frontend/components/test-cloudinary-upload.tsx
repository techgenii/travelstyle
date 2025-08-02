"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { ProfilePictureUploadCloudinary } from "./profile-picture-upload-cloudinary"
import { useSettingsFormCloudinary } from "@/hooks/use-settings-form-cloudinary"

interface TestUser {
    id: string
    firstName: string
    lastName?: string | null
    email: string
    profilePictureUrl?: string | null
}

export function TestCloudinaryUpload() {
    const testUser: TestUser = {
        id: "test-user",
        firstName: "Jane",
        lastName: "Doe",
        email: "test@example.com",
        profilePictureUrl: null
    }

    const {
        handlePictureUpdate,
        updateState,
        isUpdating,
    } = useSettingsFormCloudinary({ user: testUser })

    return (
        <div className="p-8 max-w-md mx-auto">
            <h2 className="text-2xl font-bold mb-4">Test Cloudinary Upload</h2>

            <ProfilePictureUploadCloudinary
                currentPictureUrl={testUser.profilePictureUrl}
                firstName={testUser.firstName}
                lastName={testUser.lastName}
                onPictureUpdate={handlePictureUpdate}
                onPictureDelete={() => {
                    // Handle deletion through main profile update
                    const comprehensivePayload: any = {
                        profile_picture_url: null,
                    }
                    // Note: This would need formAction which isn't available in this test component
                }}
                isUpdating={isUpdating}
                isDeleting={isUpdating}
            />

            {updateState?.error && (
                <div className="mt-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded">
                    Error: {updateState.error}
                </div>
            )}

            {updateState?.success && (
                <div className="mt-4 p-3 bg-green-100 border border-green-400 text-green-700 rounded">
                    Success: {updateState.message}
                </div>
            )}

            <div className="mt-4 text-sm text-gray-600">
                <p>Status: {isUpdating ? 'Updating...' : 'Ready'}</p>
                <p>State: {JSON.stringify(updateState)}</p>
            </div>
        </div>
    )
}
