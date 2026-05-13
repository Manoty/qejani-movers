// frontend/src/features/ops/pages/OpsSchedule.jsx

import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import { fetchWeeklySchedule } from '../api/opsApi'
import { OpsStatusBadge } from '../components/OpsStatusBadge'

function getStartOfWeek(d = new Date()) {
  const day = d.getDay()
  const diff = d.getDate() - day + (day === 0 ? -6 : 1)
  const mon = new Date(d)
  mon.setDate(diff)
  return mon.toISOString().split('T')[0]
}

export default function OpsSchedule() {
  const navigate = useNavigate()
  const [weekStart, setWeekStart] = useState(getStartOfWeek())

  const { data: weekly = [], isLoading } = useQuery({
    queryKey: ['ops-schedule-weekly', weekStart],
    queryFn: () => fetchWeeklySchedule(weekStart),
  })

  const shiftWeek = (n) => {
    const d = new Date(weekStart)
    d.setDate(d.getDate() + n * 7)
    setWeekStart(d.toISOString().split('T')[0])
  }

  const totalThisWeek = weekly.reduce((s, d) => s + d.total_bookings, 0)

  return (
    <div className="ops-animate">
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 28 }}>
        <div>
          <h1 style={{ fontSize: 24, fontWeight: 800, color: 'var(--ops-text)' }}>Schedule</h1>
          <p style={{ fontSize: 13, color: 'var(--ops-muted)', marginTop: 2 }}>
            {totalThisWeek} booking{totalThisWeek !== 1 ? 's' : ''} this week
          </p>
        </div>
        <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
          <button onClick={() => shiftWeek(-1)} style={navBtnStyle}>← Prev</button>
          <button onClick={() => setWeekStart(getStartOfWeek())} style={{ ...navBtnStyle, color: 'var(--ops-amber)', borderColor: 'var(--ops-amber)' }}>Today</button>
          <button onClick={() => shiftWeek(1)} style={navBtnStyle}>Next →</button>
        </div>
      </div>

      {isLoading ? (
        <div style={{ textAlign: 'center', padding: '60px', color: 'var(--ops-muted)' }}>Loading schedule…</div>
      ) : (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(7, 1fr)', gap: 10 }}>
          {weekly.map((day) => {
            const d = new Date(day.date + 'T00:00:00')
            const isToday = day.date === new Date().toISOString().split('T')[0]

            return (
              <div
                key={day.date}
                style={{
                  background: 'var(--ops-surface)',
                  border: `1px solid ${isToday ? 'var(--ops-amber)' : 'var(--ops-border)'}`,
                  borderRadius: 10,
                  overflow: 'hidden',
                  minHeight: 180,
                }}
              >
                {/* Day header */}
                <div style={{
                  padding: '10px 12px',
                  background: isToday ? 'var(--ops-amber-dim)' : 'transparent',
                  borderBottom: '1px solid var(--ops-border)',
                }}>
                  <div style={{ fontSize: 10, fontWeight: 700, color: isToday ? 'var(--ops-amber)' : 'var(--ops-muted)', letterSpacing: 1, textTransform: 'uppercase' }}>
                    {d.toLocaleDateString('en-KE', { weekday: 'short' })}
                  </div>
                  <div className="ops-mono" style={{ fontSize: 20, fontWeight: 600, color: isToday ? 'var(--ops-amber)' : 'var(--ops-text)', lineHeight: 1.2 }}>
                    {d.getDate()}
                  </div>
                  {day.total_bookings > 0 && (
                    <div style={{ fontSize: 10, color: 'var(--ops-muted)', marginTop: 2 }}>
                      {day.total_bookings} job{day.total_bookings > 1 ? 's' : ''}
                    </div>
                  )}
                </div>

                {/* Bookings */}
                <div style={{ padding: '8px' }}>
                  {day.bookings.map(b => (
                    <div
                      key={b.id}
                      onClick={() => navigate(`/ops/bookings/${b.id}`)}
                      style={{
                        padding: '8px',
                        borderRadius: 6,
                        background: 'var(--ops-bg)',
                        marginBottom: 6,
                        cursor: 'pointer',
                        border: '1px solid var(--ops-border)',
                        transition: 'border-color 0.15s',
                      }}
                      onMouseEnter={e => e.currentTarget.style.borderColor = 'var(--ops-amber)'}
                      onMouseLeave={e => e.currentTarget.style.borderColor = 'var(--ops-border)'}
                    >
                      <div style={{ fontSize: 11, fontWeight: 600, color: 'var(--ops-text)', marginBottom: 4, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                        {b.customer_name}
                      </div>
                      <div className="ops-mono" style={{ fontSize: 10, color: 'var(--ops-muted)', marginBottom: 5 }}>
                        {b.house_size.replace('_', ' ')}
                        {b.scheduled_time && ` · ${b.scheduled_time.slice(0, 5)}`}
                      </div>
                      <OpsStatusBadge status={b.status} />
                    </div>
                  ))}
                </div>
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}

const navBtnStyle = {
  padding: '7px 14px', background: 'var(--ops-surface)',
  border: '1px solid var(--ops-border)', borderRadius: 7,
  color: 'var(--ops-muted)', fontSize: 12, cursor: 'pointer',
  fontFamily: 'JetBrains Mono, monospace', transition: 'all 0.15s',
}