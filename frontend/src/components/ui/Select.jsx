// frontend/src/components/ui/Select.jsx

export default function Select({ label, error, children, className = '', ...props }) {
  return (
    <div className="flex flex-col gap-1.5">
      {label && (
        <label style={{ fontSize: 13, fontWeight: 500, color: 'var(--muted)' }}>
          {label}
        </label>
      )}
      <select
        style={{
          width: '100%',
          padding: '12px 16px',
          borderRadius: 'var(--radius)',
          border: `1.5px solid ${error ? '#e53e3e' : 'var(--cream-dark)'}`,
          background: 'var(--white)',
          color: 'var(--charcoal)',
          fontSize: 15,
          outline: 'none',
          cursor: 'pointer',
          appearance: 'none',
          backgroundImage: `url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='16' height='16' viewBox='0 0 24 24' fill='none' stroke='%236b7a6e' stroke-width='2'%3E%3Cpath d='m6 9 6 6 6-6'/%3E%3C/svg%3E")`,
          backgroundRepeat: 'no-repeat',
          backgroundPosition: 'right 14px center',
          paddingRight: 40,
        }}
        {...props}
      >
        {children}
      </select>
      {error && <span style={{ fontSize: 12, color: '#e53e3e' }}>{error}</span>}
    </div>
  )
}