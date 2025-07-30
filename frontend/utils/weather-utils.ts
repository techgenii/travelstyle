import { Sun, Cloud, CloudRain, Thermometer } from "lucide-react"

export function getWeatherIcon(condition: string) {
  switch (condition.toLowerCase()) {
    case "clear":
      return Sun
    case "clouds":
      return Cloud
    case "rain":
    case "drizzle":
    case "thunderstorm":
      return CloudRain
    default:
      return Thermometer
  }
}

export function getOpenWeatherIconUrl(iconCode: string): string {
  return `https://openweathermap.org/img/wn/${iconCode}@2x.png`
}

export function getDayOfWeek(dateString: string, index: number): string {
  if (index === 0) return "Today"
  if (index === 1) return "Tomorrow"
  const date = new Date(dateString)
  return date.toLocaleDateString("en-US", { weekday: "short" })
}

export function formatTemperature(temp: number): string {
  return `${Math.round(temp)}°F`
}
