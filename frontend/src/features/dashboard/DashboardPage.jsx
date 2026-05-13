// frontend/src/features/dashboard/DashboardPage.jsx

import { useQuery } from '@tanstack/react-query'
import { useNavigate, useSearchParams } from 'react-router-dom'
import api from '../../lib/axios'
import { useAuth } from '../auth/AuthContext'
import Button from '../../components/ui/Button'

const STATUS_META = {
  PENDING:    { label: 'Pending review',   color: '#d4821a', bg: 'rgba(212,130,26,0.1)' },
  CONFIRMED:  { label: 'Confirmed',        color: '#2d5a40', bg: 'rgba(45,90,64,0.1)'   },
  ASSIGNED:   { label: 'Crew assigned',    color: '#2d5a40', bg: 'rgba(45,90,64,0.1)'   },
  ON_THE_WAY: { label: 'On the way',       color: '#1a3a2a', bg: 'rgba(26,58,42,0.12)'  },
  MOVING:     { label: 'Moving now',       color: '#1a3a2a', bg: 'rgba(26,58,42,0.12)'  },
  COMPLETED:  { label: 'Completed',        color: '#276749', bg: 'rgba(39,103,73,0.1)'  },
  CANCELLED:  { label: 'Cancelled',        color: '#9b2c2c', bg: 'rgba(155,44,44,0.08)' },
}

function StatusBadge({ status }) {
  const meta = STATUS_META[status] || { label: status, color: 'var(--muted)', bg: 'var(--cream-dark)' }
  return (
    <span style={{
      display: 'inline-flex', alignItems: 'center', gap: 5,
      background: meta.bg, color: meta.color,
      padding: '4px 10px', borderRadius: 100,
      fontSize: 12, fontWeight: 600,
    }}>
      <span style={{ width: 6, height: 6, borderRadius: '50%', background: meta.color }} />
      {meta.label}
    </span>
  )
}

function BookingCard({ booking, isNew }) {
  const navigate = useNavigate()

  return (
    <div style={{
      background: 'var(--white)',
      borderRadius: 12,
      border: `1.5px solid ${isNew ? 'var(--amber)' : 'var(--cream-dark)'}`,
      padding: '20px',
      boxShadow: isNew ? '0 0 0 3px rgba(212,130,26,0.15)' : 'var(--shadow-sm)',
      transition: 'box-shadow var(--transition)',
      cursor: 'pointer',
    }}
    onClick={() => navigate(`/bookings/${booking.id}`)}
    onMouseEnter={e => e.currentTarget.style.boxShadow = 'var(--shadow-md)'}
    onMouseLeave={e => e.currentTarget.style.boxShadow = isNew ? '0 0 0 3px rgba(212,130,26,0.15)' : 'var(--shadow-sm)'}
    >
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 14 }}>
        <div>
          {isNew && (
            <span style={{ fontSize: 11, fontWeight: 600, color: 'var(--amber)', display: 'block', marginBottom: 4 }}>
              ✓ Booking confirmed!
            </span>
          )}
          <h3 style={{ fontSize: 16, fontWeight: 600, color: 'var(--forest)' }}>
            {booking.house_size.replace('_', ' ')} Move
          </h3>
          <p style={{ fontSize: 12, color: 'var(--muted)', marginTop: 2 }}>
            {new Date(booking.created_at).toLocaleDateString('en-KE', { dateStyle: 'medium' })}
          </p>
        </div>
        <StatusBadge status={booking.status} />
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: 6, marginBottom: 16 }}>
        <div style={{ display: 'flex', gap: 8, fontSize: 13 }}>
          <span style={{ color: 'var(--muted)', minWidth: 24 }}>📍</span>
          <span style={{ color: 'var(--charcoal)' }} className="truncate">{booking.pickup_address}</span>
        </div>
        <div style={{ display: 'flex', gap: 8, fontSize: 13 }}>
          <span style={{ color: 'var(--muted)', minWidth: 24 }}>🏁</span>
          <span style={{ color: 'var(--charcoal)' }} className="truncate">{booking.destination_address}</span>
        </div>
        {booking.scheduled_date && (
          <div style={{ display: 'flex', gap: 8, fontSize: 13 }}>
            <span style={{ color: 'var(--muted)', minWidth: 24 }}>📅</span>
            <span style={{ color: 'var(--charcoal)' }}>
              {new Date(booking.scheduled_date).toLocaleDateString('en-KE', { dateStyle: 'long' })}
            </span>
          </div>
        )}
      </div>

      <div style={{
        display: 'flex', justifyContent: 'space-between', alignItems: 'center',
        paddingTop: 14, borderTop: '1px solid var(--cream-dark)',
      }}>
        <div>
          <p style={{ fontSize: 11, color: 'var(--muted)' }}>Quoted total</p>
          <p className="serif" style={{ fontSize: 22, color: 'var(--forest)', marginTop: 1 }}>
            KES {Number(booking.quoted_total).toLocaleString()}
          </p>
        </div>
        <span style={{ fontSize: 13, color: 'var(--muted)' }}>View details →</span>
      </div>
    </div>
  )
}

