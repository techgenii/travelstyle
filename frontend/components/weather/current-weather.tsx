import { getOpenWeatherIconUrl, getWeatherIcon, formatTemperature } from "@/utils/weather-utils"
import type { WeatherCurrent } from "@/lib/types/api"

interface CurrentWeatherProps {
  weather: WeatherCurrent
}

export function CurrentWeather({ weather }: CurrentWeatherProps) {
  const WeatherIcon = getWeatherIcon(weather.weather[0]?.main || "")

  return (
    <div className="flex items-center justify-between mb-4">
      <div className="flex items-center">
        {weather.weather[0]?.icon ? (
          // eslint-disable-next-line @next/next/no-img-element
          <img
            src={getOpenWeatherIconUrl(weather.weather[0].icon) || "/placeholder.svg"}
            alt={weather.weather[0].description}
            className="w-10 h-10"
          />
        ) : (
          <WeatherIcon className="w-6 h-6 text-yellow-400" />
        )}
        <div className="ml-3">
          <h3 className="text-xl font-semibold text-gray-800">{weather.name}</h3>
          <p className="text-sm text-gray-600">{weather.weather[0]?.description || "N/A"}</p>
        </div>
      </div>
      <div className="text-4xl font-bold text-gray-900">{formatTemperature(weather.main.temp)}</div>
    </div>
  )
}
