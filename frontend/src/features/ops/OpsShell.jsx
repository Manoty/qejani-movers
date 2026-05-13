// frontend/src/features/ops/OpsShell.jsx

import { NavLink, Outlet, useNavigate } from 'react-router-dom'
import { useAuth } from '../auth/AuthContext'
import './ops.css'

const NAV = [
  { to: '/ops',           label: 'Dashboard',  exact: true, icon: GridIcon   },
  { to: '/ops/bookings',  label: 'Bookings',   exact: false, icon: BoxIcon   },
  { to: '/ops/schedule',  label: 'Schedule',   exact: false, icon: CalIcon   },
  { to: '/ops/analytics', label: 'Analytics',  exact: false, icon: ChartIcon },
]

export default function OpsShell() {
  const { user, logout } = useAuth()

  return (
    <div className="ops-shell" style={{ display: 'flex', minHeight: '100vh' }}>

      {/* Sidebar */}
      <aside style={{
        width: 220, flexShrink: 0,
        background: 'var(--ops-surface)',
        borderRight: '1px solid var(--ops-border)',
        display: 'flex', flexDirection: 'column',
        position: 'sticky', top: 0, height: '100vh',
        overflow: 'hidden',
      }}>
        {/* Logo */}
        <div style={{
          padding: '20px 20px 16px',
          borderBottom: '1px solid var(--ops-border)',
          display: 'flex', alignItems: 'center', gap: 10,
        }}>
          <div style={{
            width: 32, height: 32, background: 'var(--ops-amber)', borderRadius: 7,
            display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0,
          }}>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#0f1117" strokeWidth="2.5">
              <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>
            </svg>
          </div>
          <div>
            <div style={{ fontSize: 14, fontWeight: 700, color: 'var(--ops-text)', lineHeight: 1.2 }}>Qejani</div>
            <div style={{ fontSize: 11, color: 'var(--ops-amber)', fontWeight: 600, letterSpacing: 1 }}>OPS CENTER</div>
          </div>
        </div>

        {/* Nav */}
        <nav style={{ padding: '12px 10px', flex: 1 }}>
          {NAV.map(({ to, label, exact, icon: Icon }) => (
            <NavLink
              key={to}
              to={to}
              end={exact}
              style={({ isActive }) => ({
                display: 'flex', alignItems: 'center', gap: 10,
                padding: '9px 12px', borderRadius: 7, marginBottom: 2,
                textDecoration: 'none', fontSize: 14, fontWeight: 600,
                color: isActive ? '#0f1117' : 'var(--ops-muted)',
                background: isActive ? 'var(--ops-amber)' : 'transparent',
                transition: 'all 0.18s',
              })}
            >
              {({ isActive }) => (
                <>
                  <Icon size={16} color={isActive ? '#0f1117' : 'currentColor'} />
                  {label}
                </>
              )}
            </NavLink>
          ))}
        </nav>

        {/* User */}
        <div style={{
          padding: '16px 14px',
          borderTop: '1px solid var(--ops-border)',
        }}>
          <div style={{ fontSize: 13, fontWeight: 600, color: 'var(--ops-text)', marginBottom: 2 }}>
            {user?.first_name} {user?.last_name}
          </div>
          <div style={{ fontSize: 11, color: 'var(--ops-amber)', marginBottom: 10 }}>
            {user?.role}
          </div>
          <button onClick={logout} style={{
            fontSize: 12, color: 'var(--ops-muted)', background: 'none',
            border: 'none', cursor: 'pointer', padding: 0,
          }}>
            Sign out
          </button>
        </div>
      </aside>

      {/* Main content */}
      <main style={{ flex: 1, overflow: 'auto', padding: '32px' }}>
        <Outlet />
      </main>

      <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
    </div>
  )
}

// ── Inline icon components (no external dep) ──────────────────────────────────
function GridIcon({ size = 16, color = 'currentColor' }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="2">
      <rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/>
      <rect x="14" y="14" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/>
    </svg>
  )
}
function BoxIcon({ size = 16, color = 'currentColor' }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="2">
      <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/>
    </svg>
  )
}
function CalIcon({ size = 16, color = 'currentColor' }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="2">
      <rect x="3" y="4" width="18" height="18" rx="2"/><line x1="16" y1="2" x2="16" y2="6"/>
      <line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/>
    </svg>
  )
}
function ChartIcon({ size = 16, color = 'currentColor' }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="2">
      <line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/>
      <line x1="6" y1="20" x2="6" y2="14"/>
    </svg>
  )
}