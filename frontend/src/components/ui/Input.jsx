// frontend/src/components/ui/Input.jsx

export default function Input({ label, error, className = '', ...props }) {
  return (
    <div className="flex flex-col gap-1.5">
      {label && (
        <label style={{ fontSize: 13, fontWeight: 500, color: 'var(--muted)' }}>
          {label}
        </label>
      )}
      <input
        className={className}
        style={{
          width: '100%',
          padding: '12px 16px',
          borderRadius: 'var(--radius)',
          border: `1.5px solid ${error ? '#e53e3e' : 'var(--cream-dark)'}`,
          background: 'var(--white)',
          color: 'var(--charcoal)',
          fontSize: 15,
          outline: 'none',
          transition: 'border-color var(--transition)',
        }}
        onFocus={e => e.target.style.borderColor = 'var(--forest)'}
        onBlur={e => e.target.style.borderColor = error ? '#e53e3e' : 'var(--cream-dark)'}
        {...props}
      />
      {error && <span style={{ fontSize: 12, color: '#e53e3e' }}>{error}</span>}
    </div>
  )
}