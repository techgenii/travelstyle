"use client"

import type React from "react"

import { useState, useEffect } from "react"
import { Card, CardContent } from "@/components/ui/card"
import { Input } from "@/components/ui/input" // New: Import Input
import { Button } from "@/components/ui/button" // New: Import Button
import { Search } from "lucide-react" // New: Import Search icon
import { cn } from "@/lib/utils"
import { colors } from "@/lib/design-system"
import { useWeatherData } from "@/hooks/use-weather-data"
import { WeatherLoading } from "./weather/weather-loading"
import { WeatherError } from "./weather/weather-error"
import { CurrentWeather } from "./weather/current-weather"
import { WeatherStats } from "./weather/weather-stats"
import { WeatherForecast } from "./weather/weather-forecast"

interface WeatherWidgetProps {
  location?: string // This is now the default location from user profile
}

export function WeatherWidget({ location: defaultLocation = "Los Angeles" }: WeatherWidgetProps) {
  const [currentLocation, setCurrentLocation] = useState(defaultLocation)
  const [inputLocation, setInputLocation] = useState(defaultLocation)

  // Re-fetch weather data when defaultLocation changes or when user manually sets a new location
  const { currentWeather, dailyForecasts, loading, error } = useWeatherData(currentLocation)

  useEffect(() => {
    // Update currentLocation when defaultLocation prop changes (e.g., on user login/profile update)
    if (defaultLocation && defaultLocation !== currentLocation) {
      setCurrentLocation(defaultLocation)
      setInputLocation(defaultLocation)
    }
  }, [defaultLocation, currentLocation])

  const handleSetLocation = () => {
    if (inputLocation.trim() && inputLocation.trim() !== currentLocation) {
      setCurrentLocation(inputLocation.trim())
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter") {
      e.preventDefault()
      handleSetLocation()
    }
  }

  if (loading) {
    return <WeatherLoading location={currentLocation} />
  }

  if (error) {
    return <WeatherError error={error} />
  }

  if (!currentWeather || !dailyForecasts || dailyForecasts.length === 0) {
    return (
      <Card className={cn("w-full", colors.gradients.weatherWidget, "shadow-lg rounded-xl")}>
        <CardContent className="p-4 flex flex-col items-center justify-center h-32 text-center">
          <p className="text-gray-700 mb-2">No weather forecast available for {currentLocation}.</p>
          <div className="flex w-full max-w-sm">
            <Input
              type="text"
              placeholder="Enter new location"
              value={inputLocation}
              onChange={(e) => setInputLocation(e.target.value)}
              onKeyDown={handleKeyDown}
              className="flex-1 rounded-r-none"
            />
            <Button onClick={handleSetLocation} className="rounded-l-none">
              <Search className="h-4 w-4" />
            </Button>
          </div>
        </CardContent>
      </Card>
    )
  }

  const todayForecast = dailyForecasts[0]

  return (
    <Card className={cn("w-full", colors.gradients.weatherWidget, "shadow-lg rounded-xl")}>
      <CardContent className="p-4">
        <CurrentWeather weather={currentWeather} />
        <WeatherStats currentWeather={currentWeather} todayForecast={todayForecast} />
        <WeatherForecast forecasts={dailyForecasts} />

        {/* Location Input and Set Button */}
        <div className="mt-4 pt-4 border-t border-gray-200 flex items-center space-x-2">
          <Input
            type="text"
            placeholder="Change location"
            value={inputLocation}
            onChange={(e) => setInputLocation(e.target.value)}
            onKeyDown={handleKeyDown}
            className="flex-1"
          />
          <Button onClick={handleSetLocation} size="icon" className="flex-shrink-0">
            <Search className="h-4 w-4" />
          </Button>
        </div>
      </CardContent>
    </Card>
  )
}
