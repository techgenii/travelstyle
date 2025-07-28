"use client"

import { useActionState } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { login } from "@/lib/auth"
import Link from "next/link"
import { AuthFormWrapper } from "./auth-form-wrapper"
import { Chrome, Apple, Facebook } from "lucide-react" // Import social icons

export function LoginForm() {
  const [state, action, isPending] = useActionState(login, { success: false, message: "" })

  return (
    <AuthFormWrapper title="Hello, Login now">
      <p className="text-sm text-gray-600 mb-6 text-center">Login to your account</p>
      <form action={action} className="space-y-4">
        <div>
          <Label htmlFor="email">Username</Label> {/* Changed to Username as per screenshot */}
          <Input
            id="email"
            name="email"
            type="email"
            placeholder="Enter Username" // Changed placeholder
            required
            className="mt-1 bg-white border-gray-200 rounded-xl px-4 py-3 text-base focus:border-gray-300 focus:ring-0"
          />
        </div>
        <div>
          <Label htmlFor="password">Password</Label>
          <Input
            id="password"
            name="password"
            type="password"
            placeholder="Enter Password" // Changed placeholder
            required
            className="mt-1 bg-white border-gray-200 rounded-xl px-4 py-3 text-base focus:border-gray-300 focus:ring-0"
          />
        </div>
        <div className="text-right text-sm">
          <Link href="/forgot-password" className="font-medium text-gray-700 hover:underline">
            Forgot Password?
          </Link>
        </div>
        {state.message && (
          <p className={`text-sm ${state.success ? "text-green-600" : "text-red-600"}`}>{state.message}</p>
        )}
        <Button
          type="submit"
          className="w-full bg-black text-white rounded-xl px-4 py-3 hover:bg-gray-800 disabled:bg-gray-300"
          disabled={isPending}
        >
          {isPending ? "Signing In..." : "Sign In"}
        </Button>
      </form>

      <div className="relative my-6">
        <div className="absolute inset-0 flex items-center">
          <span className="w-full border-t border-gray-200" />
        </div>
        <div className="relative flex justify-center text-xs uppercase">
          <span className="bg-white px-2 text-gray-500">Or</span>
        </div>
      </div>

      <div className="space-y-3">
        <Button
          variant="outline"
          className="w-full bg-white border-gray-200 text-gray-700 rounded-xl py-3 hover:bg-gray-50"
        >
          <Chrome className="mr-2 h-4 w-4" />
          Continue with Google
        </Button>
        <Button
          variant="outline"
          className="w-full bg-white border-gray-200 text-gray-700 rounded-xl py-3 hover:bg-gray-50"
        >
          <Apple className="mr-2 h-4 w-4" />
          Continue with Apple
        </Button>
        <Button
          variant="outline"
          className="w-full bg-white border-gray-200 text-gray-700 rounded-xl py-3 hover:bg-gray-50"
        >
          <Facebook className="mr-2 h-4 w-4" />
          Continue with Facebook
        </Button>
      </div>

      <div className="mt-6 text-center text-sm text-gray-600">
        Don't have an account?{" "}
        <Link href="/signup" className="font-medium text-gray-700 hover:underline">
          Create account
        </Link>
      </div>
    </AuthFormWrapper>
  )
}
