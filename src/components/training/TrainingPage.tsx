import React, { useState, useMemo } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from "recharts"

interface PlayerSkill {
  date: string
  keeper: number
  defender: number
  playmaker: number
  winger: number
  passing: number
  scoring: number
  set_pieces: number
}

interface Player {
  ht_id: number
  name: string
  number: number
  skillHistory: PlayerSkill[]
}

const SKILL_LABELS = {
  keeper: "Keeper",
  defender: "Defender",
  playmaker: "Playmaker",
  winger: "Winger",
  passing: "Passing",
  scoring: "Scoring",
  set_pieces: "Set Pieces",
}

const SKILL_COLORS = {
  keeper: "#3b82f6",
  defender: "#ef4444",
  playmaker: "#8b5cf6",
  winger: "#ec4899",
  passing: "#14b8a6",
  scoring: "#f59e0b",
  set_pieces: "#6366f1",
}

interface TrainingPageProps {
  players: Player[]
  teamName: string
}

export default function TrainingPage({ players, teamName }: TrainingPageProps) {
  const [searchQuery, setSearchQuery] = useState("")
  const [selectedPlayer, setSelectedPlayer] = useState<number | null>(
    players.length > 0 ? players[0].ht_id : null
  )
  const [expandedPlayers, setExpandedPlayers] = useState<Set<number>>(new Set())

  // Filter players based on search
  const filteredPlayers = useMemo(
    () =>
      players.filter(
        (p) =>
          p.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
          p.number.toString().includes(searchQuery)
      ),
    [players, searchQuery]
  )

  // Get current player data
  const currentPlayer = useMemo(
    () => players.find((p) => p.ht_id === selectedPlayer),
    [players, selectedPlayer]
  )

  // Format chart data
  const chartData = useMemo(() => {
    if (!currentPlayer) return []
    return currentPlayer.skillHistory.map((entry) => ({
      date: new Date(entry.date).toLocaleDateString("en-US", {
        year: "2-digit",
        month: "2-digit",
      }),
      ...entry,
    }))
  }, [currentPlayer])

  // Calculate skill improvements
  const skillImprovements = useMemo(() => {
    if (!currentPlayer || currentPlayer.skillHistory.length < 2) {
      return Object.fromEntries(Object.keys(SKILL_LABELS).map((key) => [key, 0]))
    }

    const latest = currentPlayer.skillHistory[currentPlayer.skillHistory.length - 1]
    const earliest = currentPlayer.skillHistory[0]

    return {
      keeper: (latest.keeper || 0) - (earliest.keeper || 0),
      defender: (latest.defender || 0) - (earliest.defender || 0),
      playmaker: (latest.playmaker || 0) - (earliest.playmaker || 0),
      winger: (latest.winger || 0) - (earliest.winger || 0),
      passing: (latest.passing || 0) - (earliest.passing || 0),
      scoring: (latest.scoring || 0) - (earliest.scoring || 0),
      set_pieces: (latest.set_pieces || 0) - (earliest.set_pieces || 0),
    }
  }, [currentPlayer])

  // Deduplicate consecutive rows with identical skill values
  const deduplicatedChartData = useMemo(() => {
    if (chartData.length === 0) return []

    const deduped: typeof chartData = [chartData[0]]

    for (let i = 1; i < chartData.length; i++) {
      const current = chartData[i]
      const previous = deduped[deduped.length - 1]

      // Compare all skill values (not date)
      let skillsChanged = false
      for (const key of Object.keys(SKILL_LABELS)) {
        if (current[key as keyof typeof current] !== previous[key as keyof typeof previous]) {
          skillsChanged = true
          break
        }
      }

      // Only add if skills changed
      if (skillsChanged) {
        deduped.push(current)
      }
    }

    return deduped
  }, [chartData])

  const togglePlayerExpanded = (ht_id: number) => {
    const newExpanded = new Set(expandedPlayers)
    if (newExpanded.has(ht_id)) {
      newExpanded.delete(ht_id)
    } else {
      newExpanded.add(ht_id)
    }
    setExpandedPlayers(newExpanded)
  }

  return (
    <div className="w-full max-w-7xl mx-auto p-4 space-y-6">
      {/* Header */}
      <div className="space-y-2">
        <h1 className="text-3xl font-bold tracking-tight">Training Management</h1>
        <p className="text-gray-600">{teamName} - Player skill progression tracking</p>
      </div>

      {/* Search and Filter */}
      <Card>
        <CardHeader>
          <CardTitle>Players</CardTitle>
          <CardDescription>Search and select players to view skill progression</CardDescription>
        </CardHeader>
        <CardContent>
          <Input
            placeholder="Search by name or number..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="max-w-sm"
            aria-label="Search players"
          />
        </CardContent>
      </Card>

      {/* Player List and Details */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Player List */}
        <Card className="lg:col-span-1 h-fit">
          <CardHeader>
            <CardTitle>Squad</CardTitle>
            <CardDescription>{filteredPlayers.length} players</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-2 max-h-96 overflow-y-auto">
              {filteredPlayers.length === 0 ? (
                <p className="text-sm text-gray-500">No players found</p>
              ) : (
                filteredPlayers.map((player) => (
                  <Button
                    key={player.ht_id}
                    variant={selectedPlayer === player.ht_id ? "default" : "outline"}
                    className="w-full justify-start"
                    onClick={() => setSelectedPlayer(player.ht_id)}
                  >
                    <span className="truncate">
                      {player.number}. {player.name}
                    </span>
                    {skillImprovements[Object.keys(SKILL_LABELS)[0] as keyof typeof SKILL_LABELS] > 0 && (
                      <Badge variant="secondary" className="ml-2">
                        +{skillImprovements[Object.keys(SKILL_LABELS)[0] as keyof typeof SKILL_LABELS]}
                      </Badge>
                    )}
                  </Button>
                ))
              )}
            </div>
          </CardContent>
        </Card>

        {/* Player Details */}
        <div className="lg:col-span-2 space-y-6">
          {currentPlayer ? (
            <>
              {/* Current Skills Summary */}
              <Card>
                <CardHeader>
                  <CardTitle>{currentPlayer.name}</CardTitle>
                  <CardDescription>Current skill levels and improvements</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-4">
                    {Object.entries(SKILL_LABELS).map(([key, label]) => {
                      const latestSkill =
                        currentPlayer.skillHistory.length > 0
                          ? currentPlayer.skillHistory[currentPlayer.skillHistory.length - 1][
                              key as keyof PlayerSkill
                            ]
                          : 0
                      const improvement =
                        skillImprovements[key as keyof typeof skillImprovements]

                      return (
                        <div
                          key={key}
                          className="flex flex-col items-center p-3 rounded-lg border bg-gray-50"
                        >
                          <span className="text-xs font-medium text-gray-600 mb-1">{label}</span>
                          <span className="text-2xl font-bold text-blue-600">{latestSkill}</span>
                          {improvement !== 0 && (
                            <span
                              className={`text-xs font-semibold ${
                                improvement > 0 ? "text-green-600" : "text-red-600"
                              }`}
                            >
                              {improvement > 0 ? "+" : ""}{improvement}
                            </span>
                          )}
                        </div>
                      )
                    })}
                  </div>
                </CardContent>
              </Card>

              {/* Skill Progression Chart */}
              {chartData.length > 0 && (
                <Card>
                  <CardHeader>
                    <CardTitle>Skill Progression</CardTitle>
                    <CardDescription>
                      {currentPlayer.skillHistory.length} data points recorded
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <ResponsiveContainer width="100%" height={300}>
                      <LineChart data={chartData}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="date" />
                        <YAxis />
                        <Tooltip />
                        <Legend />
                        {Object.entries(SKILL_COLORS).map(([key, color]) => (
                          <Line
                            key={key}
                            type="monotone"
                            dataKey={key}
                            stroke={color}
                            name={SKILL_LABELS[key as keyof typeof SKILL_LABELS]}
                            dot={false}
                            isAnimationActive={false}
                          />
                        ))}
                      </LineChart>
                    </ResponsiveContainer>
                  </CardContent>
                </Card>
              )}

              {/* Detailed History Table */}
              {chartData.length > 0 && (
                <Card>
                  <CardHeader>
                    <CardTitle>Training History</CardTitle>
                    <CardDescription>
                      {deduplicatedChartData.length} of {chartData.length} unique skill updates
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="overflow-x-auto">
                      <Table>
                        <TableHeader>
                          <TableRow>
                            <TableHead>Date</TableHead>
                            {Object.values(SKILL_LABELS).map((label) => (
                              <TableHead key={label} className="text-right">
                                {label}
                              </TableHead>
                            ))}
                          </TableRow>
                        </TableHeader>
                        <TableBody>
                          {deduplicatedChartData.map((entry, idx) => (
                            <TableRow key={idx}>
                              <TableCell className="font-medium">{entry.date}</TableCell>
                              {Object.keys(SKILL_LABELS).map((key) => (
                                <TableCell key={key} className="text-right">
                                  {entry[key as keyof typeof entry]}
                                </TableCell>
                              ))}
                            </TableRow>
                          ))}
                        </TableBody>
                      </Table>
                    </div>
                  </CardContent>
                </Card>
              )}
            </>
          ) : (
            <Card>
              <CardContent className="pt-6">
                <p className="text-gray-500 text-center">Select a player to view details</p>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  )
}
