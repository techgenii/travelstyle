import { getWeatherIcon, getDayOfWeek, formatTemperature } from "@/utils/weather-utils"
import type { WeatherDailyForecast } from "@/lib/types/api"

interface WeatherForecastProps {
  forecasts: WeatherDailyForecast[]
}

export function WeatherForecast({ forecasts }: WeatherForecastProps) {
  return (
    <div className="flex justify-around text-center">
      {forecasts.map((day, index) => {
        const WeatherIcon = getWeatherIcon(day.conditions)
        return (
          <div key={day.date} className="flex flex-col items-center">
            <span className="text-xs font-medium text-gray-600 mb-1">{getDayOfWeek(day.date, index)}</span>
            <WeatherIcon className="w-6 h-6 text-gray-400" />
            <span className="text-sm font-semibold text-gray-800">{formatTemperature(day.temp_max)}</span>
            <span className="text-xs text-gray-500">{formatTemperature(day.temp_min)}</span>
          </div>
        )
      })}
    </div>
  )
}
