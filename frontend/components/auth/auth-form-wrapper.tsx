import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import Link from "next/link"
import type { ReactNode } from "react"

interface AuthFormWrapperProps {
  title: string
  description: string
  children: ReactNode
  footerText: string
  footerLinkHref: string
  footerLinkText: string
}

export function AuthFormWrapper({
  title,
  description,
  children,
  footerText,
  footerLinkHref,
  footerLinkText,
}: AuthFormWrapperProps) {
  return (
    <Card className="w-full max-w-md mx-auto rounded-2xl shadow-lg border-none">
      <CardHeader className="text-center pt-8 pb-4">
        <CardTitle className="text-3xl font-bold text-gray-800">{title}</CardTitle>
        <CardDescription className="text-gray-500 mt-2">{description}</CardDescription>
      </CardHeader>
      <CardContent className="px-6 py-4">{children}</CardContent>
      <CardFooter className="text-center flex flex-col pb-6">
        <p className="text-sm text-gray-600">
          {footerText}{" "}
          <Link href={footerLinkHref} className="font-semibold text-purple-600 hover:underline">
            {footerLinkText}
          </Link>
        </p>
      </CardFooter>
    </Card>
  )
}
