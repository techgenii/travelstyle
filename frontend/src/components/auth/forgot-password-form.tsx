"use client"

import { useActionState } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { forgotPassword } from "@/lib/auth"
import Link from "next/link"
import { AuthFormWrapper } from "./auth-form-wrapper" // Corrected import

export function ForgotPasswordForm() {
  const [state, action, isPending] = useActionState(forgotPassword, { success: false, message: "" })

  return (
    <AuthFormWrapper title="Forgot Password">
      <form action={action} className="space-y-6">
        <p className="text-sm text-gray-600 text-center">
          Enter your email address and we'll send you a link to reset your password.
        </p>
        <div>
          <Label htmlFor="email">Email</Label>
          <Input
            id="email"
            name="email"
            type="email"
            placeholder="you@example.com"
            required
            className="mt-1 bg-white border-gray-200 rounded-xl px-4 py-3 text-base focus:border-gray-300 focus:ring-0"
          />
        </div>
        {state.message && (
          <p className={`text-sm ${state.success ? "text-green-600" : "text-red-600"}`}>{state.message}</p>
        )}
        <Button
          type="submit"
          className="w-full bg-black text-white rounded-xl px-4 py-3 hover:bg-gray-800 disabled:bg-gray-300"
          disabled={isPending}
        >
          {isPending ? "Sending..." : "Send Reset Link"}
        </Button>
        <div className="text-center text-sm text-gray-600">
          <Link href="/login" className="font-medium text-gray-700 hover:underline">
            Back to Login
          </Link>
        </div>
      </form>
    </AuthFormWrapper>
  )
}
