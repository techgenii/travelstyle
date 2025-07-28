"use client"

// app/forgot-password/page.tsx
import { ForgotPasswordForm } from "@/components/auth/forgot-password-form"
import { MobileFrame } from "@/components/mobile-frame" // Import MobileFrame
import { useIsMobile } from "@/hooks/use-is-mobile"

export default function ForgotPasswordPage() {
  const isMobile = useIsMobile()

  return (
    <div className="min-h-screen bg-gray-100 flex items-center justify-center p-4">
      {isMobile ? (
        <MobileFrame>
          <ForgotPasswordForm />
        </MobileFrame>
      ) : (
        // Desktop view: ForgotPasswordForm will naturally center itself
        <ForgotPasswordForm />
      )}
    </div>
  )
}
