// frontend/src/features/ops/components/OpsStatusBadge.jsx

const META = {
  PENDING:    { label: 'Pending',     color: '#f59e0b', bg: 'rgba(245,158,11,0.12)' },
  CONFIRMED:  { label: 'Confirmed',   color: '#10b981', bg: 'rgba(16,185,129,0.1)'  },
  ASSIGNED:   { label: 'Assigned',    color: '#3b82f6', bg: 'rgba(59,130,246,0.1)'  },
  ON_THE_WAY: { label: 'On the way',  color: '#8b5cf6', bg: 'rgba(139,92,246,0.1)'  },
  MOVING:     { label: 'Moving',      color: '#ec4899', bg: 'rgba(236,72,153,0.1)'  },
  COMPLETED:  { label: 'Completed',   color: '#10b981', bg: 'rgba(16,185,129,0.1)'  },
  CANCELLED:  { label: 'Cancelled',   color: '#ef4444', bg: 'rgba(239,68,68,0.1)'   },
}

export function OpsStatusBadge({ status }) {
  const m = META[status] || { label: status, color: '#64748b', bg: 'rgba(100,116,139,0.1)' }
  return (
    <span style={{
      display: 'inline-flex', alignItems: 'center', gap: 5,
      background: m.bg, color: m.color,
      padding: '3px 9px', borderRadius: 100,
      fontSize: 11, fontWeight: 700, fontFamily: 'JetBrains Mono, monospace',
      whiteSpace: 'nowrap',
    }}>
      <span style={{ width: 5, height: 5, borderRadius: '50%', background: m.color }} />
      {m.label}
    </span>
  )
}