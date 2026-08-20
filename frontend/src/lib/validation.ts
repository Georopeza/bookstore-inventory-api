import type { BookInput } from '../types/book'

export type ValidationErrors = Partial<Record<keyof BookInput, string>>

const ISBN_SEPARATORS = /[\s-]/g

/**
 * Réplica en cliente de las reglas que aplica el servidor. No lo sustituye:
 * evita un viaje de ida y vuelta para errores evidentes, mientras que la
 * autoridad sobre la validez sigue estando en la API.
 */
export function validateBook(input: BookInput): ValidationErrors {
  const errors: ValidationErrors = {}

  if (!input.title.trim()) errors.title = 'El título es obligatorio.'
  if (!input.author.trim()) errors.author = 'El autor es obligatorio.'
  if (!input.category.trim()) errors.category = 'La categoría es obligatoria.'

  const isbn = input.isbn.replace(ISBN_SEPARATORS, '')
  if (!isbn) {
    errors.isbn = 'El ISBN es obligatorio.'
  } else if (!/^\d{9}[\dX]$|^\d{13}$/i.test(isbn)) {
    errors.isbn = 'El ISBN debe tener 10 o 13 dígitos.'
  }

  if (!Number.isFinite(input.cost_usd) || input.cost_usd <= 0) {
    errors.cost_usd = 'El costo debe ser mayor que 0.'
  }

  if (!Number.isInteger(input.stock_quantity) || input.stock_quantity < 0) {
    errors.stock_quantity = 'El stock no puede ser negativo.'
  }

  if (!/^[A-Za-z]{2}$/.test(input.supplier_country.trim())) {
    errors.supplier_country = 'Usa un código de país de dos letras (ES, AR, MX).'
  }

  return errors
}
