import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Trophy, Clock, MapPin } from "lucide-react"

interface Match {
  id: number
  datetime: string
  type: string
  home_team: string
  away_team: string
  home_goals: number
  away_goals: number
  is_home: boolean
  venue: string
  formation: string
}

interface RecentMatchesProps {
  matches: Match[]
}

export default function RecentMatches({ matches }: RecentMatchesProps) {
  return (
    <Card className="h-fit">
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-base font-medium">Recent Matches</CardTitle>
        <Trophy className="h-4 w-4 text-muted-foreground" />
      </CardHeader>
      <CardContent className="space-y-4">
        {matches.map((match) => {
          const result = match.is_home
            ? `${match.home_goals}-${match.away_goals}`
            : `${match.away_goals}-${match.home_goals}`

          const opponent = match.is_home ? match.away_team : match.home_team

          const isWin = match.is_home
            ? match.home_goals > match.away_goals
            : match.away_goals > match.home_goals

          const isDraw = match.home_goals === match.away_goals

          return (
            <div
              key={match.id}
              className="flex items-center justify-between p-4 rounded-lg border bg-card hover:bg-accent/50 transition-colors"
            >
              <div className="flex-1">
                <div className="flex items-center justify-between mb-2">
                  <div className="text-sm font-medium">
                    vs {opponent}
                  </div>
                  <Badge variant="outline" className="text-xs">
                    {match.type}
                  </Badge>
                </div>
                <div className="flex items-center gap-4 text-sm text-muted-foreground">
                  <div className="flex items-center gap-1">
                    <Clock className="h-3 w-3" />
                    {new Date(match.datetime).toLocaleDateString()}
                  </div>
                  <div className="flex items-center gap-1">
                    <MapPin className="h-3 w-3" />
                    {match.is_home ? "Home" : "Away"}
                  </div>
                </div>
              </div>
              <div className="text-right">
                <div className={`text-lg font-bold ${
                  isWin ? 'text-success' : isDraw ? 'text-warning' : 'text-destructive'
                }`}>
                  {result}
                </div>
                <div className="text-xs text-muted-foreground">
                  {match.formation}
                </div>
              </div>
            </div>
          )
        })}
      </CardContent>
    </Card>
  )
}
