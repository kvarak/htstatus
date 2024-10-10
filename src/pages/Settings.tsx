import { useState } from "react";
import Header from "@/components/layout/Header";
import Sidebar from "@/components/layout/Sidebar";
import { mockUser } from "@/data/mockData";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Settings as SettingsIcon } from "lucide-react";

export default function Settings() {
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
              <SettingsIcon className="h-16 w-16 mx-auto mb-4 text-muted-foreground" />
              <h1 className="text-3xl font-bold mb-4">Settings</h1>
              <p className="text-muted-foreground mb-8">
                Configure your HT Planner preferences, data sync settings, and application behavior.
                Advanced settings panel coming soon!
              </p>
              <Button variant="pitch" size="lg">
                <SettingsIcon className="h-4 w-4 mr-2" />
                Configure Settings
              </Button>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}