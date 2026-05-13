// frontend/src/features/ops/OpsRequireAuth.jsx

import { Navigate } from 'react-router-dom'
import { useAuth } from '../auth/AuthContext'

export default function OpsRequireAuth({ children }) {
  const { user, loading } = useAuth()

  if (loading) return (
    <div style={{ minHeight: '100vh', background: '#0f1117', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
      <div style={{
        width: 32, height: 32,
        border: '2px solid #252a35',
        borderTopColor: '#f59e0b',
        borderRadius: '50%',
        animation: 'spin 0.8s linear infinite',
      }} />
      <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
    </div>
  )

  if (!user) return <Navigate to="/ops/login" replace />

  const isOps = ['ADMIN', 'OPS_STAFF'].includes(user.role)
  if (!isOps) return <Navigate to="/" replace />

  return children
}