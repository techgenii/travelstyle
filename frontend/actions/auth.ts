// actions/auth.ts
"use server"

import { redirect } from "next/navigation"
import { fetchApiServer } from "@/lib/api-server"
import type { LoginRequest, RegisterRequest, ForgotPasswordRequest, MessageResponse } from "@/lib/types/api"

interface AuthState {
  success: boolean
  message: string
  error?: string
  authData?: {
    access_token: string
    refresh_token?: string
    user: any
  }
}

export async function login(prevState: AuthState, formData: FormData): Promise<AuthState> {
  console.log("[login] Starting login process")

  const email = formData.get("email") as string
  const password = formData.get("password") as string

  console.log(`[login] Email: ${email}`)
  console.log(`[login] Password length: ${password?.length || 0}`)

  if (!email || !password) {
    console.log("[login] Missing email or password")
    return { success: false, message: "", error: "Email and password are required." }
  }

  let response: any
  try {
    const requestBody: LoginRequest = { email, password }
    console.log("[login] Request body:", requestBody)

    console.log("[login] Calling fetchApiServer...")
    response = await fetchApiServer<any>("/auth/login", {
      method: "POST",
      body: JSON.stringify(requestBody),
    })

    console.log("[login] API call successful, response:", response)
  } catch (error: any) {
    console.error("[login] API call failed:", error)
    console.error("[login] Error stack:", error.stack)

    const errorMessage = error.message || "Login failed. An unexpected error occurred."
    return { success: false, message: "", error: errorMessage }
  }

  // Validate response structure
  if (!response.access_token || !response.user) {
    console.error("[login] Invalid response structure:", response)
    return { success: false, message: "", error: "Invalid response from server" }
  }

  console.log("[login] Login successful, returning auth data to client...")

  // Return the auth data to the client instead of trying to set it here
  return {
    success: true,
    message: "Login successful",
    authData: {
      access_token: response.access_token,
      refresh_token: response.refresh_token,
      user: response.user,
    },
  }
}

export async function signup(prevState: AuthState, formData: FormData): Promise<AuthState> {
  console.log("[signup] Starting signup process")

  const firstName = formData.get("firstName") as string
  const email = formData.get("email") as string
  const password = formData.get("password") as string

  console.log(`[signup] First Name: ${firstName}`)
  console.log(`[signup] Email: ${email}`)
  console.log(`[signup] Password length: ${password?.length || 0}`)

  if (!firstName || !email || !password) {
    console.log("[signup] Missing required fields")
    return { success: false, message: "", error: "All fields are required." }
  }

  let response: any
  try {
    const requestBody: RegisterRequest = { email, password, first_name: firstName, last_name: null }
    console.log("[signup] Request body:", requestBody)

    response = await fetchApiServer<any>("/auth/register", {
      method: "POST",
      body: JSON.stringify(requestBody),
    })

    console.log("[signup] API call successful, response:", response)
  } catch (error: any) {
    console.error("[signup] API call failed:", error)
    return { success: false, message: "", error: error.message || "Signup failed. Please try again." }
  }

  // Validate response structure
  if (!response.access_token || !response.user) {
    console.error("[signup] Invalid response structure:", response)
    return { success: false, message: "", error: "Invalid response from server" }
  }

  console.log("[signup] Signup successful, returning auth data to client...")

  // Return the auth data to the client instead of trying to set it here
  return {
    success: true,
    message: "Signup successful",
    authData: {
      access_token: response.access_token,
      refresh_token: response.refresh_token,
      user: response.user,
    },
  }
}

export async function forgotPassword(prevState: AuthState, formData: FormData): Promise<AuthState> {
  const email = formData.get("email") as string

  if (!email) {
    return { success: false, message: "", error: "Email is required." }
  }

  try {
    const requestBody: ForgotPasswordRequest = { email }
    const response = await fetchApiServer<MessageResponse>("/auth/forgot-password", {
      method: "POST",
      body: JSON.stringify(requestBody),
    })
    return { success: true, message: response.message }
  } catch (error: any) {
    console.error("Forgot password failed:", error)
    return { success: false, message: "", error: error.message || "Failed to send reset link. Please try again." }
  }
}

export async function logout(): Promise<AuthState> {
  try {
    // Get the refresh token from localStorage (only if available)
    let refreshToken: string | null = null
    let authToken: string | null = null
    if (typeof window !== 'undefined' && window.localStorage) {
      refreshToken = window.localStorage.getItem("travelstyle_refresh_token")
      authToken = window.localStorage.getItem("travelstyle_auth_token")
      console.log("[logout] Retrieved tokens:", {
        hasRefreshToken: !!refreshToken,
        hasAuthToken: !!authToken,
        authTokenLength: authToken?.length || 0
      })
    } else {
      console.log("[logout] localStorage not available")
    }

    // Call the logout endpoint to revoke tokens
    await fetchApiServer<MessageResponse>("/auth/logout", {
      method: "POST",
      body: JSON.stringify({ refresh_token: refreshToken }),
    }, authToken || undefined)

    return { success: true, message: "Logged out successfully" }
  } catch (error: any) {
    console.error("Logout failed:", error)
    // Even if the API call fails, we should still log out locally
    return { success: true, message: "Logged out successfully" }
  }
}
