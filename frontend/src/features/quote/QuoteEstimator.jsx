// frontend/src/features/quote/QuoteEstimator.jsx

import { useState } from 'react'
import { useQuery, useMutation } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import api from '../../lib/axios'
import Button from '../../components/ui/Button'
import Input from '../../components/ui/Input'
import Select from '../../components/ui/Select'
import { useAuth } from '../auth/AuthContext'

const STEPS = ['Move details', 'Access & add-ons', 'Your quote']

function StepIndicator({ current }) {
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 0, marginBottom: 40 }}>
      {STEPS.map((label, i) => (
        <div key={i} style={{ display: 'flex', alignItems: 'center', flex: i < STEPS.length - 1 ? 1 : 0 }}>
          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 6 }}>
            <div style={{
              width: 32, height: 32, borderRadius: '50%',
              background: i <= current ? 'var(--forest)' : 'var(--cream-dark)',
              color: i <= current ? 'white' : 'var(--muted)',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              fontSize: 13, fontWeight: 600,
              transition: 'background var(--transition)',
            }}>
              {i < current ? '✓' : i + 1}
            </div>
            <span style={{ fontSize: 11, color: i === current ? 'var(--forest)' : 'var(--muted)', fontWeight: i === current ? 600 : 400, whiteSpace: 'nowrap' }}>
              {label}
            </span>
          </div>
          {i < STEPS.length - 1 && (
            <div style={{
              flex: 1, height: 1, margin: '0 8px', marginBottom: 22,
              background: i < current ? 'var(--forest)' : 'var(--cream-dark)',
              transition: 'background var(--transition)',
            }} />
          )}
        </div>
      ))}
    </div>
  )
}

function QuoteBreakdown({ result, onBook }) {
  const { user } = useAuth()
  const navigate = useNavigate()

  return (
    <div className="animate-fade-up">
      <div style={{
        background: 'var(--forest)',
        borderRadius: 14,
        padding: '28px 24px',
        marginBottom: 20,
        color: 'var(--cream)',
      }}>
        <p style={{ fontSize: 12, opacity: 0.6, marginBottom: 4, textTransform: 'uppercase', letterSpacing: 1 }}>
          Estimated total
        </p>
        <div className="serif" style={{ fontSize: 52, letterSpacing: '-1px' }}>
          KES {Number(result.total).toLocaleString()}
        </div>
        <p style={{ fontSize: 12, opacity: 0.5, marginTop: 4 }}>{result.currency}</p>
      </div>

      <div style={{
        background: 'var(--white)',
        borderRadius: 12,
        overflow: 'hidden',
        border: '1px solid var(--cream-dark)',
        marginBottom: 24,
      }}>
        {result.line_items.map((item, i) => (
          <div key={i} style={{
            display: 'flex', justifyContent: 'space-between', alignItems: 'center',
            padding: '14px 20px',
            borderBottom: i < result.line_items.length - 1 ? '1px solid var(--cream-dark)' : 'none',
          }}>
            <span style={{ fontSize: 14, color: 'var(--charcoal)' }}>{item.label}</span>
            <span style={{ fontSize: 14, fontWeight: 600, color: 'var(--forest)' }}>
              KES {Number(item.amount).toLocaleString()}
            </span>
          </div>
        ))}
      </div>

      <Button
        variant="amber"
        size="lg"
        style={{ width: '100%', justifyContent: 'center', fontSize: 16 }}
        onClick={() => {
          if (!user) navigate('/login', { state: { redirectTo: '/book', quoteData: result } })
          else onBook()
        }}
      >
        {user ? 'Book this move →' : 'Sign in to book →'}
      </Button>
      {!user && (
        <p style={{ textAlign: 'center', fontSize: 12, color: 'var(--muted)', marginTop: 10 }}>
          You'll return here after signing in.
        </p>
      )}
    </div>
  )
}

