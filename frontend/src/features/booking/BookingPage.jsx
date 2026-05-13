// frontend/src/features/booking/BookingPage.jsx

import { useState } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'
import { useMutation } from '@tanstack/react-query'
import api from '../../lib/axios'
import Button from '../../components/ui/Button'
import Input from '../../components/ui/Input'

export default function BookingPage() {
  const { state } = useLocation()
  const navigate = useNavigate()
  const quote = state?.quote
  const formData = state?.formData

  const [notes, setNotes]     = useState('')
  const [date, setDate]       = useState('')
  const [time, setTime]       = useState('')
  const [error, setError]     = useState('')

  const mutation = useMutation({
    mutationFn: (payload) => api.post('/bookings/', payload).then(r => r.data),
    onSuccess: (data) => navigate(`/dashboard?new=${data.id}`),
    onError: (err) => setError(err.response?.data?.detail || 'Booking failed. Please try again.'),
  })

  if (!quote || !formData) {
    return (
      <div style={{ minHeight: '100vh', paddingTop: 100, textAlign: 'center' }}>
        <p style={{ color: 'var(--muted)', marginBottom: 20 }}>No quote found. Please start from the quote page.</p>
        <Button onClick={() => navigate('/quote')}>Get a quote</Button>
      </div>
    )
  }

  const handleSubmit = () => {
    setError('')
    mutation.mutate({
      house_size: formData.house_size,
      distance_km: parseFloat(formData.distance_km),
      pickup_address: formData.pickup_address,
      pickup_floor: parseInt(formData.floor_number),
      pickup_has_lift: formData.has_lift,
      destination_address: formData.destination_address,
      addon_ids: formData.addon_ids,
      inventory_notes: notes,
      scheduled_date: date || null,
      scheduled_time: time || null,
    })
  }

  return (
    <div style={{ minHeight: '100vh', paddingTop: 80, background: 'var(--cream)', padding: '80px 1rem 60px' }}>
      <div style={{ maxWidth: 560, margin: '0 auto' }}>

        <div className="animate-fade-up" style={{ marginBottom: 36 }}>
          <p style={{ fontSize: 12, fontWeight: 600, color: 'var(--amber)', letterSpacing: 2, textTransform: 'uppercase', marginBottom: 8 }}>
            Confirm booking
          </p>
          <h1 className="serif" style={{ fontSize: 34, color: 'var(--forest)' }}>
            Almost there
          </h1>
          <p style={{ color: 'var(--muted)', marginTop: 8, fontSize: 15 }}>
            Review your quote and confirm your move.
          </p>
        </div>

        {/* Quote summary */}
        <div className="animate-fade-up" style={{
          background: 'var(--forest)',
          borderRadius: 14, padding: '24px',
          marginBottom: 24, color: 'var(--cream)',
        }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 20 }}>
            <div>
              <p style={{ fontSize: 12, opacity: 0.5, marginBottom: 4 }}>Total estimate</p>
              <div className="serif" style={{ fontSize: 38, letterSpacing: '-0.5px' }}>
                KES {Number(quote.total).toLocaleString()}
              </div>
            </div>
            <button
              onClick={() => navigate('/quote')}
              style={{ background: 'rgba(255,255,255,0.1)', border: 'none', color: 'rgba(247,243,237,0.7)', padding: '6px 12px', borderRadius: 8, cursor: 'pointer', fontSize: 12 }}
            >
              Edit quote
            </button>
          </div>
          {quote.line_items.map((item, i) => (
            <div key={i} style={{
              display: 'flex', justifyContent: 'space-between',
              fontSize: 13, opacity: 0.7, padding: '5px 0',
              borderBottom: i < quote.line_items.length - 1 ? '1px solid rgba(255,255,255,0.08)' : 'none',
            }}>
              <span>{item.label}</span>
              <span>KES {Number(item.amount).toLocaleString()}</span>
            </div>
          ))}
        </div>

        {/* Move details */}
        <div className="animate-fade-up delay-100" style={{
          background: 'var(--white)', borderRadius: 12, padding: '20px',
          border: '1px solid var(--cream-dark)', marginBottom: 20,
        }}>
          <h3 style={{ fontSize: 14, fontWeight: 600, color: 'var(--forest)', marginBottom: 14 }}>Move details</h3>
          {[
            ['From', formData.pickup_address],
            ['To', formData.destination_address],
            ['Distance', `${formData.distance_km} km`],
            ['Floor', `${formData.floor_number}${formData.has_lift ? ' (lift available)' : ''}`],
          ].map(([label, val]) => (
            <div key={label} style={{ display: 'flex', gap: 12, marginBottom: 8 }}>
              <span style={{ fontSize: 13, color: 'var(--muted)', minWidth: 70 }}>{label}</span>
              <span style={{ fontSize: 13, color: 'var(--charcoal)', fontWeight: 500 }}>{val}</span>
            </div>
          ))}
        </div>

        {/* Schedule & notes */}
        <div className="animate-fade-up delay-200" style={{ display: 'flex', flexDirection: 'column', gap: 16, marginBottom: 24 }}>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
            <Input
              label="Preferred date (optional)"
              type="date"
              value={date}
              onChange={e => setDate(e.target.value)}
              min={new Date().toISOString().split('T')[0]}
            />
            <Input
              label="Preferred time (optional)"
              type="time"
              value={time}
              onChange={e => setTime(e.target.value)}
            />
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
            <label style={{ fontSize: 13, fontWeight: 500, color: 'var(--muted)' }}>
              Inventory notes (optional)
            </label>
            <textarea
              rows={3}
              placeholder="e.g. Handle the piano with extra care. 2 large sofas."
              value={notes}
              onChange={e => setNotes(e.target.value)}
              style={{
                width: '100%', padding: '12px 16px',
                borderRadius: 'var(--radius)',
                border: '1.5px solid var(--cream-dark)',
                background: 'var(--white)',
                fontSize: 14, resize: 'vertical', outline: 'none',
                fontFamily: 'inherit',
              }}
              onFocus={e => e.target.style.borderColor = 'var(--forest)'}
              onBlur={e => e.target.style.borderColor = 'var(--cream-dark)'}
            />
          </div>
        </div>

        {error && (
          <div style={{
            background: '#fff5f5', border: '1px solid #fed7d7',
            borderRadius: 8, padding: '12px 16px',
            color: '#c53030', fontSize: 14, marginBottom: 16,
          }}>
            {error}
          </div>
        )}

        <div className="animate-fade-up delay-300">
          <Button
            variant="amber"
            size="lg"
            loading={mutation.isPending}
            style={{ width: '100%', justifyContent: 'center', fontSize: 16 }}
            onClick={handleSubmit}
          >
            Confirm booking →
          </Button>
          <p style={{ textAlign: 'center', fontSize: 12, color: 'var(--muted)', marginTop: 12 }}>
            Payment is collected after we confirm your booking by phone.
          </p>
        </div>
      </div>
      <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
    </div>
  )
}