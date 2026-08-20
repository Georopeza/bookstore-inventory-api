interface PaginationProps {
  page: number
  pageSize: number
  total: number
  onChange: (page: number) => void
}

export function Pagination({ page, pageSize, total, onChange }: PaginationProps) {
  const lastPage = Math.max(1, Math.ceil(total / pageSize))
  const first = total === 0 ? 0 : (page - 1) * pageSize + 1
  const last = Math.min(page * pageSize, total)

  const button =
    'rounded-md border border-slate-300 px-3 py-1.5 text-sm font-medium text-slate-700 ' +
    'enabled:hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-40'

  return (
    <div className="flex items-center justify-between border-t border-slate-200 px-4 py-3">
      <p className="text-sm text-slate-600">
        {total === 0 ? 'Sin resultados' : `${first}–${last} de ${total}`}
      </p>
      <div className="flex items-center gap-2">
        <button
          type="button"
          className={button}
          onClick={() => onChange(page - 1)}
          disabled={page <= 1}
        >
          Anterior
        </button>
        <span className="text-sm text-slate-600">
          Página {page} de {lastPage}
        </span>
        <button
          type="button"
          className={button}
          onClick={() => onChange(page + 1)}
          disabled={page >= lastPage}
        >
          Siguiente
        </button>
      </div>
    </div>
  )
}
