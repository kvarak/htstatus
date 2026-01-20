import { useState } from "react";
import Header from "@/components/layout/Header";
import Sidebar from "@/components/layout/Sidebar";
import StatCard from "@/components/dashboard/StatCard";
import RecentMatches from "@/components/dashboard/RecentMatches";
import TopPlayers from "@/components/dashboard/TopPlayers";
import { mockUser, mockMatches, mockPlayers } from "@/data/mockData";
import {
  Users,
  Trophy,
  TrendingUp,
  Target,
  Calendar,
  BarChart3,
  Star,
  Activity
} from "lucide-react";

const Index = () => {
  const [user] = useState(mockUser);
  const [matches] = useState(mockMatches);
  const [players] = useState(mockPlayers);

  // Calculate dashboard statistics
  const totalPlayers = players.length;
  const totalMatches = matches.length;
  const averageAge = Math.round(players.reduce((sum, p) => sum + p.age_years, 0) / players.length);
  const averageTSI = Math.round(players.reduce((sum, p) => sum + p.tsi, 0) / players.length);

  return (
    <div className="min-h-screen bg-background">
      <Header user={user} />

      <div className="flex">
        <aside className="hidden lg:block w-64 border-r bg-card shadow-sm">
          <Sidebar />
        </aside>

        <main className="flex-1 p-6">
          <div className="max-w-7xl mx-auto space-y-6">
            {/* Header Section */}
            <div className="space-y-2">
              <h1 className="text-3xl font-bold text-foreground">
                Welcome back, {user.username}! ⚽
              </h1>
              <p className="text-muted-foreground">
                Here's what's happening with your team today.
              </p>
            </div>

            {/* Stats Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              <StatCard
                title="Total Players"
                value={totalPlayers}
                change={5.2}
                changeType="increase"
                icon={Users}
                description="Active squad members"
              />
              <StatCard
                title="Recent Matches"
                value={totalMatches}
                icon={Trophy}
                description="This season"
              />
              <StatCard
                title="Average Age"
                value={`${averageAge} years`}
                icon={Calendar}
                description="Squad average"
              />
              <StatCard
                title="Average TSI"
                value={averageTSI.toLocaleString()}
                change={3.7}
                changeType="increase"
                icon={TrendingUp}
                description="Team skill index"
              />
            </div>

            {/* Content Grid */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <RecentMatches matches={matches.slice(0, 3)} />
              <TopPlayers players={players} />
            </div>
          </div>
        </main>
      </div>
    </div>
  );
};

export default Index;