export default function DashboardPage() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const newBookingId = searchParams.get('new')

  const { data: bookings = [], isLoading } = useQuery({
    queryKey: ['my-bookings'],
    queryFn: () => api.get('/bookings/mine/').then(r => r.data),
  })

  const active = bookings.filter(b => !['COMPLETED', 'CANCELLED'].includes(b.status))
  const past   = bookings.filter(b =>  ['COMPLETED', 'CANCELLED'].includes(b.status))

  return (
    <div style={{ minHeight: '100vh', paddingTop: 64, background: 'var(--cream)' }}>
      <div style={{ maxWidth: 680, margin: '0 auto', padding: '48px 1rem 60px' }}>

        {/* Header */}
        <div className="animate-fade-up" style={{ marginBottom: 40 }}>
          <p style={{ fontSize: 13, color: 'var(--muted)' }}>Welcome back,</p>
          <h1 className="serif" style={{ fontSize: 34, color: 'var(--forest)', letterSpacing: '-0.5px' }}>
            {user?.first_name} {user?.last_name}
          </h1>
          <p style={{ fontSize: 13, color: 'var(--muted)', marginTop: 4 }}>{user?.phone}</p>
        </div>

        {/* Quick action */}
        <div className="animate-fade-up delay-100" style={{
          background: 'var(--forest)',
          borderRadius: 14, padding: '24px',
          display: 'flex', justifyContent: 'space-between', alignItems: 'center',
          marginBottom: 36,
        }}>
          <div>
            <h3 style={{ color: 'var(--cream)', fontSize: 16, fontWeight: 600 }}>Planning another move?</h3>
            <p style={{ color: 'rgba(247,243,237,0.6)', fontSize: 13, marginTop: 4 }}>Get a new quote in 60 seconds.</p>
          </div>
          <Button variant="amber" size="sm" onClick={() => navigate('/quote')}>
            New quote →
          </Button>
        </div>

        {isLoading && (
          <div style={{ textAlign: 'center', padding: '60px 0', color: 'var(--muted)' }}>
            Loading your bookings…
          </div>
        )}

        {!isLoading && bookings.length === 0 && (
          <div className="animate-fade-up" style={{
            textAlign: 'center', padding: '60px 20px',
            background: 'var(--white)', borderRadius: 14,
            border: '1px solid var(--cream-dark)',
          }}>
            <div style={{ fontSize: 48, marginBottom: 16 }}>📦</div>
            <h3 style={{ fontSize: 20, fontWeight: 600, color: 'var(--forest)', marginBottom: 8 }}>
              No bookings yet
            </h3>
            <p style={{ color: 'var(--muted)', marginBottom: 24, fontSize: 14 }}>
              Ready to move? Get an instant quote and book your crew.
            </p>
            <Button onClick={() => navigate('/quote')}>Get a quote →</Button>
          </div>
        )}

        {active.length > 0 && (
          <section className="animate-fade-up delay-200" style={{ marginBottom: 36 }}>
            <h2 style={{ fontSize: 14, fontWeight: 600, color: 'var(--muted)', letterSpacing: 1, textTransform: 'uppercase', marginBottom: 16 }}>
              Active bookings
            </h2>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
              {active.map(b => (
                <BookingCard key={b.id} booking={b} isNew={b.id === newBookingId} />
              ))}
            </div>
          </section>
        )}

        {past.length > 0 && (
          <section className="animate-fade-up delay-300">
            <h2 style={{ fontSize: 14, fontWeight: 600, color: 'var(--muted)', letterSpacing: 1, textTransform: 'uppercase', marginBottom: 16 }}>
              Past bookings
            </h2>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
              {past.map(b => <BookingCard key={b.id} booking={b} isNew={false} />)}
            </div>
          </section>
        )}
      </div>
    </div>
  )
}