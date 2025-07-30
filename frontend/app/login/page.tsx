"use client"

import { AuthFormWrapper } from "@/components/auth/auth-form-wrapper"
import { LoginForm } from "@/components/auth/login-form"
import { MobileFrame } from "@/components/mobile-frame"
import { useIsMobile } from "@/hooks/use-is-mobile"
import { isAuthenticated, redirectToHome } from "@/lib/auth"
import { useEffect, useState } from "react"

export default function LoginPage() {
  const isMobile = useIsMobile()
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    setMounted(true)
    if (isAuthenticated()) {
      redirectToHome()
    }
  }, [])

  const content = (
    <AuthFormWrapper
      title="Welcome Back"
      description="Sign in to your TravelStyle AI account"
      footerText="Don't have an account?"
      footerLinkHref="/signup"
      footerLinkText="Sign Up"
    >
      <LoginForm />
    </AuthFormWrapper>
  )

  // Prevent hydration mismatch by not rendering mobile frame until mounted
  if (!mounted) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 flex items-center justify-center p-4">
        <div className="w-full max-w-md mx-auto bg-white rounded-2xl shadow-2xl overflow-hidden">{content}</div>
      </div>
    )
  }

  if (isMobile) {
    return <MobileFrame>{content}</MobileFrame>
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 flex items-center justify-center p-4">
      <div className="w-full max-w-md mx-auto bg-white rounded-2xl shadow-2xl overflow-hidden">{content}</div>
    </div>
  )
}
