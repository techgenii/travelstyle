"use server"

import { redirect } from "next/navigation"
import { setAuthToken, removeAuthToken } from "@/lib/auth"
import { fetchApi } from "@/lib/api"

interface AuthState {
  success: boolean
  message: string
  errors?: Record<string, string[]>
}

export async function login(prevState: AuthState, formData: FormData): Promise<AuthState> {
  const email = formData.get("email") as string
  const password = formData.get("password") as string

  if (!email || !password) {
    return { success: false, message: "Email and password are required." }
  }

  // --- SIMULATION START ---
  // This section simulates a successful login for demonstration purposes.
  // In a real application, you would remove this and rely on the actual API call.
  console.log("Simulating login for:", email)
  setAuthToken("mock_jwt_token_for_demonstration") // Set a dummy token
  redirect("/") // Redirect to home immediately
  // --- SIMULATION END ---

  // The code below would be active when the backend is fully integrated
  /*
  try {
    // Assuming your FastAPI login endpoint returns a token
    const response = await fetchApi<{ access_token: string; token_type: string }>("/users/login", {
      method: "POST",
      headers: {
        "Content-Type": "application/x-www-form-urlencoded", // FastAPI-Users default for login
      },
      body: new URLSearchParams({
        username: email, // FastAPI-Users often uses 'username' for email in login
        password: password,
      }).toString(),
    })

    // Call client-side function to store token
    setAuthToken(response.access_token)

    redirect("/") // Redirect to home on success
  } catch (error: any) {
    console.error("Login failed:", error)
    return { success: false, message: error.message || "Login failed. Please check your credentials." }
  }
  */
}

export async function signup(prevState: AuthState, formData: FormData): Promise<AuthState> {
  const email = formData.get("email") as string
  const password = formData.get("password") as string

  if (!email || !password) {
    return { success: false, message: "Email and password are required." }
  }

  try {
    // Assuming your FastAPI register endpoint
    await fetchApi("/users/register", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    })

    // Optionally, auto-login after signup
    const loginResponse = await fetchApi<{ access_token: string; token_type: string }>("/users/login", {
      method: "POST",
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
      },
      body: new URLSearchParams({
        username: email,
        password: password,
      }).toString(),
    })

    setAuthToken(loginResponse.access_token)

    redirect("/") // Redirect to home on success
  } catch (error: any) {
    console.error("Signup failed:", error)
    return { success: false, message: error.message || "Signup failed. Please try again." }
  }
}

export async function forgotPassword(prevState: AuthState, formData: FormData): Promise<AuthState> {
  const email = formData.get("email") as string

  if (!email) {
    return { success: false, message: "Email is required." }
  }

  try {
    // Assuming your FastAPI forgot password endpoint
    await fetchApi("/users/forgot-password", {
      method: "POST",
      body: JSON.stringify({ email }),
    })

    return { success: true, message: "If an account with that email exists, a password reset link has been sent." }
  } catch (error: any) {
    console.error("Forgot password failed:", error)
    return { success: false, message: error.message || "Failed to send reset link. Please try again." }
  }
}

export async function logout(): Promise<void> {
  removeAuthToken()
  redirect("/login")
}
