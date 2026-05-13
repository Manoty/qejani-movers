// frontend/src/pages/LandingPage.jsx

import { useNavigate } from 'react-router-dom'
import Button from '../components/ui/Button'

const FEATURES = [
  {
    icon: '📦',
    title: 'Instant Quote',
    desc: 'Get an itemised price in seconds. House size, distance, add-ons — no hidden fees.',
  },
  {
    icon: '📱',
    title: 'Pay via M-Pesa',
    desc: 'Confirm and pay securely with M-Pesa STK Push. No cash upfront.',
  },
  {
    icon: '🚛',
    title: 'Professional Crew',
    desc: 'Vetted movers, insured trucks, real-time status updates on moving day.',
  },
  {
    icon: '🗓️',
    title: 'Schedule Ahead',
    desc: 'Book days in advance. We confirm within 2 hours.',
  },
]

const SIZES = [
  { label: 'Bedsitter', price: '10,000', icon: '🛏️' },
  { label: '1 Bedroom', price: '15,000', icon: '🏠' },
  { label: '2 Bedroom', price: '22,000', icon: '🏡' },
  { label: '3 Bedroom', price: '35,000', icon: '🏘️' },
]

export default function LandingPage() {
  const navigate = useNavigate()

  return (
    <div style={{ paddingTop: 64 }}>

      {/* ── Hero ── */}
      <section style={{
        minHeight: 'calc(100vh - 64px)',
        display: 'flex', alignItems: 'center',
        background: 'var(--forest)',
        position: 'relative',
        overflow: 'hidden',
        padding: '80px 2rem',
      }}>
        {/* Background texture */}
        <div style={{
          position: 'absolute', inset: 0,
          backgroundImage: `radial-gradient(circle at 20% 50%, rgba(212,130,26,0.12) 0%, transparent 60%),
                            radial-gradient(circle at 80% 20%, rgba(255,255,255,0.04) 0%, transparent 40%)`,
          pointerEvents: 'none',
        }} />

        {/* Geometric accent */}
        <div style={{
          position: 'absolute', right: '-80px', top: '10%',
          width: 480, height: 480,
          border: '1px solid rgba(255,255,255,0.06)',
          borderRadius: '50%',
          pointerEvents: 'none',
        }} />
        <div style={{
          position: 'absolute', right: '40px', top: '15%',
          width: 320, height: 320,
          border: '1px solid rgba(212,130,26,0.15)',
          borderRadius: '50%',
          pointerEvents: 'none',
        }} />

        <div style={{ maxWidth: 680, position: 'relative', zIndex: 1 }}>
          <div className="animate-fade-up" style={{
            display: 'inline-flex', alignItems: 'center', gap: 8,
            background: 'rgba(212,130,26,0.15)',
            border: '1px solid rgba(212,130,26,0.3)',
            borderRadius: 100, padding: '6px 16px',
            marginBottom: 32,
          }}>
            <span style={{ width: 6, height: 6, borderRadius: '50%', background: 'var(--amber)' }} />
            <span style={{ fontSize: 13, color: 'var(--amber-light)', fontWeight: 500 }}>
              Now serving Nairobi & environs
            </span>
          </div>

          <h1 className="serif animate-fade-up delay-100" style={{
            fontSize: 'clamp(3rem, 8vw, 5.5rem)',
            color: 'var(--cream)',
            lineHeight: 1.05,
            letterSpacing: '-1.5px',
            marginBottom: 28,
          }}>
            Moving made<br />
            <em style={{ color: 'var(--amber)', fontStyle: 'italic' }}>effortless.</em>
          </h1>

          <p className="animate-fade-up delay-200" style={{
            fontSize: 18, color: 'rgba(247,243,237,0.7)',
            lineHeight: 1.7, maxWidth: 480, marginBottom: 44,
          }}>
            Qejani Movers handles every detail of your house move — from instant
            quotes to professional crew. Transparent pricing. M-Pesa payments. No stress.
          </p>

          <div className="animate-fade-up delay-300" style={{ display: 'flex', gap: 12, flexWrap: 'wrap' }}>
            <Button
              variant="amber"
              size="lg"
              onClick={() => navigate('/quote')}
              style={{ fontSize: 16 }}
            >
              Get your free quote →
            </Button>
            <Button
              variant="ghost"
              size="lg"
              onClick={() => navigate('/login')}
              style={{ color: 'rgba(247,243,237,0.8)', fontSize: 16 }}
            >
              Sign in
            </Button>
          </div>

          <p className="animate-fade-up delay-400" style={{
            marginTop: 24, fontSize: 13, color: 'rgba(247,243,237,0.4)',
          }}>
            No account needed to get a quote.
          </p>
        </div>
      </section>

      {/* ── Pricing strip ── */}
      <section style={{
        background: 'var(--cream-dark)',
        padding: '60px 2rem',
        borderTop: '1px solid rgba(26,58,42,0.08)',
      }}>
        <div style={{ maxWidth: 900, margin: '0 auto' }}>
          <p style={{ fontSize: 13, fontWeight: 600, color: 'var(--amber)', letterSpacing: 2, textTransform: 'uppercase', textAlign: 'center', marginBottom: 8 }}>
            Starting from
          </p>
          <h2 className="serif" style={{ fontSize: 32, textAlign: 'center', color: 'var(--forest)', marginBottom: 40 }}>
            Transparent base pricing
          </h2>
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))',
            gap: 16,
          }}>
            {SIZES.map((s) => (
              <div key={s.label} style={{
                background: 'var(--white)',
                borderRadius: 12,
                padding: '24px 20px',
                textAlign: 'center',
                boxShadow: 'var(--shadow-sm)',
                border: '1px solid var(--cream-dark)',
                transition: 'transform var(--transition), box-shadow var(--transition)',
              }}
              onMouseEnter={e => { e.currentTarget.style.transform = 'translateY(-4px)'; e.currentTarget.style.boxShadow = 'var(--shadow-md)'; }}
              onMouseLeave={e => { e.currentTarget.style.transform = ''; e.currentTarget.style.boxShadow = 'var(--shadow-sm)'; }}
              >
                <div style={{ fontSize: 32, marginBottom: 10 }}>{s.icon}</div>
                <div style={{ fontWeight: 600, color: 'var(--charcoal)', marginBottom: 6 }}>{s.label}</div>
                <div className="serif" style={{ fontSize: 24, color: 'var(--forest)' }}>
                  KES {s.price}
                </div>
              </div>
            ))}
          </div>
          <p style={{ textAlign: 'center', marginTop: 20, fontSize: 13, color: 'var(--muted)' }}>
            Distance, floor access, and add-ons calculated in your quote.
          </p>
        </div>
      </section>

      {/* ── Features ── */}
      <section style={{ padding: '80px 2rem', background: 'var(--cream)' }}>
        <div style={{ maxWidth: 900, margin: '0 auto' }}>
          <h2 className="serif" style={{ fontSize: 36, color: 'var(--forest)', marginBottom: 48, textAlign: 'center' }}>
            Everything handled for you
          </h2>
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
            gap: 32,
          }}>
            {FEATURES.map((f) => (
              <div key={f.title}>
                <div style={{ fontSize: 36, marginBottom: 14 }}>{f.icon}</div>
                <h3 style={{ fontSize: 18, fontWeight: 600, color: 'var(--forest)', marginBottom: 8 }}>{f.title}</h3>
                <p style={{ fontSize: 14, color: 'var(--muted)', lineHeight: 1.7 }}>{f.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── CTA ── */}
      <section style={{
        background: 'var(--forest)',
        padding: '80px 2rem',
        textAlign: 'center',
      }}>
        <h2 className="serif" style={{ fontSize: 40, color: 'var(--cream)', marginBottom: 16 }}>
          Ready to move?
        </h2>
        <p style={{ color: 'rgba(247,243,237,0.6)', marginBottom: 36, fontSize: 17 }}>
          Get an itemised quote in 60 seconds. No signup required.
        </p>
        <Button variant="amber" size="lg" onClick={() => navigate('/quote')}>
          Start my quote →
        </Button>
      </section>

      {/* ── Footer ── */}
      <footer style={{
        background: 'var(--charcoal)',
        padding: '32px 2rem',
        textAlign: 'center',
      }}>
        <p style={{ fontSize: 13, color: 'rgba(255,255,255,0.3)' }}>
          © 2025 Qejani Movers · Nairobi, Kenya
        </p>
      </footer>

      <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
    </div>
  )
}