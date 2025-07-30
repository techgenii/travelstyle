"use client"

import { useActionState, useEffect } from "react"
import { login } from "@/actions/auth"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import Link from "next/link"
import { cn } from "@/lib/utils"
import { setAuthToken, setUserData, redirectToHome } from "@/lib/auth"

export function LoginForm() {
  const [state, formAction, isPending] = useActionState(login, {
    success: false,
    message: "",
    error: "",
  })

  console.log("[LoginForm] Current state:", state)
  console.log("[LoginForm] Is pending:", isPending)

  // Handle successful login on the client side
  useEffect(() => {
    if (state?.success && state?.authData) {
      console.log("[LoginForm] Login successful, setting auth data...")

      try {
        // Set auth token
        setAuthToken(state.authData.access_token)

        // Set user data
        setUserData({
          id: state.authData.user.id,
          firstName: state.authData.user.first_name,
          lastName: state.authData.user.last_name,
          email: state.authData.user.email,
          profilePictureUrl: state.authData.user.profile_picture_url,
          profileCompleted: state.authData.user.profile_completed,
          stylePreferences: state.authData.user.style_preferences,
          sizeInfo: state.authData.user.size_info,
          travelPatterns: state.authData.user.travel_patterns,
          quickReplyPreferences: state.authData.user.quick_reply_preferences,
          packingMethods: state.authData.user.packing_methods,
          currencyPreferences: state.authData.user.currency_preferences,
          selectedStyleNames: state.authData.user.selected_style_names || [],
          createdAt: state.authData.user.created_at,
          updatedAt: state.authData.user.updated_at,
          lastLogin: state.authData.user.last_login,
        })

        console.log("[LoginForm] Auth data set successfully, redirecting...")
        redirectToHome()
      } catch (error) {
        console.error("[LoginForm] Failed to set auth data:", error)
      }
    }
  }, [state])

  return (
    <form action={formAction} className="space-y-6">
      <div className="space-y-2">
        <Label htmlFor="email">Email</Label>
        <Input id="email" name="email" type="email" placeholder="m@example.com" required disabled={isPending} />
      </div>
      <div className="space-y-2">
        <div className="flex items-center justify-between">
          <Label htmlFor="password">Password</Label>
          <Link href="/forgot-password" className="text-sm font-medium text-purple-600 hover:underline">
            Forgot password?
          </Link>
        </div>
        <Input id="password" name="password" type="password" required disabled={isPending} />
      </div>
      {state?.error && <p className="text-red-500 text-sm">{state.error}</p>}
      {state?.success && !state?.authData && <p className="text-green-500 text-sm">{state.message}</p>}
      <Button
        type="submit"
        className={cn(
          "w-full bg-purple-600 hover:bg-purple-700 text-white",
          isPending && "opacity-70 cursor-not-allowed",
        )}
        disabled={isPending}
      >
        {isPending ? "Signing In..." : "Sign In"}
      </Button>
    </form>
  )
}
