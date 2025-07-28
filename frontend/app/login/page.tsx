"use client"

// app/login/page.tsx
import { LoginForm } from "@/components/auth/login-form"
import { MobileFrame } from "@/components/mobile-frame" // Import MobileFrame
import { useIsMobile } from "@/hooks/use-is-mobile"

export default function LoginPage() {
  const isMobile = useIsMobile()

  return (
    <div className="min-h-screen bg-gray-100 flex items-center justify-center p-4">
      {isMobile ? (
        <MobileFrame>
          <LoginForm />
        </MobileFrame>
      ) : (
        // Desktop view: LoginForm (which uses AuthFormWrapper) will naturally center itself
        <LoginForm />
      )}
    </div>
  )
}
