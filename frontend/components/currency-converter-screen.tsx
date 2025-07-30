"use client"

import { useState, useEffect } from "react"
import { Header } from "./header"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Loader2, ArrowRightLeft } from "lucide-react"
import { cn } from "@/lib/utils"
import { fetchExchangeRate, getAvailableCurrencies } from "@/lib/services/currency"

interface CurrencyConverterScreenProps {
  onBack: () => void
  userId: string // Added userId prop
}

export function CurrencyConverterScreen({ onBack, userId }: CurrencyConverterScreenProps) {
  const [amount, setAmount] = useState<string>("1.00")
  const [fromCurrency, setFromCurrency] = useState<string>("USD")
  const [toCurrency, setToCurrency] = useState<string>("EUR")
  const [convertedAmount, setConvertedAmount] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [currencies, setCurrencies] = useState<Array<{ value: string; label: string }>>([])

  useEffect(() => {
    const loadCurrencies = async () => {
      try {
        const availableCurrencies = await getAvailableCurrencies()
        setCurrencies(availableCurrencies)
      } catch (err) {
        console.error("Failed to load currencies:", err)
        setError("Failed to load currency list. Please try again.")
      }
    }
    loadCurrencies()
  }, [])

  const handleConvert = async () => {
    setError(null)
    setConvertedAmount(null)
    setIsLoading(true)

    const numAmount = Number.parseFloat(amount)
    if (isNaN(numAmount) || numAmount <= 0) {
      setError("Please enter a valid positive amount.")
      setIsLoading(false)
      return
    }

    if (!fromCurrency || !toCurrency) {
      setError("Please select both 'From' and 'To' currencies.")
      setIsLoading(false)
      return
    }

    try {
      const response = await fetchExchangeRate(fromCurrency, toCurrency, numAmount, userId)
      setConvertedAmount(response.converted_amount.toFixed(2))
    } catch (err: any) {
      console.error("Conversion error:", err)
      setError(err.message || "Failed to convert currency. Please try again.")
    } finally {
      setIsLoading(false)
    }
  }

  const handleSwapCurrencies = () => {
    setFromCurrency(toCurrency)
    setToCurrency(fromCurrency)
    setConvertedAmount(null) // Clear converted amount after swap
    setError(null)
  }

  return (
    <div className="flex flex-col h-full bg-[#F8F6FF]">
      <Header title="Currency Converter" showBack onBack={onBack} />

      <div className="flex-1 overflow-y-auto p-4 space-y-6">
        <Card className="bg-white rounded-2xl shadow-soft border border-gray-100">
          <CardContent className="p-6 space-y-4">
            <div className="space-y-2">
              <label htmlFor="amount" className="text-sm font-medium text-gray-700">
                Amount
              </label>
              <Input
                id="amount"
                type="number"
                value={amount}
                onChange={(e) => setAmount(e.target.value)}
                placeholder="Enter amount"
                className="rounded-xl"
                disabled={isLoading}
              />
            </div>

            <div className="grid grid-cols-[1fr_auto_1fr] items-center gap-2">
              <div className="space-y-2">
                <label htmlFor="from-currency" className="text-sm font-medium text-gray-700">
                  From
                </label>
                <Select value={fromCurrency} onValueChange={setFromCurrency} disabled={isLoading}>
                  <SelectTrigger id="from-currency" className="rounded-xl">
                    <SelectValue placeholder="Select currency" />
                  </SelectTrigger>
                  <SelectContent>
                    {currencies.map((currency) => (
                      <SelectItem key={currency.value} value={currency.value}>
                        {currency.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <Button
                variant="ghost"
                size="icon"
                onClick={handleSwapCurrencies}
                className="mt-6 rounded-full text-gray-600 hover:bg-gray-100"
                disabled={isLoading}
                aria-label="Swap currencies"
              >
                <ArrowRightLeft className="h-5 w-5" />
              </Button>

              <div className="space-y-2">
                <label htmlFor="to-currency" className="text-sm font-medium text-gray-700">
                  To
                </label>
                <Select value={toCurrency} onValueChange={setToCurrency} disabled={isLoading}>
                  <SelectTrigger id="to-currency" className="rounded-xl">
                    <SelectValue placeholder="Select currency" />
                  </SelectTrigger>
                  <SelectContent>
                    {currencies.map((currency) => (
                      <SelectItem key={currency.value} value={currency.value}>
                        {currency.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>

            <Button
              onClick={handleConvert}
              className={cn(
                "w-full rounded-full py-3 bg-purple-600 hover:bg-purple-700 text-white shadow-md",
                isLoading && "opacity-70 cursor-not-allowed",
              )}
              disabled={isLoading}
            >
              {isLoading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" /> Converting...
                </>
              ) : (
                "Convert"
              )}
            </Button>

            {error && <p className="text-red-500 text-center text-sm mt-4">{error}</p>}

            {convertedAmount && (
              <div className="text-center mt-4 p-4 bg-purple-50 rounded-xl text-purple-800 font-semibold text-lg">
                {amount} {fromCurrency} = {convertedAmount} {toCurrency}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