export default function QuoteEstimator() {
  const navigate = useNavigate()
  const [step, setStep] = useState(0)
  const [form, setForm] = useState({
    house_size: '',
    distance_km: '',
    pickup_address: '',
    destination_address: '',
    floor_number: '1',
    has_lift: false,
    addon_ids: [],
  })

  const { data: addons = [] } = useQuery({
    queryKey: ['addons'],
    queryFn: () => api.get('/pricing/addons/').then(r => r.data),
  })

  const quoteMutation = useMutation({
    mutationFn: (payload) => api.post('/pricing/quote/', payload).then(r => r.data),
  })

  const set = (key, val) => setForm(f => ({ ...f, [key]: val }))

  const toggleAddon = (id) => {
    setForm(f => ({
      ...f,
      addon_ids: f.addon_ids.includes(id)
        ? f.addon_ids.filter(a => a !== id)
        : [...f.addon_ids, id],
    }))
  }

  const handleGetQuote = () => {
    quoteMutation.mutate({
      house_size: form.house_size,
      distance_km: parseFloat(form.distance_km),
      floor_number: parseInt(form.floor_number),
      has_lift: form.has_lift,
      addon_ids: form.addon_ids,
    })
    setStep(2)
  }

  return (
    <div style={{ minHeight: '100vh', paddingTop: 64, background: 'var(--cream)', padding: '80px 1rem 60px' }}>
      <div style={{ maxWidth: 560, margin: '0 auto' }}>

        <div className="animate-fade-up" style={{ marginBottom: 36 }}>
          <p style={{ fontSize: 12, fontWeight: 600, color: 'var(--amber)', letterSpacing: 2, textTransform: 'uppercase', marginBottom: 8 }}>
            Free estimate
          </p>
          <h1 className="serif" style={{ fontSize: 36, color: 'var(--forest)', letterSpacing: '-0.5px' }}>
            Get your moving quote
          </h1>
        </div>

        <StepIndicator current={step} />

        {/* Step 0 — Move details */}
        {step === 0 && (
          <div className="animate-fade-up" style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
            <Select
              label="House size"
              value={form.house_size}
              onChange={e => set('house_size', e.target.value)}
            >
              <option value="">Select house size</option>
              <option value="BEDSITTER">Bedsitter — KES 10,000</option>
              <option value="ONE_BEDROOM">1 Bedroom — KES 15,000</option>
              <option value="TWO_BEDROOM">2 Bedroom — KES 22,000</option>
              <option value="THREE_BEDROOM">3 Bedroom — KES 35,000</option>
            </Select>

            <Input
              label="Distance to new location (km)"
              type="number"
              min="0.5"
              max="500"
              placeholder="e.g. 12"
              value={form.distance_km}
              onChange={e => set('distance_km', e.target.value)}
            />

            <Input
              label="Pickup address"
              placeholder="e.g. 45 Westlands Road, Nairobi"
              value={form.pickup_address}
              onChange={e => set('pickup_address', e.target.value)}
            />

            <Input
              label="Destination address"
              placeholder="e.g. 12 Kilimani Avenue, Nairobi"
              value={form.destination_address}
              onChange={e => set('destination_address', e.target.value)}
            />

            <Button
              variant="primary"
              size="lg"
              style={{ marginTop: 8 }}
              disabled={!form.house_size || !form.distance_km || !form.pickup_address || !form.destination_address}
              onClick={() => setStep(1)}
            >
              Next: Access details →
            </Button>
          </div>
        )}

        {/* Step 1 — Access & add-ons */}
        {step === 1 && (
          <div className="animate-fade-up" style={{ display: 'flex', flexDirection: 'column', gap: 24 }}>
            <Input
              label="Which floor are you moving from?"
              type="number"
              min="1"
              max="50"
              value={form.floor_number}
              onChange={e => set('floor_number', e.target.value)}
            />

            <div>
              <label style={{ fontSize: 13, fontWeight: 500, color: 'var(--muted)', display: 'block', marginBottom: 10 }}>
                Lift available in the building?
              </label>
              <div style={{ display: 'flex', gap: 10 }}>
                {[['Yes', true], ['No', false]].map(([label, val]) => (
                  <button
                    key={label}
                    onClick={() => set('has_lift', val)}
                    style={{
                      flex: 1, padding: '11px 0',
                      borderRadius: 'var(--radius)',
                      border: `1.5px solid ${form.has_lift === val ? 'var(--forest)' : 'var(--cream-dark)'}`,
                      background: form.has_lift === val ? 'var(--forest)' : 'var(--white)',
                      color: form.has_lift === val ? 'white' : 'var(--charcoal)',
                      cursor: 'pointer', fontSize: 14, fontWeight: 500,
                      transition: 'all var(--transition)',
                    }}
                  >
                    {label}
                  </button>
                ))}
              </div>
            </div>

            {addons.length > 0 && (
              <div>
                <label style={{ fontSize: 13, fontWeight: 500, color: 'var(--muted)', display: 'block', marginBottom: 10 }}>
                  Add-on services (optional)
                </label>
                <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                  {addons.map(addon => {
                    const selected = form.addon_ids.includes(addon.id)
                    return (
                      <button
                        key={addon.id}
                        onClick={() => toggleAddon(addon.id)}
                        style={{
                          display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                          padding: '14px 16px',
                          borderRadius: 'var(--radius)',
                          border: `1.5px solid ${selected ? 'var(--forest)' : 'var(--cream-dark)'}`,
                          background: selected ? 'rgba(26,58,42,0.04)' : 'var(--white)',
                          cursor: 'pointer', textAlign: 'left',
                          transition: 'all var(--transition)',
                        }}
                      >
                        <div>
                          <div style={{ fontSize: 14, fontWeight: 500, color: 'var(--charcoal)' }}>{addon.name}</div>
                          <div style={{ fontSize: 12, color: 'var(--muted)', marginTop: 2 }}>{addon.description}</div>
                        </div>
                        <div style={{ display: 'flex', alignItems: 'center', gap: 10, flexShrink: 0 }}>
                          <span style={{ fontSize: 13, fontWeight: 600, color: 'var(--forest)' }}>
                            +KES {Number(addon.price).toLocaleString()}
                          </span>
                          <div style={{
                            width: 20, height: 20, borderRadius: '50%',
                            border: `2px solid ${selected ? 'var(--forest)' : 'var(--cream-dark)'}`,
                            background: selected ? 'var(--forest)' : 'transparent',
                            display: 'flex', alignItems: 'center', justifyContent: 'center',
                          }}>
                            {selected && <span style={{ color: 'white', fontSize: 11 }}>✓</span>}
                          </div>
                        </div>
                      </button>
                    )
                  })}
                </div>
              </div>
            )}

            <div style={{ display: 'flex', gap: 12 }}>
              <Button variant="ghost" size="lg" style={{ flex: 1 }} onClick={() => setStep(0)}>
                ← Back
              </Button>
              <Button
                variant="primary"
                size="lg"
                style={{ flex: 2 }}
                loading={quoteMutation.isPending}
                onClick={handleGetQuote}
              >
                Calculate quote →
              </Button>
            </div>
          </div>
        )}

        {/* Step 2 — Result */}
        {step === 2 && (
          <div>
            {quoteMutation.isPending && (
              <div style={{ textAlign: 'center', padding: '60px 0', color: 'var(--muted)' }}>
                Calculating your quote…
              </div>
            )}
            {quoteMutation.isError && (
              <div style={{ textAlign: 'center', padding: '40px 0', color: '#e53e3e' }}>
                <p>Something went wrong. Please try again.</p>
                <Button variant="outline" size="sm" onClick={() => setStep(1)} style={{ marginTop: 16 }}>
                  Try again
                </Button>
              </div>
            )}
            {quoteMutation.isSuccess && (
              <QuoteBreakdown
                result={quoteMutation.data}
                onBook={() => navigate('/book', { state: { quote: quoteMutation.data, formData: form } })}
              />
            )}
          </div>
        )}
      </div>
      <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
    </div>
  )
}