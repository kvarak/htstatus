import { useState } from "react";
import Header from "@/components/layout/Header";
import Sidebar from "@/components/layout/Sidebar";
import { mockUser, mockPlayerGroups, mockPlayers } from "@/data/mockData";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Target, Plus, Users, Edit, Trash2 } from "lucide-react";

export default function Groups() {
  const [user] = useState(mockUser);
  const [groups] = useState(mockPlayerGroups);
  const [players] = useState(mockPlayers);

  // Mock player assignments to groups
  const getPlayersInGroup = (groupId: number) => {
    // For demo purposes, assign players to groups based on simple logic
    switch (groupId) {
      case 1: // Starters
        return players.filter(p => p.tsi > 7000);
      case 2: // Substitutes
        return players.filter(p => p.tsi >= 6000 && p.tsi <= 7000);
      case 3: // Youth Prospects
        return players.filter(p => p.age_years < 23);
      case 4: // Transfer List
        return players.filter(p => p.is_transfer_listed);
      default:
        return [];
    }
  };

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
                  <Target className="h-8 w-8 text-primary" />
                  Player Groups
                </h1>
                <p className="text-muted-foreground">
                  Organize your players into custom groups for better management
                </p>
              </div>
              <Button variant="pitch" size="lg">
                <Plus className="h-4 w-4 mr-2" />
                Create Group
              </Button>
            </div>

            {/* Stats Overview */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <Card className="shadow-card">
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium text-muted-foreground flex items-center gap-2">
                    <Target className="h-4 w-4" />
                    Total Groups
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{groups.length}</div>
                </CardContent>
              </Card>

              <Card className="shadow-card">
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium text-muted-foreground">
                    Active Players
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{players.length}</div>
                  <div className="text-xs text-muted-foreground">
                    In squad
                  </div>
                </CardContent>
              </Card>

              <Card className="shadow-card">
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium text-muted-foreground">
                    Starters
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold text-success">
                    {getPlayersInGroup(1).length}
                  </div>
                  <div className="text-xs text-muted-foreground">
                    First team
                  </div>
                </CardContent>
              </Card>

              <Card className="shadow-card">
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium text-muted-foreground">
                    Youth Prospects
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold text-primary">
                    {getPlayersInGroup(3).length}
                  </div>
                  <div className="text-xs text-muted-foreground">
                    Under 23
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Groups Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {groups.map((group) => {
                const playersInGroup = getPlayersInGroup(group.id);

                return (
                  <Card key={group.id} className="shadow-card hover:shadow-football transition-shadow">
                    <CardHeader
                      className="pb-4"
                      style={{
                        backgroundColor: group.bgcolor,
                        color: group.textcolor
                      }}
                    >
                      <div className="flex items-center justify-between">
                        <CardTitle className="flex items-center gap-2">
                          <Target className="h-5 w-5" />
                          {group.name}
                        </CardTitle>
                        <div className="flex items-center gap-2">
                          <Button
                            variant="ghost"
                            size="sm"
                            className="h-8 w-8 p-0 hover:bg-white/20"
                          >
                            <Edit className="h-4 w-4" />
                          </Button>
                          <Button
                            variant="ghost"
                            size="sm"
                            className="h-8 w-8 p-0 hover:bg-white/20"
                          >
                            <Trash2 className="h-4 w-4" />
                          </Button>
                        </div>
                      </div>
                    </CardHeader>

                    <CardContent className="space-y-4">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <Users className="h-4 w-4 text-muted-foreground" />
                          <span className="text-sm font-medium">
                            {playersInGroup.length} players
                          </span>
                        </div>
                        <Badge variant="outline">
                          Order: {group.order}
                        </Badge>
                      </div>

                      {playersInGroup.length > 0 ? (
                        <div className="space-y-2">
                          <h4 className="text-sm font-medium text-muted-foreground">Players:</h4>
                          <div className="space-y-2 max-h-48 overflow-y-auto">
                            {playersInGroup.map((player) => (
                              <div
                                key={player.ht_id}
                                className="flex items-center justify-between p-2 rounded-md border bg-background/50"
                              >
                                <div className="flex items-center gap-2">
                                  <div className="w-6 h-6 rounded-full bg-primary text-primary-foreground text-xs flex items-center justify-center font-bold">
                                    {player.number}
                                  </div>
                                  <div>
                                    <div className="text-sm font-medium">
                                      {player.first_name} {player.last_name}
                                    </div>
                                    <div className="text-xs text-muted-foreground">
                                      Age {player.age_years} • TSI {player.tsi.toLocaleString()}
                                    </div>
                                  </div>
                                </div>
                                <div className="text-xs text-muted-foreground">
                                  Form: {player.form}/8
                                </div>
                              </div>
                            ))}
                          </div>
                        </div>
                      ) : (
                        <div className="text-center py-6 text-muted-foreground">
                          <Users className="h-8 w-8 mx-auto mb-2 opacity-50" />
                          <p className="text-sm">No players in this group</p>
                        </div>
                      )}

                      <div className="pt-2 border-t">
                        <Button variant="outline" size="sm" className="w-full">
                          <Plus className="h-3 w-3 mr-2" />
                          Add Players
                        </Button>
                      </div>
                    </CardContent>
                  </Card>
                );
              })}
            </div>

            {/* Create New Group Card */}
            <Card className="shadow-card border-dashed border-2 hover:border-primary/50 hover:bg-accent/20 transition-colors cursor-pointer">
              <CardContent className="flex flex-col items-center justify-center py-12">
                <div className="p-4 rounded-full bg-primary/10 mb-4">
                  <Plus className="h-8 w-8 text-primary" />
                </div>
                <h3 className="text-lg font-semibold mb-2">Create New Group</h3>
                <p className="text-muted-foreground text-center max-w-sm">
                  Organize your players by creating custom groups with specific roles and purposes.
                </p>
                <Button variant="pitch" className="mt-4">
                  <Plus className="h-4 w-4 mr-2" />
                  Create Group
                </Button>
              </CardContent>
            </Card>
          </div>
        </main>
      </div>
    </div>
  );
}
