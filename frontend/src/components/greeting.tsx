interface GreetingProps {
  mainText: string
  subText: string
}

export function Greeting({ mainText, subText }: GreetingProps) {
  return (
    <div className="px-4 py-6">
      <h1 className="text-2xl font-semibold text-gray-900 mb-2 leading-tight animate-greeting-entry">{mainText}</h1>
      <p className="text-base text-gray-600 leading-relaxed">{subText}</p>
    </div>
  )
}
