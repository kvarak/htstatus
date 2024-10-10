import { useState } from "react";
import Header from "@/components/layout/Header";
import Sidebar from "@/components/layout/Sidebar";
import { mockUser } from "@/data/mockData";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Calendar as CalendarIcon } from "lucide-react";

export default function Calendar() {
  const [user] = useState(mockUser);

  return (
    <div className="min-h-screen bg-background">
      <Header user={user} />
      
      <div className="flex">
        <aside className="hidden lg:block w-64 border-r bg-card shadow-sm">
          <Sidebar />
        </aside>
        
        <main className="flex-1 p-6">
          <div className="max-w-7xl mx-auto space-y-6">
            <div className="text-center py-20">
              <CalendarIcon className="h-16 w-16 mx-auto mb-4 text-muted-foreground" />
              <h1 className="text-3xl font-bold mb-4">Match Calendar</h1>
              <p className="text-muted-foreground mb-8">
                Calendar view with upcoming matches, training sessions, and important team events.
                Integration with Hattrick match schedule coming soon!
              </p>
              <Button variant="pitch" size="lg">
                <CalendarIcon className="h-4 w-4 mr-2" />
                View Schedule
              </Button>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}