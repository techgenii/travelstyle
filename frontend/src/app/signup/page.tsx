"use client"

// app/signup/page.tsx
import { SignupForm } from "@/components/auth/signup-form"
import { MobileFrame } from "@/components/mobile-frame" // Import MobileFrame
import { useIsMobile } from "@/hooks/use-is-mobile"

export default function SignupPage() {
  const isMobile = useIsMobile()

  return (
    <div className="min-h-screen bg-gray-100 flex items-center justify-center p-4">
      {isMobile ? (
        <MobileFrame>
          <SignupForm />
        </MobileFrame>
      ) : (
        // Desktop view: SignupForm will naturally center itself
        <SignupForm />
      )}
    </div>
  )
}
