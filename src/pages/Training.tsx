import { useState, useEffect } from "react";
import Header from "@/components/layout/Header";
import Sidebar from "@/components/layout/Sidebar";
import { mockUser } from "@/data/mockData";
import TrainingPage from "@/components/training/TrainingPage";
import { Loader2 } from "lucide-react";

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

export default function Training() {
  const [user] = useState(mockUser);
  const [players, setPlayers] = useState<Player[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Fetch training data from the backend
    const fetchTrainingData = async () => {
      try {
        setLoading(true);
        const response = await fetch("/api/training");
        if (!response.ok) throw new Error("Failed to fetch training data");
        const data = await response.json();
        setPlayers(data.players || []);
        setError(null);
      } catch (err) {
        setError(err instanceof Error ? err.message : "An error occurred");
        setPlayers([]);
      } finally {
        setLoading(false);
      }
    };

    fetchTrainingData();
  }, []);

  return (
    <div className="min-h-screen bg-background">
      <Header user={user} />

      <div className="flex">
        <aside className="hidden lg:block w-64 border-r bg-card shadow-sm">
          <Sidebar />
        </aside>

        <main className="flex-1 overflow-auto">
          {loading ? (
            <div className="flex items-center justify-center h-screen">
              <div className="text-center">
                <Loader2 className="h-8 w-8 animate-spin mx-auto mb-4 text-blue-600" />
                <p className="text-muted-foreground">Loading training data...</p>
              </div>
            </div>
          ) : error ? (
            <div className="flex items-center justify-center h-screen">
              <div className="text-center">
                <p className="text-red-600 mb-4">Error: {error}</p>
                <p className="text-muted-foreground">Please refresh the page to try again.</p>
              </div>
            </div>
          ) : (
            <TrainingPage
              players={players}
              teamName={user?.team_name || "Team"}
            />
          )}
        </main>
      </div>
    </div>
  );
}
