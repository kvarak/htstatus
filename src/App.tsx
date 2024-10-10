import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { ThemeProvider } from 'next-themes'
import Index from '@/pages/Index'
import Players from '@/pages/Players'
import Matches from '@/pages/Matches'
import Training from '@/pages/Training'
import Analytics from '@/pages/Analytics'
import Groups from '@/pages/Groups'
import Calendar from '@/pages/Calendar'
import Profile from '@/pages/Profile'
import Settings from '@/pages/Settings'

function App() {
  return (
    <ThemeProvider attribute="class" defaultTheme="light" enableSystem>
      <Router>
        <Routes>
          <Route path="/" element={<Index />} />
          <Route path="/players" element={<Players />} />
          <Route path="/matches" element={<Matches />} />
          <Route path="/training" element={<Training />} />
          <Route path="/analytics" element={<Analytics />} />
          <Route path="/groups" element={<Groups />} />
          <Route path="/calendar" element={<Calendar />} />
          <Route path="/profile" element={<Profile />} />
          <Route path="/settings" element={<Settings />} />
        </Routes>
      </Router>
    </ThemeProvider>
  )
}

export default App