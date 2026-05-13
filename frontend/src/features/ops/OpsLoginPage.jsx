// frontend/src/features/ops/OpsLoginPage.jsx

import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import api from '../../lib/axios'
import { useAuth } from '../auth/AuthContext'
import './ops.css'

export default function OpsLoginPage() {
  const navigate  = useNavigate()
  const { loadProfile } = useAuth()
  const [form, setForm] = useState({ email: '', password: '' })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      const { data } = await api.post('/auth/staff/login/', form)
      localStorage.setItem('access_token', data.tokens.access)
      localStorage.setItem('refresh_token', data.tokens.refresh)
      // Reload profile into AuthContext
      window.location.href = '/ops'
    } catch (err) {
      setError(err.response?.data?.detail || 'Invalid credentials.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="ops-shell" style={{
      minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '1rem',
    }}>
      <div className="ops-animate" style={{ width: '100%', maxWidth: 400 }}>

        {/* Logo */}
        <div style={{ marginBottom: 40 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 32 }}>
            <div style={{
              width: 36, height: 36, background: 'var(--ops-amber)',
              borderRadius: 8, display: 'flex', alignItems: 'center', justifyContent: 'center',
            }}>
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#0f1117" strokeWidth="2.5">
                <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>
              </svg>
            </div>
            <span style={{ fontFamily: 'Syne, sans-serif', fontSize: 18, fontWeight: 700, color: 'var(--ops-text)' }}>
              Qejani <span style={{ color: 'var(--ops-amber)' }}>Ops</span>
            </span>
          </div>
          <h1 style={{ fontSize: 28, fontWeight: 800, color: 'var(--ops-text)', marginBottom: 6 }}>
            Staff access
          </h1>
          <p style={{ fontSize: 14, color: 'var(--ops-muted)' }}>
            Sign in with your team credentials.
          </p>
        </div>

        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
          {['email', 'password'].map(field => (
            <div key={field}>
              <label style={{ fontSize: 12, fontWeight: 600, color: 'var(--ops-muted)', display: 'block', marginBottom: 8, textTransform: 'uppercase', letterSpacing: 1 }}>
                {field}
              </label>
              <input
                type={field}
                value={form[field]}
                onChange={e => setForm(f => ({ ...f, [field]: e.target.value }))}
                required
                placeholder={field === 'email' ? 'ops@qejani.co.ke' : '••••••••'}
                style={{
                  width: '100%', padding: '12px 16px',
                  background: 'var(--ops-surface)',
                  border: '1px solid var(--ops-border)',
                  borderRadius: 8, color: 'var(--ops-text)',
                  fontSize: 14, outline: 'none',
                  fontFamily: 'JetBrains Mono, monospace',
                  transition: 'border-color 0.2s',
                }}
                onFocus={e => e.target.style.borderColor = 'var(--ops-amber)'}
                onBlur={e => e.target.style.borderColor = 'var(--ops-border)'}
              />
            </div>
          ))}

          {error && (
            <div style={{
              background: 'var(--ops-red-dim)', border: '1px solid var(--ops-red)',
              borderRadius: 8, padding: '10px 14px',
              color: 'var(--ops-red)', fontSize: 13,
            }}>
              {error}
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            style={{
              width: '100%', padding: '13px',
              background: loading ? 'rgba(245,158,11,0.5)' : 'var(--ops-amber)',
              color: '#0f1117', border: 'none', borderRadius: 8,
              fontSize: 14, fontWeight: 700, cursor: loading ? 'not-allowed' : 'pointer',
              fontFamily: 'Syne, sans-serif', letterSpacing: 0.5,
              transition: 'background 0.2s',
            }}
          >
            {loading ? 'Signing in…' : 'Sign in →'}
          </button>
        </form>
      </div>
      <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
    </div>
  )
}