"use client"

import * as React from "react"
import { Area, AreaChart, CartesianGrid, XAxis } from "recharts"

import { useIsMobile } from "@/hooks/use-mobile"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { type ChartConfig, ChartContainer, ChartTooltip, ChartTooltipContent } from "@/components/ui/chart"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { ToggleGroup, ToggleGroupItem } from "@/components/ui/toggle-group"
const chartData = [
  { date: "2024-04-01", bankA: 12000, bankB: 8000, bankC: 5000 },
  { date: "2024-04-02", bankA: 8000, bankB: 10000, bankC: 7000 },
  { date: "2024-04-03", bankA: 15000, bankB: 12000, bankC: 9000 },
  { date: "2024-04-04", bankA: 20000, bankB: 15000, bankC: 10000 },
  { date: "2024-04-05", bankA: 18000, bankB: 22000, bankC: 14000 },
  { date: "2024-04-06", bankA: 10000, bankB: 8000, bankC: 6000 },
  { date: "2024-04-07", bankA: 5000, bankB: 7000, bankC: 4000 },
  { date: "2024-04-08", bankA: 22000, bankB: 18000, bankC: 12000 },
  { date: "2024-04-09", bankA: 14000, bankB: 10000, bankC: 8000 },
  { date: "2024-04-10", bankA: 17000, bankB: 14000, bankC: 9000 },
  { date: "2024-04-11", bankA: 25000, bankB: 20000, bankC: 15000 },
  { date: "2024-04-12", bankA: 19000, bankB: 16000, bankC: 11000 },
  { date: "2024-04-13", bankA: 12000, bankB: 9000, bankC: 7000 },
  { date: "2024-04-14", bankA: 7000, bankB: 5000, bankC: 3000 },
  { date: "2024-04-15", bankA: 9000, bankB: 11000, bankC: 6000 },
  { date: "2024-04-16", bankA: 16000, bankB: 13000, bankC: 8000 },
  { date: "2024-04-17", bankA: 28000, bankB: 22000, bankC: 17000 },
  { date: "2024-04-18", bankA: 21000, bankB: 19000, bankC: 14000 },
  { date: "2024-04-19", bankA: 13000, bankB: 10000, bankC: 7000 },
  { date: "2024-04-20", bankA: 8000, bankB: 6000, bankC: 4000 },
  { date: "2024-04-21", bankA: 11000, bankB: 9000, bankC: 6000 },
  { date: "2024-04-22", bankA: 18000, bankB: 15000, bankC: 10000 },
  { date: "2024-04-23", bankA: 14000, bankB: 12000, bankC: 8000 },
  { date: "2024-04-24", bankA: 23000, bankB: 18000, bankC: 13000 },
  { date: "2024-04-25", bankA: 17000, bankB: 14000, bankC: 9000 },
  { date: "2024-04-26", bankA: 9000, bankB: 7000, bankC: 5000 },
  { date: "2024-04-27", bankA: 20000, bankB: 16000, bankC: 12000 },
  { date: "2024-04-28", bankA: 7000, bankB: 5000, bankC: 3000 },
  { date: "2024-04-29", bankA: 19000, bankB: 15000, bankC: 10000 },
  { date: "2024-04-30", bankA: 24000, bankB: 20000, bankC: 15000 },
  { date: "2024-05-01", bankA: 15000, bankB: 12000, bankC: 8000 },
  { date: "2024-05-02", bankA: 21000, bankB: 17000, bankC: 12000 },
  { date: "2024-05-03", bankA: 18000, bankB: 15000, bankC: 10000 },
  { date: "2024-05-04", bankA: 22000, bankB: 18000, bankC: 13000 },
  { date: "2024-05-05", bankA: 14000, bankB: 11000, bankC: 7000 },
  { date: "2024-05-06", bankA: 26000, bankB: 21000, bankC: 16000 },
  { date: "2024-05-07", bankA: 19000, bankB: 16000, bankC: 11000 },
  { date: "2024-05-08", bankA: 11000, bankB: 9000, bankC: 6000 },
  { date: "2024-05-09", bankA: 17000, bankB: 14000, bankC: 9000 },
  { date: "2024-05-10", bankA: 23000, bankB: 19000, bankC: 14000 },
  { date: "2024-05-11", bankA: 16000, bankB: 13000, bankC: 9000 },
  { date: "2024-05-12", bankA: 9000, bankB: 7000, bankC: 5000 },
  { date: "2024-05-13", bankA: 12000, bankB: 10000, bankC: 7000 },
  { date: "2024-05-14", bankA: 25000, bankB: 20000, bankC: 15000 },
  { date: "2024-05-15", bankA: 20000, bankB: 17000, bankC: 12000 },
  { date: "2024-05-16", bankA: 15000, bankB: 12000, bankC: 8000 },
  { date: "2024-05-17", bankA: 27000, bankB: 22000, bankC: 17000 },
  { date: "2024-05-18", bankA: 18000, bankB: 15000, bankC: 11000 },
  { date: "2024-05-19", bankA: 10000, bankB: 8000, bankC: 5000 },
  { date: "2024-05-20", bankA: 14000, bankB: 12000, bankC: 8000 },
  { date: "2024-05-21", bankA: 7000, bankB: 6000, bankC: 4000 },
  { date: "2024-05-22", bankA: 6000, bankB: 5000, bankC: 3000 },
  { date: "2024-05-23", bankA: 19000, bankB: 15000, bankC: 11000 },
  { date: "2024-05-24", bankA: 17000, bankB: 14000, bankC: 10000 },
  { date: "2024-05-25", bankA: 13000, bankB: 11000, bankC: 7000 },
  { date: "2024-05-26", bankA: 11000, bankB: 9000, bankC: 6000 },
  { date: "2024-05-27", bankA: 24000, bankB: 20000, bankC: 15000 },
  { date: "2024-05-28", bankA: 14000, bankB: 11000, bankC: 8000 },
  { date: "2024-05-29", bankA: 6000, bankB: 5000, bankC: 3000 },
  { date: "2024-05-30", bankA: 18000, bankB: 15000, bankC: 11000 },
  { date: "2024-05-31", bankA: 12000, bankB: 10000, bankC: 7000 },
  { date: "2024-06-01", bankA: 11000, bankB: 9000, bankC: 6000 },
  { date: "2024-06-02", bankA: 23000, bankB: 19000, bankC: 14000 },
  { date: "2024-06-03", bankA: 9000, bankB: 7000, bankC: 5000 },
  { date: "2024-06-04", bankA: 21000, bankB: 17000, bankC: 12000 },
  { date: "2024-06-05", bankA: 7000, bankB: 6000, bankC: 4000 },
  { date: "2024-06-06", bankA: 17000, bankB: 14000, bankC: 10000 },
  { date: "2024-06-07", bankA: 20000, bankB: 16000, bankC: 12000 },
  { date: "2024-06-08", bankA: 19000, bankB: 16000, bankC: 11000 },
  { date: "2024-06-09", bankA: 22000, bankB: 18000, bankC: 13000 },
  { date: "2024-06-10", bankA: 12000, bankB: 10000, bankC: 7000 },
  { date: "2024-06-11", bankA: 7000, bankB: 6000, bankC: 4000 },
  { date: "2024-06-12", bankA: 24000, bankB: 20000, bankC: 15000 },
  { date: "2024-06-13", bankA: 6000, bankB: 5000, bankC: 3000 },
  { date: "2024-06-14", bankA: 20000, bankB: 17000, bankC: 12000 },
  { date: "2024-06-15", bankA: 18000, bankB: 15000, bankC: 11000 },
  { date: "2024-06-16", bankA: 19000, bankB: 16000, bankC: 11000 },
  { date: "2024-06-17", bankA: 25000, bankB: 21000, bankC: 16000 },
  { date: "2024-06-18", bankA: 8000, bankB: 7000, bankC: 5000 },
  { date: "2024-06-19", bankA: 18000, bankB: 15000, bankC: 11000 },
  { date: "2024-06-20", bankA: 21000, bankB: 18000, bankC: 13000 },
  { date: "2024-06-21", bankA: 13000, bankB: 11000, bankC: 8000 },
  { date: "2024-06-22", bankA: 17000, bankB: 14000, bankC: 10000 },
  { date: "2024-06-23", bankA: 24000, bankB: 20000, bankC: 15000 },
  { date: "2024-06-24", bankA: 10000, bankB: 8000, bankC: 6000 },
  { date: "2024-06-25", bankA: 11000, bankB: 9000, bankC: 6000 },
  { date: "2024-06-26", bankA: 20000, bankB: 17000, bankC: 12000 },
  { date: "2024-06-27", bankA: 22000, bankB: 18000, bankC: 13000 },
  { date: "2024-06-28", bankA: 12000, bankB: 10000, bankC: 7000 },
  { date: "2024-06-29", bankA: 8000, bankB: 7000, bankC: 5000 },
  { date: "2024-06-30", bankA: 21000, bankB: 18000, bankC: 13000 }
]

