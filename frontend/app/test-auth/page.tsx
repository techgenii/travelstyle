"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"

export default function TestAuthPage() {
    const [email, setEmail] = useState("test@example.com")
    const [password, setPassword] = useState("test123")
    const [result, setResult] = useState<string>("")
    const [loading, setLoading] = useState(false)

    const testLogin = async () => {
        setLoading(true)
        setResult("Testing login...")

        try {
            const response = await fetch("https://3a8rb9s3d6.execute-api.us-west-2.amazonaws.com/api/v1/auth/login", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ email, password }),
            })

            const data = await response.json()
            setResult(`Status: ${response.status}\nResponse: ${JSON.stringify(data, null, 2)}`)
        } catch (error) {
            setResult(`Error: ${error}`)
        } finally {
            setLoading(false)
        }
    }

    const testRegister = async () => {
        setLoading(true)
        setResult("Testing register...")

        try {
            const response = await fetch("https://3a8rb9s3d6.execute-api.us-west-2.amazonaws.com/api/v1/auth/register", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    email: `test${Date.now()}@example.com`,
                    password: "test123",
                    first_name: "Test",
                    last_name: "User"
                }),
            })

            const data = await response.json()
            setResult(`Status: ${response.status}\nResponse: ${JSON.stringify(data, null, 2)}`)
        } catch (error) {
            setResult(`Error: ${error}`)
        } finally {
            setLoading(false)
        }
    }

    return (
        <div className="container mx-auto p-8 max-w-2xl">
            <h1 className="text-2xl font-bold mb-6">Auth Endpoint Test</h1>

            <div className="space-y-4 mb-6">
                <div>
                    <Label htmlFor="email">Email</Label>
                    <Input
                        id="email"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        placeholder="test@example.com"
                    />
                </div>
                <div>
                    <Label htmlFor="password">Password</Label>
                    <Input
                        id="password"
                        type="password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        placeholder="test123"
                    />
                </div>
            </div>

            <div className="space-x-4 mb-6">
                <Button onClick={testLogin} disabled={loading}>
                    Test Login
                </Button>
                <Button onClick={testRegister} disabled={loading}>
                    Test Register
                </Button>
            </div>

            <div className="bg-gray-100 p-4 rounded">
                <h2 className="font-semibold mb-2">Result:</h2>
                <pre className="text-sm whitespace-pre-wrap">{result}</pre>
            </div>
        </div>
    )
}
