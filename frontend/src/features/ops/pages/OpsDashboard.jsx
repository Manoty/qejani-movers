// frontend/src/features/ops/pages/OpsDashboard.jsx

import { useQuery } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import { fetchAnalyticsOverview, fetchOpsBookings } from '../api/opsApi'
import { OpsStatusBadge } from '../components/OpsStatusBadge'

export default function OpsDashboard() {
  const navigate = useNavigate()

  const since = new Date(Date.now() - 30 * 86400000).toISOString().split('T')[0]
  const until = new Date().toISOString().split('T')[0]

  const { data: overview } = useQuery({
    queryKey: ['ops-overview', since, until],
    queryFn: () => fetchAnalyticsOverview({ since, until }),
  })

  const { data: pending = [] } = useQuery({
    queryKey: ['ops-bookings', 'PENDING'],
    queryFn: () => fetchOpsBookings({ status: 'PENDING' }),
  })

  const stats = [
    { label: 'Total bookings', value: overview?.bookings?.total ?? '—', unit: 'last 30 days' },
    { label: 'Completed',      value: overview?.bookings?.completed ?? '—', unit: 'moves done' },
    { label: 'Revenue',        value: overview ? `KES ${Number(overview.revenue.total).toLocaleString()}` : '—', unit: 'collected', amber: true },
    { label: 'Active',         value: overview?.bookings?.active ?? '—', unit: 'in progress' },
  ]

  return (
    <div className="ops-animate">
      <div style={{ marginBottom: 32 }}>
        <h1 style={{ fontSize: 26, fontWeight: 800, color: 'var(--ops-text)', marginBottom: 4 }}>
          Operations Dashboard
        </h1>
        <p style={{ fontSize: 13, color: 'var(--ops-muted)' }}>
          {new Date().toLocaleDateString('en-KE', { weekday: 'long', dateStyle: 'long' })}
        </p>
      </div>

      {/* Stats row */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 14, marginBottom: 36 }}>
        {stats.map((s, i) => (
          <div key={i} className={`ops-delay-${i + 1}`} style={{
            background: 'var(--ops-surface)',
            border: `1px solid ${s.amber ? 'rgba(245,158,11,0.3)' : 'var(--ops-border)'}`,
            borderRadius: 10, padding: '20px',
          }}>
            <p style={{ fontSize: 11, color: 'var(--ops-muted)', fontWeight: 600, letterSpacing: 1, textTransform: 'uppercase', marginBottom: 10 }}>
              {s.label}
            </p>
            <p className="ops-mono" style={{ fontSize: 28, fontWeight: 600, color: s.amber ? 'var(--ops-amber)' : 'var(--ops-text)', lineHeight: 1 }}>
              {s.value}
            </p>
            <p style={{ fontSize: 11, color: 'var(--ops-muted)', marginTop: 6 }}>{s.unit}</p>
          </div>
        ))}
      </div>

      {/* Pending bookings */}
      <div style={{ background: 'var(--ops-surface)', border: '1px solid var(--ops-border)', borderRadius: 10 }}>
        <div style={{
          padding: '16px 20px',
          borderBottom: '1px solid var(--ops-border)',
          display: 'flex', alignItems: 'center', justifyContent: 'space-between',
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
            <h2 style={{ fontSize: 14, fontWeight: 700, color: 'var(--ops-text)' }}>Pending Review</h2>
            {pending.length > 0 && (
              <span style={{
                background: 'var(--ops-amber)', color: '#0f1117',
                borderRadius: 100, padding: '2px 8px', fontSize: 11, fontWeight: 700,
              }}>{pending.length}</span>
            )}
          </div>
          <button onClick={() => navigate('/ops/bookings')} style={{
            background: 'none', border: 'none', color: 'var(--ops-amber)',
            fontSize: 12, cursor: 'pointer', fontWeight: 600,
          }}>
            View all →
          </button>
        </div>

        {pending.length === 0 ? (
          <div style={{ padding: '40px', textAlign: 'center', color: 'var(--ops-muted)', fontSize: 13 }}>
            No pending bookings right now.
          </div>
        ) : (
          <div>
            {pending.slice(0, 6).map((b, i) => (
              <div
                key={b.id}
                onClick={() => navigate(`/ops/bookings/${b.id}`)}
                style={{
                  display: 'grid',
                  gridTemplateColumns: '1fr 140px 120px 100px',
                  gap: 16, alignItems: 'center',
                  padding: '13px 20px',
                  borderBottom: i < Math.min(pending.length, 6) - 1 ? '1px solid var(--ops-border)' : 'none',
                  cursor: 'pointer',
                  transition: 'background 0.15s',
                }}
                onMouseEnter={e => e.currentTarget.style.background = 'rgba(255,255,255,0.02)'}
                onMouseLeave={e => e.currentTarget.style.background = 'transparent'}
              >
                <div>
                  <div style={{ fontSize: 13, fontWeight: 600, color: 'var(--ops-text)', marginBottom: 2 }}>
                    {b.customer_name}
                  </div>
                  <div className="ops-mono" style={{ fontSize: 11, color: 'var(--ops-muted)' }}>
                    {b.house_size.replace('_', ' ')} · {b.pickup_address.split(',')[0]}
                  </div>
                </div>
                <div className="ops-mono" style={{ fontSize: 12, color: 'var(--ops-muted)' }}>
                  {b.scheduled_date || 'No date set'}
                </div>
                <div className="ops-mono" style={{ fontSize: 13, color: 'var(--ops-amber)', fontWeight: 600 }}>
                  KES {Number(b.quoted_total).toLocaleString()}
                </div>
                <OpsStatusBadge status={b.status} />
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}