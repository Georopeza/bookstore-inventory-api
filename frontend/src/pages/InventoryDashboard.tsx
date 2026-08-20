import { useCallback, useEffect, useState } from 'react'

import { booksApi, DEFAULT_PAGE_SIZE } from '../api/books'
import { ApiError } from '../api/http'
import { BookForm } from '../components/BookForm'
import { BookTable } from '../components/BookTable'
import { ConfirmDialog } from '../components/ConfirmDialog'
import { FiltersPanel } from '../components/FiltersPanel'
import { Modal } from '../components/Modal'
import { Pagination } from '../components/Pagination'
import { PriceBreakdownModal } from '../components/PriceBreakdownModal'
import { Spinner } from '../components/Spinner'
import { useToast } from '../components/ToastProvider'
import { useBooks } from '../hooks/useBooks'
import type { Book, BookFilters, BookInput } from '../types/book'

const INITIAL_FILTERS: BookFilters = { category: '', lowStock: false, threshold: 10 }

type Dialog =
  | { kind: 'create' }
  | { kind: 'edit'; book: Book }
  | { kind: 'delete'; book: Book }
  | { kind: 'price'; book: Book }
  | null

export function InventoryDashboard() {
  const [filters, setFilters] = useState<BookFilters>(INITIAL_FILTERS)
  const [page, setPage] = useState(1)
  const [dialog, setDialog] = useState<Dialog>(null)

  const { books, total, loading, error, reload } = useBooks(filters, page)
  const { notify } = useToast()

  // Un filtro nuevo reinicia la paginación: la página 3 del listado anterior
  // rara vez existe en el resultado filtrado.
  useEffect(() => setPage(1), [filters])

  const closeDialog = useCallback(() => setDialog(null), [])

  const save = async (input: BookInput, book?: Book) => {
    try {
      if (book) {
        await booksApi.update(book.id, input)
        notify('success', `«${input.title}» se actualizó correctamente.`)
      } else {
        await booksApi.create(input)
        notify('success', `«${input.title}» se añadió al inventario.`)
      }
      closeDialog()
      reload()
    } catch (cause) {
      // El aviso resume qué pasó; el formulario pinta el detalle por campo a
      // partir del mismo error, por eso se vuelve a lanzar hacia él.
      const failure = cause instanceof ApiError ? cause : new ApiError(0, 'Error')
      notify('error', failure.userMessage)
      throw failure
    }
  }

  const remove = async (book: Book) => {
    try {
      await booksApi.remove(book.id)
      notify('success', `«${book.title}» se eliminó del inventario.`)
      closeDialog()
      // Al borrar el último elemento de una página, retroceder evita quedarse
      // mirando una página vacía.
      setPage((current) => (books.length === 1 && current > 1 ? current - 1 : current))
      reload()
    } catch (cause) {
      const failure = cause instanceof ApiError ? cause : new ApiError(0, 'Error')
      notify('error', failure.userMessage)
    }
  }

  const onPriceCalculated = useCallback(() => {
    notify('success', 'Precio de venta calculado y guardado.')
    reload()
  }, [notify, reload])

  return (
    <div className="mx-auto max-w-7xl px-6 py-10">
      <header className="mb-6 flex flex-wrap items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold text-slate-900">Inventario de libros</h1>
          <p className="mt-1 text-sm text-slate-600">
            Catálogo, búsqueda por categoría y control de stock bajo.
          </p>
        </div>
        <button
          type="button"
          onClick={() => setDialog({ kind: 'create' })}
          className="rounded-md bg-slate-900 px-4 py-2 text-sm font-medium text-white hover:bg-slate-800"
        >
          Nuevo libro
        </button>
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
            <button
              type="button"
              onClick={reload}
              className="mt-3 text-sm font-medium text-slate-700 underline"
            >
              Reintentar
            </button>
          </div>
        )}

        {!loading && !error && books.length === 0 && (
          <p className="px-4 py-16 text-center text-slate-500">
            No hay libros que coincidan con los filtros aplicados.
          </p>
        )}

        {!loading && !error && books.length > 0 && (
          <>
            <BookTable
              books={books}
              threshold={filters.threshold}
              actions={{
                onEdit: (book) => setDialog({ kind: 'edit', book }),
                onDelete: (book) => setDialog({ kind: 'delete', book }),
                onCalculatePrice: (book) => setDialog({ kind: 'price', book }),
              }}
            />
            <Pagination
              page={page}
              pageSize={DEFAULT_PAGE_SIZE}
              total={total}
              onChange={setPage}
            />
          </>
        )}
      </section>

      {dialog?.kind === 'create' && (
        <Modal title="Nuevo libro" onClose={closeDialog}>
          <BookForm onSubmit={(input) => save(input)} onCancel={closeDialog} />
        </Modal>
      )}

      {dialog?.kind === 'edit' && (
        <Modal title="Editar libro" onClose={closeDialog}>
          <BookForm
            book={dialog.book}
            onSubmit={(input) => save(input, dialog.book)}
            onCancel={closeDialog}
          />
        </Modal>
      )}

      {dialog?.kind === 'delete' && (
        <ConfirmDialog
          title="Eliminar libro"
          message={`«${dialog.book.title}» se eliminará del inventario de forma permanente. Esta acción no se puede deshacer.`}
          confirmLabel="Eliminar"
          onConfirm={() => remove(dialog.book)}
          onCancel={closeDialog}
        />
      )}

      {dialog?.kind === 'price' && (
        <PriceBreakdownModal
          book={dialog.book}
          onClose={closeDialog}
          onCalculated={onPriceCalculated}
        />
      )}
    </div>
  )
}
