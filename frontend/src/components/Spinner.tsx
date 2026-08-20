interface SpinnerProps {
  label?: string
  className?: string
}

export function Spinner({ label, className = '' }: SpinnerProps) {
  return (
    <span className={`inline-flex items-center gap-2 ${className}`} role="status">
      <span
        aria-hidden
        className="h-4 w-4 animate-spin rounded-full border-2 border-slate-300 border-t-slate-700"
      />
      {label && <span className="text-sm text-slate-600">{label}</span>}
      <span className="sr-only">{label ?? 'Cargando'}</span>
    </span>
  )
}