const chartConfig = {
  transactions: {
    label: "Transactions",
  },
  bankA: {
    label: "Bank A",
    color: "hsl(var(--chart-1))",
  },
  bankB: {
    label: "Bank B",
    color: "hsl(var(--chart-2))",
  },
  bankC: {
    label: "Bank C",
    color: "hsl(var(--chart-3))",
  },
} satisfies ChartConfig

export function ChartAreaInteractive() {
  const isMobile = useIsMobile()
  const [timeRange, setTimeRange] = React.useState("30d")

  React.useEffect(() => {
    if (isMobile) {
      setTimeRange("7d")
    }
  }, [isMobile])

  const filteredData = chartData.filter((item) => {
    const date = new Date(item.date)
    const referenceDate = new Date("2024-06-30")
    let daysToSubtract = 90
    if (timeRange === "30d") {
      daysToSubtract = 30
    } else if (timeRange === "7d") {
      daysToSubtract = 7
    }
    const startDate = new Date(referenceDate)
    startDate.setDate(startDate.getDate() - daysToSubtract)
    return date >= startDate
  })

  return (
    <Card className="@container/card">
      <CardHeader className="relative">
        <CardTitle>Bank Account Activity</CardTitle>
        <CardDescription>
          <span className="@[540px]/card:block hidden">Transaction frequency across your banks</span>
          <span className="@[540px]/card:hidden">Transaction activity</span>
        </CardDescription>
        <div className="absolute right-4 top-4">
          <ToggleGroup
            type="single"
            value={timeRange}
            onValueChange={setTimeRange}
            variant="outline"
            className="@[767px]/card:flex hidden"
          >
            <ToggleGroupItem value="90d" className="h-8 px-2.5">
              Last 3 months
            </ToggleGroupItem>
            <ToggleGroupItem value="30d" className="h-8 px-2.5">
              Last 30 days
            </ToggleGroupItem>
            <ToggleGroupItem value="7d" className="h-8 px-2.5">
              Last 7 days
            </ToggleGroupItem>
          </ToggleGroup>
          <Select value={timeRange} onValueChange={setTimeRange}>
            <SelectTrigger className="@[767px]/card:hidden flex w-40" aria-label="Select a value">
              <SelectValue placeholder="Last 3 months" />
            </SelectTrigger>
            <SelectContent className="rounded-xl">
              <SelectItem value="90d" className="rounded-lg">
                Last 3 months
              </SelectItem>
              <SelectItem value="30d" className="rounded-lg">
                Last 30 days
              </SelectItem>
              <SelectItem value="7d" className="rounded-lg">
                Last 7 days
              </SelectItem>
            </SelectContent>
          </Select>
        </div>
      </CardHeader>
      <CardContent className="px-2 pt-4 sm:px-6 sm:pt-6">
        <ChartContainer config={chartConfig} className="aspect-auto h-[250px] w-full">
          <AreaChart data={filteredData}>
            <defs>
              <linearGradient id="fillBankA" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="var(--color-bankA)" stopOpacity={1.0} />
                <stop offset="95%" stopColor="var(--color-bankA)" stopOpacity={0.1} />
              </linearGradient>
              <linearGradient id="fillBankB" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="var(--color-bankB)" stopOpacity={0.8} />
                <stop offset="95%" stopColor="var(--color-bankB)" stopOpacity={0.1} />
              </linearGradient>
              <linearGradient id="fillBankC" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="var(--color-bankC)" stopOpacity={0.8} />
                <stop offset="95%" stopColor="var(--color-bankC)" stopOpacity={0.1} />
              </linearGradient>
            </defs>
            <CartesianGrid vertical={false} />
            <XAxis
              dataKey="date"
              tickLine={false}
              axisLine={false}
              tickMargin={8}
              minTickGap={32}
              tickFormatter={(value) => {
                const date = new Date(value)
                return date.toLocaleDateString("en-US", {
                  month: "short",
                  day: "numeric",
                })
              }}
            />
            <ChartTooltip
              cursor={false}
              content={
                <ChartTooltipContent
                  labelFormatter={(value) => {
                    return new Date(value).toLocaleDateString("en-US", {
                      month: "short",
                      day: "numeric",
                    })
                  }}
                  indicator="dot"
                />
              }
            />
            <Area dataKey="bankA" type="natural" fill="url(#fillBankA)" stroke="var(--color-bankA)" stackId="a" />
            <Area dataKey="bankB" type="natural" fill="url(#fillBankB)" stroke="var(--color-bankB)" stackId="a" />
            <Area dataKey="bankC" type="natural" fill="url(#fillBankC)" stroke="var(--color-bankC)" stackId="a" />
          </AreaChart>
        </ChartContainer>
      </CardContent>
    </Card>
  )
}