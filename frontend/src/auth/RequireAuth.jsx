// frontend/src/features/auth/RequireAuth.jsx

import { Navigate, useLocation } from 'react-router-dom'
import { useAuth } from './AuthContext'

export default function RequireAuth({ children }) {
  const { user, loading } = useAuth()
  const location = useLocation()

  if (loading) return (
    <div className="min-h-screen flex items-center justify-center bg-cream">
      <Spinner />
    </div>
  )

  if (!user) return <Navigate to="/login" state={{ from: location }} replace />

  return children
}

function Spinner() {
  return (
    <div style={{
      width: 36, height: 36,
      border: '3px solid var(--cream-dark)',
      borderTopColor: 'var(--forest)',
      borderRadius: '50%',
      animation: 'spin 0.8s linear infinite',
    }} />
  )
}