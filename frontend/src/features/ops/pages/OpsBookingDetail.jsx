// frontend/src/features/ops/pages/OpsBookingDetail.jsx

import { useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
  fetchBookingDetail, fetchBookingCrew,
  fetchMovers, assignCrew, unassignMover,
} from '../api/opsApi'
import { OpsStatusBadge } from '../components/OpsStatusBadge'

export default function OpsBookingDetail() {
  const { id } = useParams()
  const navigate = useNavigate()
  const qc = useQueryClient()
  const [selectedMovers, setSelectedMovers] = useState([])

  const { data: booking, isLoading } = useQuery({
    queryKey: ['booking-detail', id],
    queryFn: () => fetchBookingDetail(id),
  })

  const { data: crew = [] } = useQuery({
    queryKey: ['booking-crew', id],
    queryFn: () => fetchBookingCrew(id),
  })

  const { data: movers = [] } = useQuery({
    queryKey: ['ops-movers'],
    queryFn: fetchMovers,
  })

  const assignMutation = useMutation({
    mutationFn: () => assignCrew(id, { mover_ids: selectedMovers }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['booking-crew', id] })
      qc.invalidateQueries({ queryKey: ['booking-detail', id] })
      setSelectedMovers([])
    },
  })

  const unassignMutation = useMutation({
    mutationFn: (moverId) => unassignMover(id, { mover_id: moverId }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['booking-crew', id] })
    },
  })

  const toggleMover = (moverId) => {
    setSelectedMovers(s =>
      s.includes(moverId) ? s.filter(m => m !== moverId) : [...s, moverId]
    )
  }

  if (isLoading) return (
    <div style={{ padding: '60px', textAlign: 'center', color: 'var(--ops-muted)' }}>Loading…</div>
  )

  if (!booking) return null

  const assignedIds = new Set(crew.map(c => c.mover))

  return (
    <div className="ops-animate">
      <button
        onClick={() => navigate('/ops/bookings')}
        style={{ background: 'none', border: 'none', color: 'var(--ops-muted)', cursor: 'pointer', fontSize: 13, marginBottom: 20, display: 'flex', alignItems: 'center', gap: 6 }}
      >
        ← Back to bookings
      </button>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 340px', gap: 20, alignItems: 'start' }}>

        {/* Left — Booking Info */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>

          {/* Header card */}
          <div style={{ background: 'var(--ops-surface)', border: '1px solid var(--ops-border)', borderRadius: 10, padding: '24px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 20 }}>
              <div>
                <h1 style={{ fontSize: 20, fontWeight: 800, color: 'var(--ops-text)', marginBottom: 4 }}>
                  {booking.customer_name}
                </h1>
                <div className="ops-mono" style={{ fontSize: 12, color: 'var(--ops-muted)' }}>
                  {booking.customer_phone} · {booking.house_size.replace('_', ' ')}
                </div>
              </div>
              <OpsStatusBadge status={booking.status} />
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 14 }}>
              {[
                ['Pickup', booking.pickup_address],
                ['Destination', booking.destination_address],
                ['Floor', `${booking.pickup_floor}${booking.pickup_has_lift ? ' (lift)' : ' (stairs)'}`],
                ['Distance', `${booking.distance_km} km`],
                ['Scheduled', booking.scheduled_date || '—'],
                ['Time', booking.scheduled_time || '—'],
              ].map(([label, val]) => (
                <div key={label}>
                  <div style={{ fontSize: 10, color: 'var(--ops-muted)', fontWeight: 600, letterSpacing: 1, textTransform: 'uppercase', marginBottom: 4 }}>
                    {label}
                  </div>
                  <div className="ops-mono" style={{ fontSize: 13, color: 'var(--ops-text)' }}>{val}</div>
                </div>
              ))}
            </div>

            {booking.inventory_notes && (
              <div style={{ marginTop: 16, padding: '12px', background: 'var(--ops-bg)', borderRadius: 7 }}>
                <div style={{ fontSize: 10, color: 'var(--ops-muted)', fontWeight: 600, letterSpacing: 1, textTransform: 'uppercase', marginBottom: 6 }}>
                  Inventory notes
                </div>
                <div className="ops-mono" style={{ fontSize: 12, color: 'var(--ops-text)', lineHeight: 1.6 }}>
                  {booking.inventory_notes}
                </div>
              </div>
            )}
          </div>

          {/* Quote breakdown */}
          <div style={{ background: 'var(--ops-surface)', border: '1px solid var(--ops-border)', borderRadius: 10, padding: '20px' }}>
            <h3 style={{ fontSize: 13, fontWeight: 700, color: 'var(--ops-text)', marginBottom: 14 }}>
              Quote Breakdown
            </h3>
            {booking.quote_snapshot?.line_items?.map((item, i) => (
              <div key={i} style={{
                display: 'flex', justifyContent: 'space-between',
                padding: '8px 0',
                borderBottom: i < booking.quote_snapshot.line_items.length - 1 ? '1px solid var(--ops-border)' : 'none',
              }}>
                <span className="ops-mono" style={{ fontSize: 12, color: 'var(--ops-muted)' }}>{item.label}</span>
                <span className="ops-mono" style={{ fontSize: 12, color: 'var(--ops-text)', fontWeight: 600 }}>
                  KES {Number(item.amount).toLocaleString()}
                </span>
              </div>
            ))}
            <div style={{
              display: 'flex', justifyContent: 'space-between', marginTop: 12,
              paddingTop: 12, borderTop: '1px solid var(--ops-border-hi)',
            }}>
              <span style={{ fontSize: 13, fontWeight: 700, color: 'var(--ops-text)' }}>Total</span>
              <span className="ops-mono" style={{ fontSize: 16, fontWeight: 700, color: 'var(--ops-amber)' }}>
                KES {Number(booking.quoted_total).toLocaleString()}
              </span>
            </div>
          </div>

          {/* Cancellation reason */}
          {booking.cancellation_reason && (
            <div style={{
              background: 'var(--ops-red-dim)', border: '1px solid var(--ops-red)',
              borderRadius: 10, padding: '16px 20px',
            }}>
              <div style={{ fontSize: 11, color: 'var(--ops-red)', fontWeight: 700, letterSpacing: 1, textTransform: 'uppercase', marginBottom: 6 }}>
                Cancellation Reason
              </div>
              <div className="ops-mono" style={{ fontSize: 13, color: 'var(--ops-text)' }}>
                {booking.cancellation_reason}
              </div>
            </div>
          )}
        </div>

        {/* Right — Crew */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>

          {/* Current crew */}
          <div style={{ background: 'var(--ops-surface)', border: '1px solid var(--ops-border)', borderRadius: 10, padding: '20px' }}>
            <h3 style={{ fontSize: 13, fontWeight: 700, color: 'var(--ops-text)', marginBottom: 14 }}>
              Assigned Crew ({crew.length})
            </h3>

            {crew.length === 0 ? (
              <p style={{ fontSize: 12, color: 'var(--ops-muted)' }}>No crew assigned yet.</p>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
                {crew.map(c => (
                  <div key={c.id} style={{
                    display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                    padding: '10px 12px', background: 'var(--ops-bg)',
                    borderRadius: 7, border: '1px solid var(--ops-border)',
                  }}>
                    <div>
                      <div style={{ fontSize: 13, fontWeight: 600, color: 'var(--ops-text)' }}>{c.mover_name}</div>
                      <div className="ops-mono" style={{ fontSize: 10, color: 'var(--ops-amber)' }}>{c.role}</div>
                    </div>
                    <button
                      onClick={() => unassignMutation.mutate(c.mover)}
                      style={{
                        background: 'var(--ops-red-dim)', border: '1px solid var(--ops-red)',
                        color: 'var(--ops-red)', borderRadius: 5, padding: '3px 8px',
                        fontSize: 10, cursor: 'pointer', fontWeight: 700,
                      }}
                    >
                      Remove
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Assign crew */}
          {booking.can_transition_to?.includes('ASSIGNED') || booking.status === 'CONFIRMED' || booking.status === 'ASSIGNED' ? (
            <div style={{ background: 'var(--ops-surface)', border: '1px solid var(--ops-border)', borderRadius: 10, padding: '20px' }}>
              <h3 style={{ fontSize: 13, fontWeight: 700, color: 'var(--ops-text)', marginBottom: 14 }}>
                Add crew member
              </h3>

              <div style={{ display: 'flex', flexDirection: 'column', gap: 8, marginBottom: 14 }}>
                {movers.filter(m => !assignedIds.has(m.user_id)).map(m => (
                  <label key={m.user_id} style={{
                    display: 'flex', alignItems: 'center', gap: 10, cursor: 'pointer',
                    padding: '10px 12px', borderRadius: 7,
                    border: `1px solid ${selectedMovers.includes(m.user_id) ? 'var(--ops-amber)' : 'var(--ops-border)'}`,
                    background: selectedMovers.includes(m.user_id) ? 'var(--ops-amber-dim)' : 'var(--ops-bg)',
                    transition: 'all 0.15s',
                  }}>
                    <input
                      type="checkbox"
                      checked={selectedMovers.includes(m.user_id)}
                      onChange={() => toggleMover(m.user_id)}
                      style={{ accentColor: 'var(--ops-amber)' }}
                    />
                    <div style={{ flex: 1 }}>
                      <div style={{ fontSize: 13, fontWeight: 600, color: 'var(--ops-text)' }}>{m.full_name}</div>
                      <div className="ops-mono" style={{ fontSize: 10, color: m.is_available ? 'var(--ops-green)' : 'var(--ops-red)' }}>
                        {m.is_available ? 'Available' : 'Unavailable'}
                      </div>
                    </div>
                  </label>
                ))}

                {movers.filter(m => !assignedIds.has(m.user_id)).length === 0 && (
                  <p style={{ fontSize: 12, color: 'var(--ops-muted)' }}>All movers are assigned.</p>
                )}
              </div>

              {selectedMovers.length > 0 && (
                <button
                  onClick={() => assignMutation.mutate()}
                  disabled={assignMutation.isPending}
                  style={{
                    width: '100%', padding: '10px',
                    background: 'var(--ops-amber)', border: 'none',
                    borderRadius: 7, color: '#0f1117', fontWeight: 700,
                    fontSize: 13, cursor: 'pointer',
                    fontFamily: 'Syne, sans-serif',
                  }}
                >
                  {assignMutation.isPending ? 'Assigning…' : `Assign ${selectedMovers.length} mover${selectedMovers.length > 1 ? 's' : ''} →`}
                </button>
              )}
            </div>
          ) : null}
        </div>
      </div>
    </div>
  )
}