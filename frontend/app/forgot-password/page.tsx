"use client"

import { AuthFormWrapper } from "@/components/auth/auth-form-wrapper"
import { ForgotPasswordForm } from "@/components/auth/forgot-password-form"
import { MobileFrame } from "@/components/mobile-frame"
import { useIsMobile } from "@/hooks/use-is-mobile"
import { isAuthenticated, redirectToHome } from "@/lib/auth"
import { useEffect } from "react"

export default function ForgotPasswordPage() {
  const isMobile = useIsMobile()

  useEffect(() => {
    if (isAuthenticated()) {
      redirectToHome()
    }
  }, [])

  const content = (
    <AuthFormWrapper
      title="Forgot Password"
      description="Enter your email to receive a reset link"
      footerText="Remember your password?"
      footerLinkHref="/login"
      footerLinkText="Log In"
    >
      <ForgotPasswordForm />
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
