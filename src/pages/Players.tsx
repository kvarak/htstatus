import { useState } from "react";
import Header from "@/components/layout/Header";
import Sidebar from "@/components/layout/Sidebar";
import { mockUser, mockPlayers } from "@/data/mockData";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Search, Filter, Users, Star, TrendingUp, Award } from "lucide-react";
import { Player } from "@/types";

const getSpecialtyName = (specialty: number): string => {
  const specialties: { [key: number]: string } = {
    0: "None",
    1: "Technical",
    2: "Quick",
    3: "Powerful",
    4: "Unpredictable",
    5: "Head specialist",
    6: "Regainer",
    7: "Support",
    8: "Resilient"
  };
  return specialties[specialty] || "Unknown";
};

const getPositionFromSkills = (player: Player): string => {
  const skills = {
    keeper: player.keeper,
    defender: player.defender,
    playmaker: player.playmaker,
    winger: player.winger,
    passing: player.passing,
    scorer: player.scorer
  };

  if (skills.keeper >= 6) return "GK";
  if (skills.defender >= 6) return "DEF";
  if (skills.playmaker >= 6) return "MID";
  if (skills.winger >= 6) return "WIN";
  if (skills.scorer >= 6) return "FWD";
  return "DEF";
};

export default function Players() {
  const [user] = useState(mockUser);
  const [players] = useState(mockPlayers);
  const [searchTerm, setSearchTerm] = useState("");
  const [positionFilter, setPositionFilter] = useState<string>("all");
  const [sortBy, setSortBy] = useState<string>("tsi");

  // Filter and sort players
  const filteredPlayers = players
    .filter(player => {
      const nameMatch = `${player.first_name} ${player.last_name}`.toLowerCase()
        .includes(searchTerm.toLowerCase());

      if (positionFilter === "all") return nameMatch;

      const position = getPositionFromSkills(player);
      return nameMatch && position === positionFilter;
    })
    .sort((a, b) => {
      switch (sortBy) {
        case "name":
          return `${a.first_name} ${a.last_name}`.localeCompare(`${b.first_name} ${b.last_name}`);
        case "age":
          return a.age_years - b.age_years;
        case "tsi":
          return b.tsi - a.tsi;
        case "form":
          return b.form - a.form;
        default:
          return 0;
      }
    });

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
                  <Users className="h-8 w-8 text-primary" />
                  Players
                </h1>
                <p className="text-muted-foreground">
                  Manage your team and player development
                </p>
              </div>
              <Button variant="pitch" size="lg">
                <TrendingUp className="h-4 w-4 mr-2" />
                Update Data
              </Button>
            </div>

            {/* Stats Cards */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="bg-card rounded-lg p-4 shadow-card">
                <div className="flex items-center gap-2 mb-2">
                  <Users className="h-4 w-4 text-primary" />
                  <span className="text-sm font-medium text-muted-foreground">Total Players</span>
                </div>
                <div className="text-2xl font-bold">{players.length}</div>
              </div>
              <div className="bg-card rounded-lg p-4 shadow-card">
                <div className="flex items-center gap-2 mb-2">
                  <Star className="h-4 w-4 text-warning" />
                  <span className="text-sm font-medium text-muted-foreground">Average Form</span>
                </div>
                <div className="text-2xl font-bold">
                  {(players.reduce((sum, p) => sum + p.form, 0) / players.length).toFixed(1)}/8
                </div>
              </div>
              <div className="bg-card rounded-lg p-4 shadow-card">
                <div className="flex items-center gap-2 mb-2">
                  <Award className="h-4 w-4 text-success" />
                  <span className="text-sm font-medium text-muted-foreground">Average TSI</span>
                </div>
                <div className="text-2xl font-bold">
                  {Math.round(players.reduce((sum, p) => sum + p.tsi, 0) / players.length).toLocaleString()}
                </div>
              </div>
              <div className="bg-card rounded-lg p-4 shadow-card">
                <div className="flex items-center gap-2 mb-2">
                  <TrendingUp className="h-4 w-4 text-primary" />
                  <span className="text-sm font-medium text-muted-foreground">Average Age</span>
                </div>
                <div className="text-2xl font-bold">
                  {Math.round(players.reduce((sum, p) => sum + p.age_years, 0) / players.length)} years
                </div>
              </div>
            </div>

            {/* Filters */}
            <div className="bg-card rounded-lg p-4 shadow-card">
              <div className="flex flex-col md:flex-row gap-4">
                <div className="flex-1 relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                  <Input
                    placeholder="Search players..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="pl-9"
                  />
                </div>
                <Select value={positionFilter} onValueChange={setPositionFilter}>
                  <SelectTrigger className="w-full md:w-48">
                    <SelectValue placeholder="Filter by position" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All Positions</SelectItem>
                    <SelectItem value="GK">Goalkeeper</SelectItem>
                    <SelectItem value="DEF">Defender</SelectItem>
                    <SelectItem value="MID">Midfielder</SelectItem>
                    <SelectItem value="WIN">Winger</SelectItem>
                    <SelectItem value="FWD">Forward</SelectItem>
                  </SelectContent>
                </Select>
                <Select value={sortBy} onValueChange={setSortBy}>
                  <SelectTrigger className="w-full md:w-48">
                    <SelectValue placeholder="Sort by" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="tsi">TSI (High to Low)</SelectItem>
                    <SelectItem value="name">Name (A-Z)</SelectItem>
                    <SelectItem value="age">Age (Young to Old)</SelectItem>
                    <SelectItem value="form">Form (High to Low)</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>

            {/* Players Table */}
            <div className="bg-card rounded-lg shadow-card overflow-hidden">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead className="w-12">#</TableHead>
                    <TableHead>Name</TableHead>
                    <TableHead>Position</TableHead>
                    <TableHead>Age</TableHead>
                    <TableHead>Form</TableHead>
                    <TableHead>TSI</TableHead>
                    <TableHead>Salary</TableHead>
                    <TableHead>Skills</TableHead>
                    <TableHead>Specialty</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {filteredPlayers.map((player) => (
                    <TableRow key={player.ht_id} className="hover:bg-accent/50">
                      <TableCell className="font-mono text-sm">
                        {player.number}
                      </TableCell>
                      <TableCell>
                        <div>
                          <div className="font-medium">
                            {player.first_name} {player.last_name}
                          </div>
                          {player.nick_name && (
                            <div className="text-xs text-muted-foreground">
                              "{player.nick_name}"
                            </div>
                          )}
                        </div>
                      </TableCell>
                      <TableCell>
                        <Badge variant="outline">
                          {getPositionFromSkills(player)}
                        </Badge>
                      </TableCell>
                      <TableCell>{player.age_years}</TableCell>
                      <TableCell>
                        <div className="flex items-center gap-1">
                          <Star className="h-3 w-3 text-warning" />
                          {player.form}/8
                        </div>
                      </TableCell>
                      <TableCell className="font-mono">
                        {player.tsi.toLocaleString()}
                      </TableCell>
                      <TableCell className="font-mono">
                        ${player.salary.toLocaleString()}
                      </TableCell>
                      <TableCell>
                        <div className="text-xs space-y-1">
                          <div>K:{player.keeper} D:{player.defender} P:{player.playmaker}</div>
                          <div>W:{player.winger} Pa:{player.passing} S:{player.scorer}</div>
                        </div>
                      </TableCell>
                      <TableCell>
                        {player.specialty > 0 && (
                          <Badge variant="secondary" className="text-xs">
                            {getSpecialtyName(player.specialty)}
                          </Badge>
                        )}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}
