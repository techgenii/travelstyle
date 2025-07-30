// actions/user.ts
"use server"

import { fetchApiServer } from "@/lib/api-server" // Use server API
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

export async function updateUserProfile(
  token: string,
  prevState: UpdateUserProfileState,
  formData: FormData,
): Promise<UpdateUserProfileState> {
  try {
    if (!token) {
      return { success: false, message: "", error: "No authentication token provided" }
    }

    // Extract form data
    const updateData: Partial<UserOut> = {
      first_name: formData.get("firstName") as string,
      last_name: formData.get("lastName") as string,
      email: formData.get("email") as string,
      profile_picture_url: formData.get("profilePictureUrl") as string,
    }

    // Parse JSON fields
    const jsonFields = [
      "stylePreferences",
      "sizeInfo",
      "travelPatterns",
      "quickReplyPreferences",
      "packingMethods",
      "currencyPreferences",
    ]

    jsonFields.forEach((field) => {
      const value = formData.get(field) as string
      if (value) {
        try {
          const snakeCaseField = field.replace(/([A-Z])/g, "_$1").toLowerCase()
          ;(updateData as any)[snakeCaseField] = JSON.parse(value)
        } catch (error) {
          console.warn(`Failed to parse ${field}:`, error)
        }
      }
    })

    // Handle selected style names
    const selectedStyleNames = formData.get("selectedStyleNames") as string
    if (selectedStyleNames) {
      try {
        updateData.selected_style_names = JSON.parse(selectedStyleNames)
      } catch (error) {
        console.warn("Failed to parse selectedStyleNames:", error)
      }
    }

    // Remove empty/null values
    Object.keys(updateData).forEach((key) => {
      if (updateData[key as keyof UserOut] === "" || updateData[key as keyof UserOut] === null) {
        delete updateData[key as keyof UserOut]
      }
    })

    console.log("Updating user profile with data:", updateData)

    // Make API call to update user profile
    const updatedUser = await fetchApiServer<UserOut>(
      "/users/me",
      {
        method: "PATCH",
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
