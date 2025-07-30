"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { CreditCard } from "lucide-react"
import { ToggleableList } from "./toggleable-list"

interface CurrencySectionProps {
  selectedCurrencies: string[]
  onToggleCurrency: (currency: string) => void
}

const supportedCurrencies = [
  "USD",
  "EUR",
  "GBP",
  "JPY",
  "CAD",
  "AUD",
  "CHF",
  "CNY",
  "INR",
  "BRL",
  "MXN",
  "KRW",
  "SGD",
  "HKD",
  "NZD",
  "SEK",
  "NOK",
  "DKK",
  "PLN",
  "CZK",
  "HUF",
  "ILS",
  "ZAR",
  "THB",
  "PHP",
  "MYR",
  "IDR",
  "VND",
  "TRY",
  "RUB",
  "AED",
  "SAR",
  "QAR",
  "KWD",
  "BHD",
  "OMR",
  "JOD",
  "LBP",
  "EGP",
  "MAD",
]

export function CurrencySection({ selectedCurrencies, onToggleCurrency }: CurrencySectionProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <CreditCard className="h-5 w-5" />
          Currency Preferences
        </CardTitle>
      </CardHeader>
      <CardContent>
        <ToggleableList
          title="Currencies"
          description="Select your preferred currencies:"
          items={supportedCurrencies}
          selectedItems={selectedCurrencies}
          onToggle={onToggleCurrency}
          columns={5}
          compact
        />
      </CardContent>
    </Card>
  )
}
