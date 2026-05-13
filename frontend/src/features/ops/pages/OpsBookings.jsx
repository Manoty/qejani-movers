// frontend/src/features/ops/pages/OpsBookings.jsx

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import { fetchOpsBookings, updateBookingStatus } from '../api/opsApi'
import { OpsStatusBadge } from '../components/OpsStatusBadge'

const STATUSES = ['', 'PENDING', 'CONFIRMED', 'ASSIGNED', 'ON_THE_WAY', 'MOVING', 'COMPLETED', 'CANCELLED']

const TRANSITIONS = {
  PENDING:    ['CONFIRMED', 'CANCELLED'],
  CONFIRMED:  ['ASSIGNED', 'CANCELLED'],
  ASSIGNED:   ['ON_THE_WAY'],
  ON_THE_WAY: ['MOVING'],
  MOVING:     ['COMPLETED'],
  COMPLETED:  [],
  CANCELLED:  [],
}

export default function OpsBookings() {
  const navigate = useNavigate()
  const qc = useQueryClient()
  const [statusFilter, setStatusFilter] = useState('')
  const [updatingId, setUpdatingId] = useState(null)
  const [cancellationReason, setCancellationReason] = useState('')
  const [pendingCancel, setPendingCancel] = useState(null) // { bookingId, newStatus }

  const { data: bookings = [], isLoading } = useQuery({
    queryKey: ['ops-bookings-all', statusFilter],
    queryFn: () => fetchOpsBookings(statusFilter ? { status: statusFilter } : {}),
  })

  const mutation = useMutation({
    mutationFn: ({ id, payload }) => updateBookingStatus(id, payload),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['ops-bookings-all'] })
      qc.invalidateQueries({ queryKey: ['ops-overview'] })
      setUpdatingId(null)
      setPendingCancel(null)
      setCancellationReason('')
    },
  })

  const handleStatusChange = (bookingId, newStatus) => {
    if (newStatus === 'CANCELLED') {
      setPendingCancel({ bookingId, newStatus })
      return
    }
    setUpdatingId(bookingId)
    mutation.mutate({ id: bookingId, payload: { status: newStatus } })
  }

  const confirmCancel = () => {
    if (!cancellationReason.trim()) return
    setUpdatingId(pendingCancel.bookingId)
    mutation.mutate({
      id: pendingCancel.bookingId,
      payload: { status: 'CANCELLED', cancellation_reason: cancellationReason },
    })
  }

  return (
    <div className="ops-animate">
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 28 }}>
        <div>
          <h1 style={{ fontSize: 24, fontWeight: 800, color: 'var(--ops-text)' }}>Bookings</h1>
          <p style={{ fontSize: 13, color: 'var(--ops-muted)', marginTop: 2 }}>
            {bookings.length} booking{bookings.length !== 1 ? 's' : ''} shown
          </p>
        </div>

        {/* Status filter */}
        <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
          {STATUSES.map(s => (
            <button
              key={s || 'all'}
              onClick={() => setStatusFilter(s)}
              style={{
                padding: '6px 12px', borderRadius: 6, fontSize: 11, fontWeight: 700,
                border: '1px solid var(--ops-border)',
                background: statusFilter === s ? 'var(--ops-amber)' : 'var(--ops-surface)',
                color: statusFilter === s ? '#0f1117' : 'var(--ops-muted)',
                cursor: 'pointer', transition: 'all 0.15s',
                fontFamily: 'JetBrains Mono, monospace',
              }}
            >
              {s || 'ALL'}
            </button>
          ))}
        </div>
      </div>

      {/* Cancellation modal */}
      {pendingCancel && (
        <div style={{
          position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.7)',
          display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000,
        }}>
          <div style={{
            background: 'var(--ops-surface)', border: '1px solid var(--ops-border)',
            borderRadius: 12, padding: '28px', width: '100%', maxWidth: 420,
          }}>
            <h3 style={{ fontSize: 16, fontWeight: 700, color: 'var(--ops-text)', marginBottom: 8 }}>
              Cancel booking
            </h3>
            <p style={{ fontSize: 13, color: 'var(--ops-muted)', marginBottom: 16 }}>
              Provide a reason. This is recorded for audit.
            </p>
            <textarea
              rows={3}
              value={cancellationReason}
              onChange={e => setCancellationReason(e.target.value)}
              placeholder="e.g. Customer requested cancellation by phone."
              style={{
                width: '100%', padding: '10px 14px',
                background: 'var(--ops-bg)', border: '1px solid var(--ops-border)',
                borderRadius: 8, color: 'var(--ops-text)', fontSize: 13,
                resize: 'vertical', outline: 'none', fontFamily: 'inherit', marginBottom: 16,
              }}
            />
            <div style={{ display: 'flex', gap: 10 }}>
              <button
                onClick={() => { setPendingCancel(null); setCancellationReason('') }}
                style={{ flex: 1, padding: '10px', background: 'var(--ops-bg)', border: '1px solid var(--ops-border)', borderRadius: 8, color: 'var(--ops-muted)', cursor: 'pointer', fontSize: 13 }}
              >
                Dismiss
              </button>
              <button
                onClick={confirmCancel}
                disabled={!cancellationReason.trim()}
                style={{
                  flex: 1, padding: '10px',
                  background: cancellationReason.trim() ? 'var(--ops-red)' : 'rgba(239,68,68,0.3)',
                  border: 'none', borderRadius: 8, color: 'white',
                  cursor: cancellationReason.trim() ? 'pointer' : 'not-allowed',
                  fontSize: 13, fontWeight: 700,
                }}
              >
                Confirm cancel
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Table */}
      <div style={{ background: 'var(--ops-surface)', border: '1px solid var(--ops-border)', borderRadius: 10, overflow: 'hidden' }}>
        {/* Header */}
        <div style={{
          display: 'grid', gridTemplateColumns: '2fr 1.2fr 1fr 110px 130px 140px',
          gap: 12, padding: '11px 18px',
          borderBottom: '1px solid var(--ops-border)',
          fontSize: 10, fontWeight: 700, color: 'var(--ops-muted)',
          letterSpacing: 1, textTransform: 'uppercase',
        }}>
          {['Customer / Move', 'From → To', 'Date', 'Total', 'Status', 'Action'].map(h => (
            <span key={h}>{h}</span>
          ))}
        </div>

        {isLoading ? (
          <div style={{ padding: '60px', textAlign: 'center', color: 'var(--ops-muted)' }}>
            Loading…
          </div>
        ) : bookings.length === 0 ? (
          <div style={{ padding: '60px', textAlign: 'center', color: 'var(--ops-muted)', fontSize: 13 }}>
            No bookings match this filter.
          </div>
        ) : (
          bookings.map((b, i) => {
            const transitions = TRANSITIONS[b.status] || []
            const isUpdating = updatingId === b.id

            return (
              <div
                key={b.id}
                style={{
                  display: 'grid', gridTemplateColumns: '2fr 1.2fr 1fr 110px 130px 140px',
                  gap: 12, alignItems: 'center', padding: '13px 18px',
                  borderBottom: i < bookings.length - 1 ? '1px solid var(--ops-border)' : 'none',
                  transition: 'background 0.15s',
                }}
                onMouseEnter={e => e.currentTarget.style.background = 'rgba(255,255,255,0.02)'}
                onMouseLeave={e => e.currentTarget.style.background = 'transparent'}
              >
                {/* Customer / Move */}
                <div
                  style={{ cursor: 'pointer' }}
                  onClick={() => navigate(`/ops/bookings/${b.id}`)}
                >
                  <div style={{ fontSize: 13, fontWeight: 600, color: 'var(--ops-text)', marginBottom: 2 }}>
                    {b.customer_name}
                  </div>
                  <div className="ops-mono" style={{ fontSize: 11, color: 'var(--ops-muted)' }}>
                    {b.house_size.replace('_', ' ')}
                  </div>
                </div>

                {/* From → To */}
                <div className="ops-mono" style={{ fontSize: 11, color: 'var(--ops-muted)', lineHeight: 1.6 }}>
                  <div style={{ color: 'var(--ops-text)', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', maxWidth: 160 }}>
                    {b.pickup_address.split(',')[0]}
                  </div>
                  <div style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', maxWidth: 160 }}>
                    {b.destination_address.split(',')[0]}
                  </div>
                </div>

                {/* Date */}
                <div className="ops-mono" style={{ fontSize: 12, color: 'var(--ops-muted)' }}>
                  {b.scheduled_date || <span style={{ opacity: 0.4 }}>—</span>}
                </div>

                {/* Total */}
                <div className="ops-mono" style={{ fontSize: 13, color: 'var(--ops-amber)', fontWeight: 600 }}>
                  {Number(b.quoted_total).toLocaleString()}
                </div>

                {/* Status */}
                <OpsStatusBadge status={b.status} />

                {/* Action */}
                {transitions.length > 0 ? (
                  <select
                    disabled={isUpdating}
                    value=""
                    onChange={e => e.target.value && handleStatusChange(b.id, e.target.value)}
                    style={{
                      background: isUpdating ? 'rgba(245,158,11,0.1)' : 'var(--ops-bg)',
                      border: '1px solid var(--ops-border)',
                      borderRadius: 6, color: 'var(--ops-amber)',
                      fontSize: 11, padding: '5px 8px',
                      cursor: isUpdating ? 'not-allowed' : 'pointer',
                      fontFamily: 'JetBrains Mono, monospace',
                      width: '100%',
                    }}
                  >
                    <option value="">{isUpdating ? 'Updating…' : 'Move to…'}</option>
                    {transitions.map(t => (
                      <option key={t} value={t}>{t}</option>
                    ))}
                  </select>
                ) : (
                  <span style={{ fontSize: 11, color: 'var(--ops-muted)', fontFamily: 'JetBrains Mono, monospace' }}>
                    Terminal
                  </span>
                )}
              </div>
            )
          })
        )}
      </div>
    </div>
  )
}