import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Star, TrendingUp } from "lucide-react"

interface Player {
  id: number
  name: string
  age_years: number
  tsi: number
  form: number
  position: string
  skills: {
    keeper: number
    defending: number
    playmaker: number
    winger: number
    passing: number
    scorer: number
    set_pieces: number
  }
}

interface TopPlayersProps {
  players: Player[]
}

export default function TopPlayers({ players }: TopPlayersProps) {
  // Sort players by TSI and take top 5
  const topPlayers = [...players]
    .sort((a, b) => b.tsi - a.tsi)
    .slice(0, 5)

  const getBestSkill = (skills: Player["skills"]) => {
    const skillEntries = Object.entries(skills).filter(([key]) => key !== "keeper")
    const bestSkill = skillEntries.reduce((best, current) => 
      current[1] > best[1] ? current : best
    )
    return {
      name: bestSkill[0].charAt(0).toUpperCase() + bestSkill[0].slice(1),
      value: bestSkill[1]
    }
  }

  return (
    <Card className="h-fit">
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-base font-medium">Top Players</CardTitle>
        <Star className="h-4 w-4 text-muted-foreground" />
      </CardHeader>
      <CardContent className="space-y-4">
        {topPlayers.map((player, index) => {
          const bestSkill = getBestSkill(player.skills)
          return (
            <div key={player.id} className="flex items-center space-x-4">
              <div className="flex-shrink-0">
                <div className="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center">
                  <span className="text-sm font-semibold text-primary">
                    #{index + 1}
                  </span>
                </div>
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-foreground truncate">
                      {player.name}
                    </p>
                    <p className="text-xs text-muted-foreground">
                      {player.position} • {player.age_years}y
                    </p>
                  </div>
                  <div className="flex flex-col items-end">
                    <p className="text-sm font-semibold">
                      {player.tsi.toLocaleString()}
                    </p>
                    <Badge variant="outline" className="text-xs">
                      {bestSkill.name}: {bestSkill.value}
                    </Badge>
                  </div>
                </div>
                <div className="mt-1 flex items-center gap-2">
                  <div className="flex items-center gap-1 text-xs text-muted-foreground">
                    <TrendingUp className="h-3 w-3" />
                    Form: {player.form}
                  </div>
                </div>
              </div>
            </div>
          )
        })}
        <Button variant="outline" size="sm" className="w-full mt-4">
          View All Players
        </Button>
      </CardContent>
    </Card>
  )
}