"use client"

import { AuthFormWrapper } from "@/components/auth/auth-form-wrapper"
import { SignupForm } from "@/components/auth/signup-form"
import { MobileFrame } from "@/components/mobile-frame"
import { useIsMobile } from "@/hooks/use-is-mobile"
import { isAuthenticated, redirectToHome } from "@/lib/auth"
import { useEffect } from "react"

export default function SignupPage() {
  const isMobile = useIsMobile()

  useEffect(() => {
    if (isAuthenticated()) {
      redirectToHome()
    }
  }, [])

  const content = (
    <AuthFormWrapper
      title="Create Account"
      description="Join TravelStyle AI and start your journey"
      footerText="Already have an account?"
      footerLinkHref="/login"
      footerLinkText="Log In"
    >
      <SignupForm />
    </AuthFormWrapper>
  )

  if (isMobile) {
    return <MobileFrame>{content}</MobileFrame>
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 flex items-center justify-center p-4">
      <div className="w-full max-w-md mx-auto bg-white rounded-2xl shadow-2xl overflow-hidden">{content}</div>
    </div>
  )
}
