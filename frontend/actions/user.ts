// actions/user.ts
"use server"

import { fetchApiServer } from "@/lib/api-server"
import type { UserOut } from "@/lib/types/api"

interface UserProfileState {
  user: UserOut | null
  error?: string
}

interface UpdateUserProfileState {
  success: boolean
  message: string
  error?: string
}

interface UpdateProfilePictureState {
  success: boolean
  message: string
  error?: string
}

export async function getUserProfile(token?: string): Promise<UserProfileState> {
  try {
    if (!token) {
      return { user: null, error: "No authentication token provided" }
    }

    const user = await fetchApiServer<UserOut>("/users/me", { method: "GET" }, token)
    return { user }
  } catch (error: any) {
    console.error("Failed to fetch user profile:", error)
    return { user: null, error: error.message || "Failed to load user profile." }
  }
}

// Modified to use PUT /users/me for comprehensive profile updates
export async function updateUserProfile(
  token: string,
  prevState: UpdateUserProfileState,
  // This action now expects a Partial<UserOut> containing all fields to be updated
  // The client (useSettingsForm) will construct this comprehensive payload.
  updateData: Partial<UserOut>,
): Promise<UpdateUserProfileState> {
  try {
    if (!token) {
      console.log("No token provided for profile update")
      return { success: false, message: "", error: "No authentication token provided" }
    }

    console.log("Updating user profile with data via PUT /users/me:", updateData)
    console.log("Token available:", !!token)

    // Make API call to update user profile (PUT /users/me)
    const response = await fetchApiServer<UserOut>(
      "/users/me",
      {
        method: "PUT", // Changed from PATCH to PUT
        body: JSON.stringify(updateData),
      },
      token,
    )

    console.log("Profile update response:", response)
    return {
      success: true,
      message: "Profile updated successfully!",
    }
  } catch (error: any) {
    console.error("Failed to update user profile:", error)
    console.error("Error details:", {
      message: error.message,
      stack: error.stack,
      name: error.name
    })
    return {
      success: false,
      message: "",
      error: error.message || "Failed to update profile. Please try again.",
    }
  }
}

// New action specifically for updating profile picture URL
export async function updateProfilePictureUrl(
  token: string,
  prevState: UpdateProfilePictureState,
  profilePictureUrl: string,
): Promise<UpdateProfilePictureState> {
  try {
    if (!token) {
      console.log("No token provided for profile picture update")
      return { success: false, message: "", error: "No authentication token provided" }
    }

    console.log("Updating profile picture URL via PATCH /me/profile-picture-url:", profilePictureUrl)
    console.log("Token available:", !!token)

    // Make API call to update profile picture URL (PATCH /me/profile-picture-url)
    const response = await fetchApiServer<{ message: string }>(
      "/users/me/profile-picture-url",
      {
        method: "PATCH",
        body: JSON.stringify({ profile_picture_url: profilePictureUrl }),
      },
      token,
    )

    console.log("Profile picture update response:", response)
    return {
      success: true,
      message: "Profile picture updated successfully!",
    }
  } catch (error: any) {
    console.error("Failed to update profile picture:", error)
    console.error("Error details:", {
      message: error.message,
      stack: error.stack,
      name: error.name
    })
    return {
      success: false,
      message: "",
      error: error.message || "Failed to update profile picture. Please try again.",
    }
  }
}

// Removed updateUserPreferences as its functionality is now part of updateUserProfile
