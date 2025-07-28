"use client"

import { useState, useEffect } from "react"
import { Cloud, Sun, CloudRain, Snowflake, CloudFog, Wind } from "lucide-react"
import { fetchWeather, type WeatherData } from "@/lib/services/weather"

export function WeatherWidget() {
  const [weather, setWeather] = useState<WeatherData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const loadWeather = async (latitude?: number, longitude?: number) => {
      setLoading(true)
      setError(null)
      try {
        let destination = "San Francisco" // Default destination
        if (latitude && longitude) {
          // In a real app, you'd use a reverse geocoding API here
          // For now, we'll just use a placeholder or try to infer
          // For demonstration, let's just use a fixed location for now
          // or you could pass a prop to WeatherWidget for the user's last known trip destination
          destination = "New York City" // Example: could be dynamic based on user profile or last trip
        }

        const fetchedWeather = await fetchWeather(destination)
        setWeather(fetchedWeather)
      } catch (err) {
        setError("Failed to fetch weather data. Showing default.")
        console.error("Weather fetch error:", err)
        // Fallback to a mock or default if API fails
        setWeather({
          location: "San Francisco",
          temperature: 18,
          condition: "cloudy",
          current: {
            temperature: 18,
            feels_like: 17,
            humidity: 70,
            description: "cloudy",
            wind_speed: 5,
            visibility: 10,
            pressure: 1012,
          },
          forecast: {
            daily_forecasts: [],
            temp_range: { min: 15, max: 20 },
            precipitation_chance: 20,
          },
          clothing_recommendations: {
            layers: ["Light jacket"],
            footwear: ["Comfortable walking shoes"],
            accessories: [],
            materials: [],
            special_considerations: [],
          },
          retrieved_at: new Date().toISOString(),
        } as WeatherData) // Cast to WeatherData to satisfy type
      } finally {
        setLoading(false)
      }
    }

    // This part remains similar, but now calls loadWeather
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          loadWeather(position.coords.latitude, position.coords.longitude)
        },
        (err) => {
          console.warn(`ERROR(${err.code}): ${err.message}`)
          setError("Location access denied. Showing default weather.")
          loadWeather() // Fetch with default location if access denied
        },
        { enableHighAccuracy: true, timeout: 5000, maximumAge: 0 },
      )
    } else {
      setError("Geolocation not supported by your browser. Showing default weather.")
      loadWeather() // Fetch with default location if geolocation not supported
    }
  }, [])

  const getWeatherIcon = (conditionDescription: string) => {
    if (conditionDescription.toLowerCase().includes("sun")) return <Sun className="h-6 w-6 text-yellow-500" />
    if (conditionDescription.toLowerCase().includes("cloud")) return <Cloud className="h-6 w-6 text-gray-500" />
    if (conditionDescription.toLowerCase().includes("rain") || conditionDescription.toLowerCase().includes("drizzle"))
      return <CloudRain className="h-6 w-6 text-blue-500" />
    if (conditionDescription.toLowerCase().includes("snow")) return <Snowflake className="h-6 w-6 text-blue-300" />
    if (conditionDescription.toLowerCase().includes("fog") || conditionDescription.toLowerCase().includes("mist"))
      return <CloudFog className="h-6 w-6 text-gray-400" />
    if (conditionDescription.toLowerCase().includes("wind")) return <Wind className="h-6 w-6 text-gray-500" />
    return <Sun className="h-6 w-6 text-yellow-500" />
  }

  if (loading) {
    return (
      <div className="bg-white rounded-2xl p-4 shadow-soft flex items-center justify-center h-24">
        <p className="text-sm text-gray-600">Loading weather...</p>
      </div>
    )
  }

  if (error) {
    return (
      <div className="bg-white rounded-2xl p-4 shadow-soft flex flex-col items-center justify-center h-24 text-center">
        <p className="text-sm text-red-500 mb-1">{error}</p>
        <p className="text-xs text-gray-500">Weather for San Francisco</p>
      </div>
    )
  }

  if (!weather) {
    return null
  }

  return (
    <div className="bg-white rounded-2xl p-4 shadow-soft flex items-center gap-4">
      <div className="flex-shrink-0">{getWeatherIcon(weather.current.description)}</div>
      <div>
        <p className="text-lg font-semibold text-gray-900">{weather.current.temperature}°C</p>
        <p className="text-sm text-gray-600">{weather.location}</p>
      </div>
    </div>
  )
}
