// frontend/src/features/ops/pages/OpsAnalytics.jsx

import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import {
  fetchAnalyticsOverview,
  fetchDailyRevenue,
  fetchBookingVolumes,
  fetchHouseSizeBreakdown,
} from '../api/opsApi'

function getRangeParams(days) {
  const until = new Date().toISOString().split('T')[0]
  const since = new Date(Date.now() - days * 86400000).toISOString().split('T')[0]
  return { since, until }
}

function BarChart({ data, valueKey, labelKey, color = 'var(--ops-amber)', prefix = '' }) {
  if (!data?.length) return (
    <div style={{ textAlign: 'center', padding: '40px', color: 'var(--ops-muted)', fontSize: 12 }}>
      No data for this period.
    </div>
  )
  const max = Math.max(...data.map(d => Number(d[valueKey]) || 0))

  return (
    <div style={{ display: 'flex', gap: 3, alignItems: 'flex-end', height: 120, padding: '0 4px' }}>
      {data.map((row, i) => {
        const val = Number(row[valueKey]) || 0
        const pct = max > 0 ? (val / max) * 100 : 0
        return (
          <div
            key={i}
            title={`${row[labelKey]}: ${prefix}${val.toLocaleString()}`}
            style={{
              flex: 1, display: 'flex', flexDirection: 'column',
              alignItems: 'center', justifyContent: 'flex-end', gap: 4,
            }}
          >
            <div style={{
              width: '100%', height: `${Math.max(pct, 2)}%`,
              background: color,
              borderRadius: '3px 3px 0 0',
              opacity: 0.85,
              transition: 'height 0.4s ease',
              minHeight: 2,
            }} />
          </div>
        )
      })}
    </div>
  )
}

