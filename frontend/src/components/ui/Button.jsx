// frontend/src/components/ui/Button.jsx

export default function Button({
  children, variant = 'primary', size = 'md',
  loading = false, className = '', ...props
}) {
  const base = `
    inline-flex items-center justify-center gap-2 font-medium rounded-lg
    transition-all duration-200 cursor-pointer border-0
    disabled:opacity-50 disabled:cursor-not-allowed
  `
  const variants = {
    primary: `
      bg-[var(--forest)] text-white
      hover:bg-[var(--forest-light)] active:bg-[var(--forest-dim)]
      shadow-sm hover:shadow-md
    `,
    amber: `
      bg-[var(--amber)] text-white
      hover:bg-[var(--amber-light)] active:bg-[var(--amber)]
    `,
    outline: `
      border border-[var(--forest)] text-[var(--forest)] bg-transparent
      hover:bg-[var(--forest)] hover:text-white
    `,
    ghost: `
      text-[var(--forest)] bg-transparent
      hover:bg-[var(--cream-dark)]
    `,
  }
  const sizes = {
    sm: 'px-4 py-2 text-sm',
    md: 'px-6 py-3 text-base',
    lg: 'px-8 py-4 text-lg',
  }

  return (
    <button
      className={`${base} ${variants[variant]} ${sizes[size]} ${className}`}
      disabled={loading || props.disabled}
      {...props}
    >
      {loading && (
        <span style={{
          width: 16, height: 16,
          border: '2px solid rgba(255,255,255,0.3)',
          borderTopColor: 'white',
          borderRadius: '50%',
          display: 'inline-block',
          animation: 'spin 0.7s linear infinite',
        }} />
      )}
      {children}
    </button>
  )
}