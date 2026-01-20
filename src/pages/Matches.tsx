import { useState } from "react";
import Header from "@/components/layout/Header";
import Sidebar from "@/components/layout/Sidebar";
import { mockUser, mockMatches } from "@/data/mockData";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Trophy, Calendar, MapPin, Users, Target, Clock } from "lucide-react";
import { MATCH_TYPES } from "@/types";

export default function Matches() {
  const [user] = useState(mockUser);
  const [matches] = useState(mockMatches);

  // Sort matches by date (most recent first)
  const sortedMatches = [...matches].sort((a, b) =>
    new Date(b.datetime).getTime() - new Date(a.datetime).getTime()
  );

  const getMatchResult = (match: any) => {
    const isHome = match.home_team_id === user.ht_id;
    const teamGoals = isHome ? match.home_goals : match.away_goals;
    const opponentGoals = isHome ? match.away_goals : match.home_goals;

    if (teamGoals > opponentGoals) return { result: 'W', color: 'bg-success' };
    if (teamGoals < opponentGoals) return { result: 'L', color: 'bg-destructive' };
    return { result: 'D', color: 'bg-warning' };
  };

  const getOpponentName = (match: any) => {
    return match.home_team_id === user.ht_id ? match.away_team_name : match.home_team_name;
  };

  const getMatchLocation = (match: any) => {
    return match.home_team_id === user.ht_id ? 'Home' : 'Away';
  };

  // Calculate match statistics
  const totalMatches = matches.length;
  const wins = matches.filter(m => {
    const { result } = getMatchResult(m);
    return result === 'W';
  }).length;
  const draws = matches.filter(m => {
    const { result } = getMatchResult(m);
    return result === 'D';
  }).length;
  const losses = totalMatches - wins - draws;

  const totalGoalsScored = matches.reduce((sum, m) => {
    const isHome = m.home_team_id === user.ht_id;
    return sum + (isHome ? m.home_goals : m.away_goals);
  }, 0);

  const totalGoalsConceded = matches.reduce((sum, m) => {
    const isHome = m.home_team_id === user.ht_id;
    return sum + (isHome ? m.away_goals : m.home_goals);
  }, 0);

  return (
    <div className="min-h-screen bg-background">
      <Header user={user} />

      <div className="flex">
        <aside className="hidden lg:block w-64 border-r bg-card shadow-sm">
          <Sidebar />
        </aside>

        <main className="flex-1 p-6">
          <div className="max-w-7xl mx-auto space-y-6">
            {/* Header */}
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-3xl font-bold text-foreground flex items-center gap-2">
                  <Trophy className="h-8 w-8 text-primary" />
                  Matches
                </h1>
                <p className="text-muted-foreground">
                  Review your team's match history and performance
                </p>
              </div>
              <Button variant="pitch" size="lg">
                <Calendar className="h-4 w-4 mr-2" />
                View Calendar
              </Button>
            </div>

            {/* Stats Overview */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
              <Card className="shadow-card">
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium text-muted-foreground flex items-center gap-2">
                    <Trophy className="h-4 w-4" />
                    Total Matches
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{totalMatches}</div>
                </CardContent>
              </Card>

              <Card className="shadow-card">
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium text-muted-foreground">
                    Wins
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold text-success">{wins}</div>
                  <div className="text-xs text-muted-foreground">
                    {totalMatches > 0 ? Math.round((wins / totalMatches) * 100) : 0}% win rate
                  </div>
                </CardContent>
              </Card>

              <Card className="shadow-card">
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium text-muted-foreground">
                    Draws
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold text-warning">{draws}</div>
                  <div className="text-xs text-muted-foreground">
                    {totalMatches > 0 ? Math.round((draws / totalMatches) * 100) : 0}% draw rate
                  </div>
                </CardContent>
              </Card>

              <Card className="shadow-card">
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium text-muted-foreground">
                    Goals For
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold text-success">{totalGoalsScored}</div>
                  <div className="text-xs text-muted-foreground">
                    {totalMatches > 0 ? (totalGoalsScored / totalMatches).toFixed(1) : 0} avg/match
                  </div>
                </CardContent>
              </Card>

              <Card className="shadow-card">
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium text-muted-foreground">
                    Goals Against
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold text-destructive">{totalGoalsConceded}</div>
                  <div className="text-xs text-muted-foreground">
                    {totalMatches > 0 ? (totalGoalsConceded / totalMatches).toFixed(1) : 0} avg/match
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Match History */}
            <Card className="shadow-card">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Calendar className="h-5 w-5 text-primary" />
                  Match History
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {sortedMatches.length === 0 ? (
                  <div className="text-center py-12 text-muted-foreground">
                    <Trophy className="h-16 w-16 mx-auto mb-4 opacity-50" />
                    <h3 className="text-lg font-semibold mb-2">No matches found</h3>
                    <p>Your match history will appear here once you've played some games.</p>
                  </div>
                ) : (
                  sortedMatches.map((match) => {
                    const { result, color } = getMatchResult(match);
                    const opponent = getOpponentName(match);
                    const location = getMatchLocation(match);
                    const isHome = match.home_team_id === user.ht_id;
                    const teamGoals = isHome ? match.home_goals : match.away_goals;
                    const opponentGoals = isHome ? match.away_goals : match.home_goals;

                    return (
                      <div
                        key={match.ht_id}
                        className="flex items-center justify-between p-4 rounded-lg border bg-card hover:bg-accent/50 transition-colors"
                      >
                        <div className="flex items-center gap-4">
                          <div className={`w-8 h-8 rounded-full ${color} flex items-center justify-center text-white font-bold text-sm`}>
                            {result}
                          </div>

                          <div className="flex-1 min-w-0">
                            <div className="flex items-center gap-2 mb-1">
                              <h4 className="font-medium">
                                vs {opponent}
                              </h4>
                              <Badge variant="outline" className="text-xs">
                                {MATCH_TYPES[match.matchtype as keyof typeof MATCH_TYPES] || "Unknown"}
                              </Badge>
                            </div>

                            <div className="flex items-center gap-4 text-sm text-muted-foreground">
                              <div className="flex items-center gap-1">
                                <Clock className="h-3 w-3" />
                                {new Date(match.datetime).toLocaleDateString('en-US', {
                                  weekday: 'short',
                                  month: 'short',
                                  day: 'numeric',
                                  hour: '2-digit',
                                  minute: '2-digit'
                                })}
                              </div>
                              <div className="flex items-center gap-1">
                                <MapPin className="h-3 w-3" />
                                {location}
                              </div>
                            </div>
                          </div>
                        </div>

                        <div className="text-right">
                          <div className="text-lg font-bold">
                            {teamGoals} - {opponentGoals}
                          </div>
                          <div className="text-xs text-muted-foreground">
                            Final Score
                          </div>
                        </div>
                      </div>
                    );
                  })
                )}
              </CardContent>
            </Card>
          </div>
        </main>
      </div>
    </div>
  );
}
