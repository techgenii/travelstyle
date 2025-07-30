import { Thermometer, Droplet, Wind, Gauge } from "lucide-react"
import { formatTemperature } from "@/utils/weather-utils"
import type { WeatherCurrent, WeatherDailyForecast } from "@/lib/types/api"

interface WeatherStatsProps {
  currentWeather: WeatherCurrent
  todayForecast: WeatherDailyForecast
}

export function WeatherStats({ currentWeather, todayForecast }: WeatherStatsProps) {
  return (
    <div className="grid grid-cols-2 gap-2 text-sm text-gray-700 mb-4 border-b pb-4 border-gray-200">
      <div className="flex items-center">
        <Thermometer size={16} className="mr-2" /> Min: {formatTemperature(todayForecast.temp_min)}
      </div>
      <div className="flex items-center">
        <Thermometer size={16} className="mr-2" /> Max: {formatTemperature(todayForecast.temp_max)}
      </div>
      <div className="flex items-center">
        <Droplet size={16} className="mr-2" /> Humidity: {currentWeather.main.humidity}%
      </div>
      <div className="flex items-center">
        <Wind size={16} className="mr-2" /> Wind: {currentWeather.wind.speed} m/s
      </div>
      <div className="flex items-center">
        <Gauge size={16} className="mr-2" /> Pressure: {currentWeather.main.pressure} hPa
      </div>
    </div>
  )
}
