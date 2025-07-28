"use client"

import { useState, useEffect } from "react"

const MOBILE_BREAKPOINT = 768 // Corresponds to Tailwind's 'md' breakpoint

export function useIsMobile() {
  const [isMobile, setIsMobile] = useState(false)

  useEffect(() => {
    // Function to check if current window width is mobile
    const checkIsMobile = () => {
      setIsMobile(window.innerWidth < MOBILE_BREAKPOINT)
    }

    // Set initial value
    checkIsMobile()

    // Add event listener for window resize
    window.addEventListener("resize", checkIsMobile)

    // Clean up event listener on component unmount
    return () => {
      window.removeEventListener("resize", checkIsMobile)
    }
  }, []) // Empty dependency array ensures this runs once on mount and cleans up on unmount

  return isMobile
}
