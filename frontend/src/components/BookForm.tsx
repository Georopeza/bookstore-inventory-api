import { useState, type FormEvent } from 'react'

import { ApiError, type FieldErrors } from '../api/http'
import { translateApiMessage } from '../lib/messages'
import { validateBook, type ValidationErrors } from '../lib/validation'
import type { Book, BookInput } from '../types/book'
import { Spinner } from './Spinner'

interface BookFormProps {
  book?: Book
  onSubmit: (input: BookInput) => Promise<void>
  onCancel: () => void
}

const EMPTY: BookInput = {
  title: '',
  author: '',
  isbn: '',
  cost_usd: 0,
  stock_quantity: 0,
  category: '',
  supplier_country: '',
}

function toInput(book?: Book): BookInput {
  if (!book) return EMPTY
  return {
    title: book.title,
    author: book.author,
    isbn: book.isbn,
    cost_usd: book.cost_usd,
    stock_quantity: book.stock_quantity,
    category: book.category,
    supplier_country: book.supplier_country,
  }
}

/** Aplana los errores por campo del servidor al formato del formulario. */
function fromApi(fieldErrors: FieldErrors): ValidationErrors {
  return Object.fromEntries(
    Object.entries(fieldErrors).map(([field, message]) => [
      field,
      translateApiMessage(Array.isArray(message) ? message.join(' ') : message),
    ]),
  ) as ValidationErrors
}

export function BookForm({ book, onSubmit, onCancel }: BookFormProps) {
  const [values, setValues] = useState<BookInput>(() => toInput(book))
  const [errors, setErrors] = useState<ValidationErrors>({})
  const [submitting, setSubmitting] = useState(false)

  const update = <K extends keyof BookInput>(field: K, value: BookInput[K]) => {
    setValues((current) => ({ ...current, [field]: value }))
    setErrors((current) => ({ ...current, [field]: undefined }))
  }

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault()

    const found = validateBook(values)
    if (Object.keys(found).length > 0) {
      setErrors(found)
      return
    }

    setSubmitting(true)
    try {
      await onSubmit({ ...values, supplier_country: values.supplier_country.toUpperCase() })
    } catch (cause) {
      // El servidor es la autoridad: si rechaza el envío, sus mensajes por
      // campo sustituyen a los del cliente. El aviso global ya lo emite quien
      // invoca, así que aquí el error se consume y el diálogo queda abierto.
      if (cause instanceof ApiError && Object.keys(cause.fieldErrors).length > 0) {
        setErrors(fromApi(cause.fieldErrors))
      }
    } finally {
      setSubmitting(false)
    }
  }

  const field = 'w-full rounded-md border px-3 py-2 text-sm'
  const border = (name: keyof BookInput) =>
    errors[name] ? 'border-red-400 bg-red-50' : 'border-slate-300'

  const Error = ({ name }: { name: keyof BookInput }) =>
    errors[name] ? <p className="mt-1 text-xs text-red-600">{errors[name]}</p> : null

  return (
    <form onSubmit={handleSubmit} noValidate>
      <div className="grid gap-4 px-5 py-5 sm:grid-cols-2">
        <div className="sm:col-span-2">
          <label htmlFor="title" className="mb-1 block text-sm font-medium text-slate-700">
            Título
          </label>
          <input
            id="title"
            value={values.title}
            onChange={(e) => update('title', e.target.value)}
            className={`${field} ${border('title')}`}
          />
          <Error name="title" />
        </div>

        <div>
          <label htmlFor="author" className="mb-1 block text-sm font-medium text-slate-700">
            Autor
          </label>
          <input
            id="author"
            value={values.author}
            onChange={(e) => update('author', e.target.value)}
            className={`${field} ${border('author')}`}
          />
          <Error name="author" />
        </div>

        <div>
          <label htmlFor="isbn" className="mb-1 block text-sm font-medium text-slate-700">
            ISBN
          </label>
          <input
            id="isbn"
            value={values.isbn}
            placeholder="978-84-376-0494-7"
            onChange={(e) => update('isbn', e.target.value)}
            className={`${field} font-mono ${border('isbn')}`}
          />
          <Error name="isbn" />
        </div>

        <div>
          <label htmlFor="category" className="mb-1 block text-sm font-medium text-slate-700">
            Categoría
          </label>
          <input
            id="category"
            value={values.category}
            onChange={(e) => update('category', e.target.value)}
            className={`${field} ${border('category')}`}
          />
          <Error name="category" />
        </div>

        <div>
          <label
            htmlFor="supplier_country"
            className="mb-1 block text-sm font-medium text-slate-700"
          >
            País del proveedor
          </label>
          <input
            id="supplier_country"
            value={values.supplier_country}
            placeholder="ES"
            maxLength={2}
            onChange={(e) => update('supplier_country', e.target.value.toUpperCase())}
            className={`${field} uppercase ${border('supplier_country')}`}
          />
          <Error name="supplier_country" />
        </div>

        <div>
          <label htmlFor="cost_usd" className="mb-1 block text-sm font-medium text-slate-700">
            Costo USD
          </label>
          <input
            id="cost_usd"
            type="number"
            step="0.01"
            min="0.01"
            value={values.cost_usd || ''}
            onChange={(e) => update('cost_usd', Number(e.target.value))}
            className={`${field} ${border('cost_usd')}`}
          />
          <Error name="cost_usd" />
        </div>

        <div>
          <label
            htmlFor="stock_quantity"
            className="mb-1 block text-sm font-medium text-slate-700"
          >
            Stock
          </label>
          <input
            id="stock_quantity"
            type="number"
            min="0"
            step="1"
            value={values.stock_quantity}
            onChange={(e) => update('stock_quantity', Number(e.target.value))}
            className={`${field} ${border('stock_quantity')}`}
          />
          <Error name="stock_quantity" />
        </div>
      </div>

      <footer className="flex justify-end gap-3 border-t border-slate-200 px-5 py-4">
        <button
          type="button"
          onClick={onCancel}
          className="rounded-md border border-slate-300 px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50"
        >
          Cancelar
        </button>
        <button
          type="submit"
          disabled={submitting}
          className="inline-flex items-center gap-2 rounded-md bg-slate-900 px-4 py-2 text-sm font-medium text-white hover:bg-slate-800 disabled:opacity-60"
        >
          {submitting && <Spinner />}
          {book ? 'Guardar cambios' : 'Crear libro'}
        </button>
      </footer>
    </form>
  )
}
