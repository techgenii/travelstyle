import { Card, CardContent } from "@/components/ui/card"
import { cn } from "@/lib/utils"
import { colors } from "@/lib/design-system"

interface WeatherErrorProps {
  error: string
}

export function WeatherError({ error }: WeatherErrorProps) {
  return (
    <Card className={cn("w-full", colors.gradients.weatherWidget, "shadow-lg rounded-xl")}>
      <CardContent className="p-4 flex items-center justify-center h-32">
        <p className="text-red-600">Error: {error}</p>
      </CardContent>
    </Card>
  )
}
