import type { ReactNode } from "react"

interface MobileFrameProps {
  children: ReactNode
}

export function MobileFrame({ children }: MobileFrameProps) {
  return (
    <div className="mx-auto max-w-[390px] h-[844px] bg-white relative overflow-hidden rounded-[40px] shadow-2xl border border-gray-200">
      {/* Status Bar */}
      <div className="absolute top-0 left-0 right-0 h-11 flex items-center justify-between px-6 text-sm font-semibold text-black z-50">
        <span>9:41</span>
        <div className="flex items-center gap-1">
          <div className="w-4 h-3 border border-black rounded-sm">
            <div className="w-2 h-1 bg-black rounded-sm m-0.5"></div>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="pt-11 pb-8 h-full flex flex-col">{children}</div>

      {/* Home Indicator */}
      <div className="absolute bottom-2 left-1/2 transform -translate-x-1/2 w-32 h-1 bg-black rounded-full"></div>
    </div>
  )
}
