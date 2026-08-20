export interface Book {
  id: number
  title: string
  author: string
  isbn: string
  cost_usd: number
  selling_price_local: number | null
  stock_quantity: number
  category: string
  supplier_country: string
  created_at: string
  updated_at: string
}

/** Campos que el cliente envía; el resto los gobierna el servidor. */
export type BookInput = Omit<
  Book,
  'id' | 'selling_price_local' | 'created_at' | 'updated_at'
>

export interface Page<T> {
  count: number
  next: string | null
  previous: string | null
  results: T[]
}

export type RateSource = 'live' | 'fallback'

export interface PriceCalculation {
  book_id: number
  cost_usd: number
  exchange_rate: number
  cost_local: number
  margin_percentage: number
  selling_price_local: number
  currency: string
  rate_source: RateSource
  calculation_timestamp: string
}

export interface BookFilters {
  category: string
  lowStock: boolean
  threshold: number
}
