"use client"

import { useActionState } from "react"
import { forgotPassword } from "@/actions/auth"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import Link from "next/link"
import { cn } from "@/lib/utils"

export function ForgotPasswordForm() {
  const [state, formAction, isPending] = useActionState(forgotPassword, {
    success: false,
    message: "",
    error: "",
  })

  return (
    <form action={formAction} className="space-y-6">
      <div className="space-y-2">
        <Label htmlFor="email">Email</Label>
        <Input id="email" name="email" type="email" placeholder="m@example.com" required disabled={isPending} />
      </div>
      {state?.error && <p className="text-red-500 text-sm">{state.error}</p>}
      {state?.success && <p className="text-green-500 text-sm">{state.message}</p>}
      <Button type="submit" className={cn("w-full", isPending && "opacity-70 cursor-not-allowed")} disabled={isPending}>
        {isPending ? "Sending..." : "Send Reset Link"}
      </Button>
      <div className="text-center text-sm text-gray-600">
        Remember your password?{" "}
        <Link href="/login" className="font-medium text-purple-600 hover:underline">
          Log In
        </Link>
      </div>
    </form>
  )
}
