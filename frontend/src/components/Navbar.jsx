// frontend/src/components/Navbar.jsx

import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../features/auth/AuthContext'
import Button from './ui/Button'

export default function Navbar() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  return (
    <nav style={{
      position: 'fixed', top: 0, left: 0, right: 0, zIndex: 100,
      background: 'rgba(247,243,237,0.92)',
      backdropFilter: 'blur(12px)',
      borderBottom: '1px solid var(--cream-dark)',
      padding: '0 2rem',
      height: 64,
      display: 'flex', alignItems: 'center', justifyContent: 'space-between',
    }}>
      <Link to="/" style={{ textDecoration: 'none', display: 'flex', alignItems: 'center', gap: 10 }}>
        <span style={{
          width: 32, height: 32,
          background: 'var(--forest)',
          borderRadius: 8,
          display: 'flex', alignItems: 'center', justifyContent: 'center',
        }}>
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2.2">
            <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>
            <polyline points="9 22 9 12 15 12 15 22"/>
          </svg>
        </span>
        <span className="serif" style={{ fontSize: 20, color: 'var(--forest)', letterSpacing: '-0.3px' }}>
          Qejani
        </span>
      </Link>

      <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
        {user ? (
          <>
            <Link to="/dashboard" style={{ textDecoration: 'none', fontSize: 14, color: 'var(--forest)', fontWeight: 500 }}>
              My Bookings
            </Link>
            <button
              onClick={logout}
              style={{ background: 'none', border: 'none', cursor: 'pointer', fontSize: 14, color: 'var(--muted)' }}
            >
              Sign out
            </button>
          </>
        ) : (
          <>
            <Link to="/login" style={{ textDecoration: 'none', fontSize: 14, color: 'var(--forest)', fontWeight: 500 }}>
              Sign in
            </Link>
            <Button size="sm" onClick={() => navigate('/quote')}>
              Get a Quote
            </Button>
          </>
        )}
      </div>
    </nav>
  )
}