"use client"

import type { ReactNode } from "react"

interface MobileFrameProps {
  children: ReactNode
}

export function MobileFrame({ children }: MobileFrameProps) {
  return (
    <div className="relative w-full max-w-md mx-auto aspect-[9/19.5] bg-black rounded-[2.5rem] shadow-2xl overflow-hidden">
      {/* Notch */}
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[100px] h-[25px] bg-black rounded-b-xl z-10" />

      {/* Speaker and Camera (mock) */}
      <div className="absolute top-2 left-1/2 -translate-x-1/2 flex items-center justify-center w-1/3 h-4">
        <div className="w-10 h-1.5 bg-gray-700 rounded-full mr-2" />
        <div className="w-2 h-2 bg-gray-700 rounded-full" />
      </div>

      {/* Screen content */}
      <div className="relative w-full h-full pt-[25px] pb-[10px] px-[10px] box-border">
        <div className="relative w-full h-full bg-white rounded-[2rem] overflow-hidden">{children}</div>
      </div>

      {/* Side buttons (mock) */}
      <div className="absolute top-1/4 left-0 w-2 h-10 bg-gray-800 rounded-l-md" />
      <div className="absolute top-1/2 left-0 w-2 h-16 bg-gray-800 rounded-l-md" />
      <div className="absolute top-1/3 right-0 w-2 h-16 bg-gray-800 rounded-r-md" />
    </div>
  )
}
