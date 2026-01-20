import { useState } from "react";
import Header from "@/components/layout/Header";
import Sidebar from "@/components/layout/Sidebar";
import { mockUser, mockPlayers, mockMatches } from "@/data/mockData";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { BarChart3, TrendingUp, Users, Trophy, Target, Activity } from "lucide-react";

export default function Analytics() {
  const [user] = useState(mockUser);
  const [players] = useState(mockPlayers);
  const [matches] = useState(mockMatches);

  // Calculate analytics data
  const totalPlayers = players.length;
  const avgAge = Math.round(players.reduce((sum, p) => sum + p.age_years, 0) / players.length);
  const avgTSI = Math.round(players.reduce((sum, p) => sum + p.tsi, 0) / players.length);
  const avgForm = (players.reduce((sum, p) => sum + p.form, 0) / players.length).toFixed(1);

  // Position distribution
  const positionDistribution = players.reduce((acc, player) => {
    if (player.keeper >= 6) acc.GK++;
    else if (player.defender >= 6) acc.DEF++;
    else if (player.playmaker >= 6) acc.MID++;
    else if (player.winger >= 6) acc.WIN++;
    else if (player.scorer >= 6) acc.FWD++;
    else acc.DEF++; // Default to defender
    return acc;
  }, { GK: 0, DEF: 0, MID: 0, WIN: 0, FWD: 0 });

  // Age distribution
  const ageGroups = players.reduce((acc, player) => {
    if (player.age_years < 20) acc.youth++;
    else if (player.age_years < 25) acc.young++;
    else if (player.age_years < 30) acc.prime++;
    else acc.veteran++;
    return acc;
  }, { youth: 0, young: 0, prime: 0, veteran: 0 });

  // Top performers
  const topTSI = [...players].sort((a, b) => b.tsi - a.tsi).slice(0, 3);
  const topForm = [...players].sort((a, b) => b.form - a.form).slice(0, 3);
  const topGoalscorers = [...players].sort((a, b) => b.career_goals - a.career_goals).slice(0, 3);

  // Match statistics
  const totalMatches = matches.length;
  const wins = matches.filter(m => {
    const isHome = m.home_team_id === user.ht_id;
    const teamGoals = isHome ? m.home_goals : m.away_goals;
    const opponentGoals = isHome ? m.away_goals : m.home_goals;
    return teamGoals > opponentGoals;
  }).length;

  const winRate = totalMatches > 0 ? Math.round((wins / totalMatches) * 100) : 0;

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
                  <BarChart3 className="h-8 w-8 text-primary" />
                  Analytics
                </h1>
                <p className="text-muted-foreground">
                  Deep insights into your team's performance and composition
                </p>
              </div>
              <Button variant="pitch" size="lg">
                <TrendingUp className="h-4 w-4 mr-2" />
                Export Report
              </Button>
            </div>

            {/* Key Metrics */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <Card className="shadow-card">
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium text-muted-foreground flex items-center gap-2">
                    <Users className="h-4 w-4" />
                    Squad Size
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{totalPlayers}</div>
                  <div className="text-xs text-muted-foreground">Active players</div>
                </CardContent>
              </Card>

              <Card className="shadow-card">
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium text-muted-foreground">
                    Average TSI
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{avgTSI.toLocaleString()}</div>
                  <div className="text-xs text-muted-foreground">Team skill index</div>
                </CardContent>
              </Card>

              <Card className="shadow-card">
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium text-muted-foreground">
                    Win Rate
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold text-success">{winRate}%</div>
                  <div className="text-xs text-muted-foreground">{wins}/{totalMatches} matches</div>
                </CardContent>
              </Card>

              <Card className="shadow-card">
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium text-muted-foreground">
                    Average Form
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{avgForm}/8</div>
                  <div className="text-xs text-muted-foreground">Squad fitness</div>
                </CardContent>
              </Card>
            </div>

            {/* Position & Age Analysis */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <Card className="shadow-card">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Target className="h-5 w-5 text-primary" />
                    Position Distribution
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  {Object.entries(positionDistribution).map(([position, count]) => (
                    <div key={position} className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <Badge variant="outline" className="w-12 justify-center">
                          {position}
                        </Badge>
                        <span className="text-sm font-medium">{position === 'GK' ? 'Goalkeepers' :
                          position === 'DEF' ? 'Defenders' :
                          position === 'MID' ? 'Midfielders' :
                          position === 'WIN' ? 'Wingers' : 'Forwards'}</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <div className="w-24 bg-muted rounded-full h-2 overflow-hidden">
                          <div
                            className="bg-primary h-full transition-all duration-500"
                            style={{ width: `${(count / totalPlayers) * 100}%` }}
                          />
                        </div>
                        <span className="text-sm font-bold w-8 text-right">{count}</span>
                      </div>
                    </div>
                  ))}
                </CardContent>
              </Card>

              <Card className="shadow-card">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Activity className="h-5 w-5 text-primary" />
                    Age Distribution
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  {[
                    { label: 'Youth (Under 20)', key: 'youth', color: 'bg-blue-500' },
                    { label: 'Young (20-24)', key: 'young', color: 'bg-green-500' },
                    { label: 'Prime (25-29)', key: 'prime', color: 'bg-yellow-500' },
                    { label: 'Veteran (30+)', key: 'veteran', color: 'bg-red-500' }
                  ].map(({ label, key, color }) => (
                    <div key={key} className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <div className={`w-3 h-3 rounded-full ${color}`} />
                        <span className="text-sm font-medium">{label}</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <div className="w-24 bg-muted rounded-full h-2 overflow-hidden">
                          <div
                            className={`${color} h-full transition-all duration-500`}
                            style={{ width: `${(ageGroups[key as keyof typeof ageGroups] / totalPlayers) * 100}%` }}
                          />
                        </div>
                        <span className="text-sm font-bold w-8 text-right">
                          {ageGroups[key as keyof typeof ageGroups]}
                        </span>
                      </div>
                    </div>
                  ))}
                </CardContent>
              </Card>
            </div>

            {/* Top Performers */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              <Card className="shadow-card">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <TrendingUp className="h-5 w-5 text-primary" />
                    Highest TSI
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  {topTSI.map((player, index) => (
                    <div key={player.ht_id} className="flex items-center gap-3">
                      <div className="w-6 h-6 rounded-full bg-primary text-primary-foreground text-xs flex items-center justify-center font-bold">
                        {index + 1}
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="text-sm font-medium truncate">
                          {player.first_name} {player.last_name}
                        </div>
                        <div className="text-xs text-muted-foreground">
                          Age {player.age_years}
                        </div>
                      </div>
                      <div className="text-sm font-bold">
                        {player.tsi.toLocaleString()}
                      </div>
                    </div>
                  ))}
                </CardContent>
              </Card>

              <Card className="shadow-card">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Activity className="h-5 w-5 text-success" />
                    Best Form
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  {topForm.map((player, index) => (
                    <div key={player.ht_id} className="flex items-center gap-3">
                      <div className="w-6 h-6 rounded-full bg-success text-success-foreground text-xs flex items-center justify-center font-bold">
                        {index + 1}
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="text-sm font-medium truncate">
                          {player.first_name} {player.last_name}
                        </div>
                        <div className="text-xs text-muted-foreground">
                          Age {player.age_years}
                        </div>
                      </div>
                      <div className="text-sm font-bold text-success">
                        {player.form}/8
                      </div>
                    </div>
                  ))}
                </CardContent>
              </Card>

              <Card className="shadow-card">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Trophy className="h-5 w-5 text-warning" />
                    Top Scorers
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  {topGoalscorers.map((player, index) => (
                    <div key={player.ht_id} className="flex items-center gap-3">
                      <div className="w-6 h-6 rounded-full bg-warning text-warning-foreground text-xs flex items-center justify-center font-bold">
                        {index + 1}
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="text-sm font-medium truncate">
                          {player.first_name} {player.last_name}
                        </div>
                        <div className="text-xs text-muted-foreground">
                          Age {player.age_years}
                        </div>
                      </div>
                      <div className="text-sm font-bold text-warning">
                        {player.career_goals}
                      </div>
                    </div>
                  ))}
                </CardContent>
              </Card>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}
