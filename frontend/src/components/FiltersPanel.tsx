import { useEffect, useState } from 'react'

import type { BookFilters } from '../types/book'

interface FiltersPanelProps {
  filters: BookFilters
  onChange: (filters: BookFilters) => void
}

export function FiltersPanel({ filters, onChange }: FiltersPanelProps) {
  const [category, setCategory] = useState(filters.category)

  // La categoría se escribe letra a letra: se deja reposar la entrada para no
  // lanzar una petición por pulsación.
  useEffect(() => {
    if (category === filters.category) return
    const timer = setTimeout(() => onChange({ ...filters, category }), 300)
    return () => clearTimeout(timer)
  }, [category, filters, onChange])

  useEffect(() => setCategory(filters.category), [filters.category])

  return (
    <section
      aria-label="Filtros"
      className="flex flex-wrap items-end gap-4 rounded-lg border border-slate-200 bg-white p-4"
    >
      <div className="grow sm:grow-0">
        <label
          htmlFor="filter-category"
          className="mb-1 block text-sm font-medium text-slate-700"
        >
          Categoría
        </label>
        <input
          id="filter-category"
          type="search"
          value={category}
          placeholder="Literatura Clásica"
          onChange={(event) => setCategory(event.target.value)}
          className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm sm:w-64"
        />
      </div>

      <div>
        <label
          htmlFor="filter-threshold"
          className="mb-1 block text-sm font-medium text-slate-700"
        >
          Umbral de stock bajo
        </label>
        <input
          id="filter-threshold"
          type="number"
          min={0}
          value={filters.threshold}
          disabled={!filters.lowStock}
          onChange={(event) =>
            onChange({ ...filters, threshold: Math.max(0, Number(event.target.value)) })
          }
          className="w-32 rounded-md border border-slate-300 px-3 py-2 text-sm disabled:bg-slate-100 disabled:text-slate-400"
        />
      </div>

      <label className="flex items-center gap-2 pb-2 text-sm font-medium text-slate-700">
        <input
          type="checkbox"
          checked={filters.lowStock}
          onChange={(event) => onChange({ ...filters, lowStock: event.target.checked })}
          className="h-4 w-4 rounded border-slate-300"
        />
        Solo stock bajo
      </label>

      {(filters.category || filters.lowStock) && (
        <button
          type="button"
          onClick={() => onChange({ category: '', lowStock: false, threshold: 10 })}
          className="pb-2 text-sm font-medium text-slate-500 underline hover:text-slate-700"
        >
          Limpiar filtros
        </button>
      )}
    </section>
  )
}
