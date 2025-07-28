// components/auth/auth-form-wrapper.tsx
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import type { ReactNode } from "react"

interface AuthFormWrapperProps {
  title: string
  children: ReactNode
}

export function AuthFormWrapper({ title, children }: AuthFormWrapperProps) {
  return (
    // Removed the 'p-4' from here. The Card itself has padding.
    // This div now simply ensures the background color fills the space and centers the card.
    <div className="w-full h-full flex items-center justify-center bg-[#F8F6FF]">
      <Card className="w-full max-w-md rounded-2xl shadow-soft">
        <CardHeader className="text-center">
          <CardTitle className="text-2xl font-bold text-gray-900">{title}</CardTitle>
        </CardHeader>
        <CardContent className="p-6">{children}</CardContent>
      </Card>
    </div>
  )
}
