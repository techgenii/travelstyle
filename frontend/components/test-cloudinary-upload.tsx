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
        deleteAction,
        isDeleting,
        pictureUrlState,
        isUpdatingPicture,
    } = useSettingsFormCloudinary(testUser)

    return (
        <div className="p-8 max-w-md mx-auto">
            <h2 className="text-2xl font-bold mb-4">Test Cloudinary Upload</h2>

            <ProfilePictureUploadCloudinary
                currentPictureUrl={testUser.profilePictureUrl}
                firstName={testUser.firstName}
                lastName={testUser.lastName}
                onPictureUpdate={handlePictureUpdate}
                onPictureDelete={deleteAction}
                isDeleting={isDeleting}
                isUpdatingPicture={isUpdatingPicture}
            />

            {pictureUrlState?.error && (
                <div className="mt-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded">
                    Error: {pictureUrlState.error}
                </div>
            )}

            {pictureUrlState?.success && (
                <div className="mt-4 p-3 bg-green-100 border border-green-400 text-green-700 rounded">
                    Success: {pictureUrlState.message}
                </div>
            )}

            <div className="mt-4 text-sm text-gray-600">
                <p>Status: {isUpdatingPicture ? 'Updating...' : 'Ready'}</p>
                <p>State: {JSON.stringify(pictureUrlState)}</p>
            </div>
        </div>
    )
}
