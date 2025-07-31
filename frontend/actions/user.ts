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

interface UploadProfilePictureState {
  success: boolean
  message: string
  error?: string
  profilePictureUrl?: string
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

// New server action for uploading profile pictures
export async function uploadProfilePicture(
  token: string,
  prevState: UploadProfilePictureState,
  formData: FormData,
): Promise<UploadProfilePictureState> {
  try {
    if (!token) {
      return { success: false, message: "", error: "No authentication token provided" }
    }

    const file = formData.get("file") as File
    if (!file) {
      return { success: false, message: "", error: "No file provided" }
    }

    // Validate file type
    if (!file.type.startsWith("image/")) {
      return { success: false, message: "", error: "Please select an image file" }
    }

    // Validate file size (max 10MB)
    if (file.size > 10 * 1024 * 1024) {
      return { success: false, message: "", error: "File size must be less than 10MB" }
    }

    // Create a new FormData for the API call
    const apiFormData = new FormData()
    apiFormData.append("file", file)

    // Upload to backend which will handle Cloudinary upload
    const response = await fetchApiServer<{ profile_picture_url: string }>(
      "/users/me/profile-picture",
      {
        method: "POST",
        body: apiFormData,
        headers: {
          // Don't set Content-Type for FormData, let the browser set it with boundary
        },
      },
      token,
    )

    return {
      success: true,
      message: "Profile picture uploaded successfully!",
      profilePictureUrl: response.profile_picture_url,
    }
  } catch (error: any) {
    console.error("Failed to upload profile picture:", error)
    return {
      success: false,
      message: "",
      error: error.message || "Failed to upload profile picture. Please try again.",
    }
  }
}

// New server action for deleting profile pictures
export async function deleteProfilePicture(
  token: string,
  prevState: UploadProfilePictureState,
): Promise<UploadProfilePictureState> {
  try {
    if (!token) {
      return { success: false, message: "", error: "No authentication token provided" }
    }

    // Call backend to delete profile picture
    await fetchApiServer(
      "/users/me/profile-picture",
      {
        method: "DELETE",
      },
      token,
    )

    return {
      success: true,
      message: "Profile picture deleted successfully!",
      profilePictureUrl: null,
    }
  } catch (error: any) {
    console.error("Failed to delete profile picture:", error)
    return {
      success: false,
      message: "",
      error: error.message || "Failed to delete profile picture. Please try again.",
    }
  }
}

// Removed updateUserPreferences as its functionality is now part of updateUserProfile
