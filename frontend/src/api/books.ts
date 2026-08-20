import type { Book, BookInput, Page, PriceCalculation } from '../types/book'
import { request } from './http'

export interface ListParams {
  page?: number
  pageSize?: number
  category?: string
  lowStock?: boolean
  threshold?: number
}

export const DEFAULT_PAGE_SIZE = 10

// La paginación de la API es opt-in: sin ?page devuelve una lista plana. El
// cliente la pide siempre para trabajar con una única forma de respuesta.
function buildQuery(params: ListParams): string {
  return new URLSearchParams({
    page: String(params.page ?? 1),
    page_size: String(params.pageSize ?? DEFAULT_PAGE_SIZE),
  }).toString()
}

/**
 * Resuelve la ruta de listado según el filtro activo. La API expone la
 * búsqueda por categoría y el stock bajo como recursos propios, de modo que
 * el filtro decide el endpoint, no un parámetro más.
 */
function resolvePath(params: ListParams): string {
  const query = buildQuery(params)

  if (params.category?.trim()) {
    return `/books/search?category=${encodeURIComponent(params.category.trim())}&${query}`
  }
  if (params.lowStock) {
    return `/books/low-stock?threshold=${params.threshold ?? 10}&${query}`
  }
  return `/books?${query}`
}

export const booksApi = {
  list: (params: ListParams = {}) => request<Page<Book>>(resolvePath(params)),

  retrieve: (id: number) => request<Book>(`/books/${id}`),

  create: (input: BookInput) =>
    request<Book>('/books', { method: 'POST', body: JSON.stringify(input) }),

  update: (id: number, input: BookInput) =>
    request<Book>(`/books/${id}`, { method: 'PUT', body: JSON.stringify(input) }),

  remove: (id: number) => request<void>(`/books/${id}`, { method: 'DELETE' }),

  calculatePrice: (id: number, currency?: string) =>
    request<PriceCalculation>(`/books/${id}/calculate-price`, {
      method: 'POST',
      body: JSON.stringify(currency ? { currency } : {}),
    }),
}
