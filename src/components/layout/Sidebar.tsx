import { Link, useLocation } from "react-router-dom"
import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"
import {
  Home,
  Users,
  Trophy,
  TrendingUp,
  BarChart3,
  Target,
  Calendar,
  User,
  Settings,
} from "lucide-react"

const navigation = [
  { name: "Dashboard", href: "/", icon: Home },
  { name: "Players", href: "/players", icon: Users },
  { name: "Matches", href: "/matches", icon: Trophy },
  { name: "Training", href: "/training", icon: TrendingUp },
  { name: "Analytics", href: "/analytics", icon: BarChart3 },
  { name: "Groups", href: "/groups", icon: Target },
  { name: "Calendar", href: "/calendar", icon: Calendar },
]

const secondaryNavigation = [
  { name: "Profile", href: "/profile", icon: User },
  { name: "Settings", href: "/settings", icon: Settings },
]

export default function Sidebar() {
  const location = useLocation()

  return (
    <div className="flex h-full flex-col">
      <div className="flex flex-1 flex-col overflow-y-auto pt-5 pb-4">
        <nav className="mt-5 flex-1 space-y-1 px-2">
          {navigation.map((item) => {
            const isActive = location.pathname === item.href
            return (
              <Link key={item.name} to={item.href}>
                <Button
                  variant={isActive ? "secondary" : "ghost"}
                  className={cn(
                    "w-full justify-start",
                    isActive
                      ? "bg-accent text-accent-foreground"
                      : "text-muted-foreground hover:text-foreground"
                  )}
                >
                  <item.icon className="mr-3 h-4 w-4" />
                  {item.name}
                </Button>
              </Link>
            )
          })}

          <div className="pt-4">
            <div className="px-3 py-2">
              <h3 className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                Account
              </h3>
            </div>
            {secondaryNavigation.map((item) => {
              const isActive = location.pathname === item.href
              return (
                <Link key={item.name} to={item.href}>
                  <Button
                    variant={isActive ? "secondary" : "ghost"}
                    className={cn(
                      "w-full justify-start",
                      isActive
                        ? "bg-accent text-accent-foreground"
                        : "text-muted-foreground hover:text-foreground"
                    )}
                  >
                    <item.icon className="mr-3 h-4 w-4" />
                    {item.name}
                  </Button>
                </Link>
              )
            })}
          </div>
        </nav>
      </div>
    </div>
  )
}
