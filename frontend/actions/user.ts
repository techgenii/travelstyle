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
      return { success: false, message: "", error: "No authentication token provided" }
    }

    console.log("Updating user profile with data via PUT /users/me:", updateData)

    // Make API call to update user profile (PUT /users/me)
    await fetchApiServer<UserOut>(
      "/users/me",
      {
        method: "PUT", // Changed from PATCH to PUT
        body: JSON.stringify(updateData),
      },
      token,
    )

    return {
      success: true,
      message: "Profile updated successfully!",
    }
  } catch (error: any) {
    console.error("Failed to update user profile:", error)
    return {
      success: false,
      message: "",
      error: error.message || "Failed to update profile. Please try again.",
    }
  }
}

// Removed updateUserPreferences as its functionality is now part of updateUserProfile
