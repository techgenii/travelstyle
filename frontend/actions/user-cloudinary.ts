// actions/user-cloudinary.ts
"use server"

import { fetchApiServer } from "@/lib/api-server"

interface UpdateProfilePictureState {
    success: boolean
    message: string
    error?: string
}

// Simple action to update just the profile picture URL
export async function updateProfilePictureUrl(
    token: string,
    prevState: UpdateProfilePictureState,
    profilePictureUrl: string,
): Promise<UpdateProfilePictureState> {
    try {
        if (!token) {
            return { success: false, message: "", error: "No authentication token provided" }
        }

        console.log("Updating profile picture URL:", profilePictureUrl)

        // Make API call to update just the profile picture URL
        await fetchApiServer(
            "/users/me/profile-picture-url",
            {
                method: "PATCH",
                body: JSON.stringify({ profile_picture_url: profilePictureUrl }),
            },
            token,
        )

        return {
            success: true,
            message: "Profile picture updated successfully!",
        }
    } catch (error: any) {
        console.error("Failed to update profile picture URL:", error)
        return {
            success: false,
            message: "",
            error: error.message || "Failed to update profile picture. Please try again.",
        }
    }
}
