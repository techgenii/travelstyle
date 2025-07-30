import { Card, CardContent } from "@/components/ui/card"
import { cn } from "@/lib/utils"
import { colors } from "@/lib/design-system"

interface WeatherLoadingProps {
  location: string
}

export function WeatherLoading({ location }: WeatherLoadingProps) {
  return (
    <Card className={cn("w-full", colors.gradients.weatherWidget, "shadow-lg rounded-xl")}>
      <CardContent className="p-4 flex items-center justify-center h-32">
        <div className="flex items-center space-x-2">
          <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-gray-600"></div>
          <p className="text-gray-700">Loading weather for {location}...</p>
        </div>
      </CardContent>
    </Card>
  )
}
