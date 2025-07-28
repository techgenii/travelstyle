// components/auth/signup-form.tsx
"use client"

import { useActionState } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { signup } from "@/actions/auth"
import Link from "next/link"
import { AuthFormWrapper } from "./auth-form-wrapper"
import { Chrome, Apple, Facebook } from "lucide-react" // Import social icons

export function SignupForm() {
  const [state, action, isPending] = useActionState(signup, { success: false, message: "" })

  return (
    <AuthFormWrapper title="Create your new account">
      <p className="text-sm text-gray-600 mb-6 text-center">Register to continue</p>
      <form action={action} className="space-y-4">
        <div>
          <Label htmlFor="email">Email</Label>
          <Input
            id="email"
            name="email"
            type="email"
            placeholder="Enter Email"
            required
            className="mt-1 bg-white border-gray-200 rounded-xl px-4 py-3 text-base focus:border-gray-300 focus:ring-0"
          />
        </div>
        <div>
          <Label htmlFor="username">Username</Label>
          <Input
            id="username"
            name="username" // Added username field
            type="text"
            placeholder="Enter Username"
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
            placeholder="Enter Password"
            required
            className="mt-1 bg-white border-gray-200 rounded-xl px-4 py-3 text-base focus:border-gray-300 focus:ring-0"
          />
        </div>
        <div className="flex items-center space-x-2 text-sm text-gray-600">
          {/* Placeholder for checkbox - actual checkbox component not included */}
          <input type="checkbox" id="terms" className="h-4 w-4 rounded border-gray-300 text-black focus:ring-black" />
          <label htmlFor="terms">
            I Agree with{" "}
            <Link href="#" className="font-medium text-gray-700 hover:underline">
              Terms of Service
            </Link>{" "}
            and{" "}
            <Link href="#" className="font-medium text-gray-700 hover:underline">
              Privacy Policy
            </Link>
          </label>
        </div>
        {state.message && (
          <p className={`text-sm ${state.success ? "text-green-600" : "text-red-600"}`}>{state.message}</p>
        )}
        <Button
          type="submit"
          className="w-full bg-black text-white rounded-xl px-4 py-3 hover:bg-gray-800 disabled:bg-gray-300"
          disabled={isPending}
        >
          {isPending ? "Continuing..." : "Continue"}
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
        Already have an account?{" "}
        <Link href="/login" className="font-medium text-gray-700 hover:underline">
          Sign In
        </Link>
      </div>
    </AuthFormWrapper>
  )
}
