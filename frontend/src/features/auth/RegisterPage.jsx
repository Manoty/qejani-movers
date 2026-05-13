// frontend/src/features/auth/RegisterPage.jsx

import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from './AuthContext'
import Button from '../../components/ui/Button'
import Input from '../../components/ui/Input'

export default function RegisterPage() {
  const { register } = useAuth()
  const navigate = useNavigate()
  const [form, setForm]   = useState({ phone: '', password: '', first_name: '', last_name: '' })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const set = (k, v) => setForm(f => ({ ...f, [k]: v }))

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      await register(form)
      navigate('/dashboard')
    } catch (err) {
      const data = err.response?.data
      setError(
        typeof data === 'object'
          ? Object.values(data).flat().join(' ')
          : 'Registration failed. Please try again.'
      )
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{
      minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center',
      background: 'var(--cream)', padding: '1rem',
    }}>
      <div className="animate-fade-up" style={{ width: '100%', maxWidth: 420 }}>
        <div style={{ textAlign: 'center', marginBottom: 36 }}>
          <Link to="/" style={{ textDecoration: 'none' }}>
            <div style={{
              width: 48, height: 48, background: 'var(--forest)', borderRadius: 14,
              display: 'inline-flex', alignItems: 'center', justifyContent: 'center', marginBottom: 16,
            }}>
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2">
                <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>
                <polyline points="9 22 9 12 15 12 15 22"/>
              </svg>
            </div>
          </Link>
          <h1 className="serif" style={{ fontSize: 28, color: 'var(--forest)' }}>Create account</h1>
          <p style={{ fontSize: 14, color: 'var(--muted)', marginTop: 6 }}>Join Qejani Movers</p>
        </div>

        <div style={{
          background: 'var(--white)', borderRadius: 16,
          padding: '32px', border: '1px solid var(--cream-dark)',
          boxShadow: 'var(--shadow-sm)',
        }}>
          <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
              <Input label="First name" placeholder="Jane" value={form.first_name} onChange={e => set('first_name', e.target.value)} required />
              <Input label="Last name" placeholder="Wanjiru" value={form.last_name} onChange={e => set('last_name', e.target.value)} required />
            </div>
            <Input label="Phone number" type="tel" placeholder="+254712345678" value={form.phone} onChange={e => set('phone', e.target.value)} required />
            <Input label="Password" type="password" placeholder="Minimum 8 characters" value={form.password} onChange={e => set('password', e.target.value)} required minLength={8} />

            {error && (
              <div style={{ background: '#fff5f5', border: '1px solid #fed7d7', borderRadius: 8, padding: '10px 14px', color: '#c53030', fontSize: 13 }}>
                {error}
              </div>
            )}

            <Button type="submit" size="lg" loading={loading} style={{ justifyContent: 'center', marginTop: 4 }}>
              Create account
            </Button>
          </form>
        </div>

        <p style={{ textAlign: 'center', marginTop: 20, fontSize: 14, color: 'var(--muted)' }}>
          Already have an account?{' '}
          <Link to="/login" style={{ color: 'var(--forest)', fontWeight: 600, textDecoration: 'none' }}>Sign in</Link>
        </p>
      </div>
    </div>
  )
}