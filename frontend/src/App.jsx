// frontend/src/App.jsx

import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { AuthProvider } from './features/auth/AuthContext'
import RequireAuth from './features/auth/RequireAuth'
import OpsRequireAuth from './features/ops/OpsRequireAuth'
import Navbar from './components/Navbar'
import LandingPage from './pages/LandingPage'
import QuoteEstimator from './features/quote/QuoteEstimator'
import BookingPage from './features/booking/BookingPage'
import DashboardPage from './features/dashboard/DashboardPage'
import LoginPage from './features/auth/LoginPage'
import RegisterPage from './features/auth/RegisterPage'
import OpsShell from './features/ops/OpsShell'
import OpsLoginPage from './features/ops/OpsLoginPage'
import OpsDashboard from './features/ops/pages/OpsDashboard'
import OpsBookings from './features/ops/pages/OpsBookings'
import OpsBookingDetail from './features/ops/pages/OpsBookingDetail'
import OpsSchedule from './features/ops/pages/OpsSchedule'
import OpsAnalytics from './features/ops/pages/OpsAnalytics'

const queryClient = new QueryClient({
  defaultOptions: { queries: { retry: 1, staleTime: 30_000 } },
})

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <BrowserRouter>
          <Routes>
            {/* Customer-facing — Navbar included */}
            <Route path="/" element={<><Navbar /><LandingPage /></>} />
            <Route path="/quote" element={<><Navbar /><QuoteEstimator /></>} />
            <Route path="/login" element={<><Navbar /><LoginPage /></>} />
            <Route path="/register" element={<><Navbar /><RegisterPage /></>} />
            <Route path="/book" element={<><Navbar /><RequireAuth><BookingPage /></RequireAuth></>} />
            <Route path="/dashboard" element={<><Navbar /><RequireAuth><DashboardPage /></RequireAuth></>} />

            {/* Ops — no customer Navbar, own shell */}
            <Route path="/ops/login" element={<OpsLoginPage />} />
            <Route path="/ops" element={<OpsRequireAuth><OpsShell /></OpsRequireAuth>}>
              <Route index element={<OpsDashboard />} />
              <Route path="bookings" element={<OpsBookings />} />
              <Route path="bookings/:id" element={<OpsBookingDetail />} />
              <Route path="schedule" element={<OpsSchedule />} />
              <Route path="analytics" element={<OpsAnalytics />} />
            </Route>
          </Routes>
        </BrowserRouter>
      </AuthProvider>
    </QueryClientProvider>
  )
}