export default function OpsAnalytics() {
  const [range, setRange] = useState(30)
  const params = getRangeParams(range)

  const { data: overview } = useQuery({
    queryKey: ['ops-overview', params.since, params.until],
    queryFn: () => fetchAnalyticsOverview(params),
  })

  const { data: revenue = [] } = useQuery({
    queryKey: ['ops-revenue', params.since, params.until],
    queryFn: () => fetchDailyRevenue(params),
  })

  const { data: volumes = [] } = useQuery({
    queryKey: ['ops-volumes', params.since, params.until],
    queryFn: () => fetchBookingVolumes(params),
  })

  const { data: houseSizes = [] } = useQuery({
    queryKey: ['ops-house-sizes', params.since, params.until],
    queryFn: () => fetchHouseSizeBreakdown(params),
  })

  const totalRevenue = overview?.revenue?.total || '0'
  const mpesaRev    = overview?.revenue?.mpesa  || '0'
  const cashRev     = overview?.revenue?.cash   || '0'

  return (
    <div className="ops-animate">
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 28 }}>
        <div>
          <h1 style={{ fontSize: 24, fontWeight: 800, color: 'var(--ops-text)' }}>Analytics</h1>
          <p style={{ fontSize: 13, color: 'var(--ops-muted)', marginTop: 2 }}>
            {params.since} → {params.until}
          </p>
        </div>
        <div style={{ display: 'flex', gap: 6 }}>
          {[7, 30, 90].map(d => (
            <button
              key={d}
              onClick={() => setRange(d)}
              style={{
                padding: '6px 14px', borderRadius: 6, fontSize: 11, fontWeight: 700,
                border: '1px solid var(--ops-border)',
                background: range === d ? 'var(--ops-amber)' : 'var(--ops-surface)',
                color: range === d ? '#0f1117' : 'var(--ops-muted)',
                cursor: 'pointer', fontFamily: 'JetBrains Mono, monospace',
              }}
            >
              {d}d
            </button>
          ))}
        </div>
      </div>

      {/* Revenue cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 14, marginBottom: 24 }}>
        {[
          { label: 'Total Revenue', value: totalRevenue, color: 'var(--ops-amber)' },
          { label: 'M-Pesa',        value: mpesaRev,     color: 'var(--ops-green)' },
          { label: 'Cash',          value: cashRev,      color: 'var(--ops-blue)'  },
        ].map(s => (
          <div key={s.label} style={{
            background: 'var(--ops-surface)', border: '1px solid var(--ops-border)',
            borderRadius: 10, padding: '20px',
          }}>
            <p style={{ fontSize: 10, color: 'var(--ops-muted)', fontWeight: 600, letterSpacing: 1, textTransform: 'uppercase', marginBottom: 10 }}>
              {s.label}
            </p>
            <p className="ops-mono" style={{ fontSize: 24, fontWeight: 600, color: s.color }}>
              {Number(s.value).toLocaleString()}
            </p>
            <p style={{ fontSize: 10, color: 'var(--ops-muted)', marginTop: 4 }}>KES</p>
          </div>
        ))}
      </div>

      {/* Booking status breakdown */}
      {overview?.bookings?.by_status && (
        <div style={{ background: 'var(--ops-surface)', border: '1px solid var(--ops-border)', borderRadius: 10, padding: '20px', marginBottom: 24 }}>
          <h3 style={{ fontSize: 13, fontWeight: 700, color: 'var(--ops-text)', marginBottom: 16 }}>
            Bookings by status
          </h3>
          <div style={{ display: 'flex', gap: 10, flexWrap: 'wrap' }}>
            {Object.entries(overview.bookings.by_status).map(([status, count]) => (
              <div key={status} style={{
                background: 'var(--ops-bg)', border: '1px solid var(--ops-border)',
                borderRadius: 8, padding: '10px 16px', textAlign: 'center',
              }}>
                <div className="ops-mono" style={{ fontSize: 22, fontWeight: 600, color: 'var(--ops-text)' }}>{count}</div>
                <div style={{ fontSize: 10, color: 'var(--ops-muted)', fontWeight: 600, letterSpacing: 1, textTransform: 'uppercase', marginTop: 4 }}>{status}</div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Charts row */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16, marginBottom: 24 }}>
        <div style={{ background: 'var(--ops-surface)', border: '1px solid var(--ops-border)', borderRadius: 10, padding: '20px' }}>
          <h3 style={{ fontSize: 13, fontWeight: 700, color: 'var(--ops-text)', marginBottom: 4 }}>Daily Revenue</h3>
          <p style={{ fontSize: 11, color: 'var(--ops-muted)', marginBottom: 16 }}>KES collected per day</p>
          <BarChart data={revenue} valueKey="revenue" labelKey="date" color="var(--ops-amber)" prefix="KES " />
        </div>

        <div style={{ background: 'var(--ops-surface)', border: '1px solid var(--ops-border)', borderRadius: 10, padding: '20px' }}>
          <h3 style={{ fontSize: 13, fontWeight: 700, color: 'var(--ops-text)', marginBottom: 4 }}>Booking Volume</h3>
          <p style={{ fontSize: 11, color: 'var(--ops-muted)', marginBottom: 16 }}>Bookings created per day</p>
          <BarChart data={volumes} valueKey="total" labelKey="date" color="var(--ops-blue)" />
        </div>
      </div>

      {/* House size breakdown */}
      {houseSizes.length > 0 && (
        <div style={{ background: 'var(--ops-surface)', border: '1px solid var(--ops-border)', borderRadius: 10, padding: '20px' }}>
          <h3 style={{ fontSize: 13, fontWeight: 700, color: 'var(--ops-text)', marginBottom: 16 }}>
            Completed moves by house size
          </h3>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(160px, 1fr))', gap: 12 }}>
            {houseSizes.map(row => (
              <div key={row.house_size} style={{
                background: 'var(--ops-bg)', border: '1px solid var(--ops-border)', borderRadius: 8, padding: '14px',
              }}>
                <div style={{ fontSize: 10, color: 'var(--ops-muted)', fontWeight: 600, letterSpacing: 1, textTransform: 'uppercase', marginBottom: 8 }}>
                  {row.house_size.replace('_', ' ')}
                </div>
                <div className="ops-mono" style={{ fontSize: 20, fontWeight: 600, color: 'var(--ops-text)', marginBottom: 4 }}>
                  {row.count}
                </div>
                <div className="ops-mono" style={{ fontSize: 11, color: 'var(--ops-amber)' }}>
                  KES {Number(row.total_revenue).toLocaleString()}
                </div>
                <div style={{ fontSize: 10, color: 'var(--ops-muted)', marginTop: 2 }}>
                  avg KES {Number(row.avg_value).toLocaleString()}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}