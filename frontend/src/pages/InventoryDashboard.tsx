import { useEffect, useState } from 'react'

import { DEFAULT_PAGE_SIZE } from '../api/books'
import { BookTable } from '../components/BookTable'
import { FiltersPanel } from '../components/FiltersPanel'
import { Pagination } from '../components/Pagination'
import { Spinner } from '../components/Spinner'
import { useBooks } from '../hooks/useBooks'
import type { BookFilters } from '../types/book'

const INITIAL_FILTERS: BookFilters = { category: '', lowStock: false, threshold: 10 }

export function InventoryDashboard() {
  const [filters, setFilters] = useState<BookFilters>(INITIAL_FILTERS)
  const [page, setPage] = useState(1)

  const { books, total, loading, error } = useBooks(filters, page)

  // Un filtro nuevo reinicia la paginación: la página 3 del listado anterior
  // rara vez existe en el resultado filtrado.
  useEffect(() => setPage(1), [filters])

  return (
    <div className="mx-auto max-w-7xl px-6 py-10">
      <header className="mb-6">
        <h1 className="text-2xl font-semibold text-slate-900">Inventario de libros</h1>
        <p className="mt-1 text-sm text-slate-600">
          Catálogo, búsqueda por categoría y control de stock bajo.
        </p>
      </header>

      <FiltersPanel filters={filters} onChange={setFilters} />

      <section className="mt-6 overflow-hidden rounded-lg border border-slate-200 bg-white">
        {loading && (
          <div className="flex justify-center px-4 py-16">
            <Spinner label="Cargando inventario…" />
          </div>
        )}

        {!loading && error && (
          <div className="px-4 py-16 text-center">
            <p className="font-medium text-red-700">{error.userMessage}</p>
          </div>
        )}

        {!loading && !error && books.length === 0 && (
          <p className="px-4 py-16 text-center text-slate-500">
            No hay libros que coincidan con los filtros aplicados.
          </p>
        )}

        {!loading && !error && books.length > 0 && (
          <>
            <BookTable books={books} threshold={filters.threshold} />
            <Pagination
              page={page}
              pageSize={DEFAULT_PAGE_SIZE}
              total={total}
              onChange={setPage}
            />
          </>
        )}
      </section>
    </div>
  )
}
