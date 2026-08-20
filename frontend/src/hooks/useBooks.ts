import { useCallback, useEffect, useState } from 'react'

import { booksApi, DEFAULT_PAGE_SIZE } from '../api/books'
import { ApiError } from '../api/http'
import type { Book, BookFilters } from '../types/book'

interface UseBooksResult {
  books: Book[]
  total: number
  loading: boolean
  error: ApiError | null
  reload: () => void
}

export function useBooks(
  filters: BookFilters,
  page: number,
  pageSize: number = DEFAULT_PAGE_SIZE,
): UseBooksResult {
  const [books, setBooks] = useState<Book[]>([])
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<ApiError | null>(null)
  const [reloadToken, setReloadToken] = useState(0)

  const reload = useCallback(() => setReloadToken((token) => token + 1), [])

  const { category, lowStock, threshold } = filters

  useEffect(() => {
    // Cada efecto marca su propia respuesta: si el filtro cambia mientras una
    // petición sigue en vuelo, la respuesta tardía no debe pisar a la actual.
    let current = true
    setLoading(true)
    setError(null)

    booksApi
      .list({ page, pageSize, category, lowStock, threshold })
      .then((result) => {
        if (!current) return
        setBooks(result.results)
        setTotal(result.count)
      })
      .catch((cause: unknown) => {
        if (!current) return
        setBooks([])
        setTotal(0)
        setError(
          cause instanceof ApiError ? cause : new ApiError(0, 'Unexpected error'),
        )
      })
      .finally(() => {
        if (current) setLoading(false)
      })

    return () => {
      current = false
    }
  }, [category, lowStock, threshold, page, pageSize, reloadToken])

  return { books, total, loading, error, reload }
}
