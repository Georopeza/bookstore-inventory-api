import { useCallback, useEffect, useState } from 'react'

import { booksApi } from '../api/books'
import { ApiError } from '../api/http'
import type { Book, PriceCalculation } from '../types/book'
import { Modal } from './Modal'
import { Spinner } from './Spinner'

interface PriceBreakdownModalProps {
  book: Book
  onClose: () => void
  onCalculated: () => void
}

function Row({
  label,
  value,
  emphasis = false,
}: {
  label: string
  value: string
  emphasis?: boolean
}) {
  return (
    <div
      className={`flex items-baseline justify-between gap-4 py-2 ${
        emphasis ? 'border-t border-slate-200 pt-3' : ''
      }`}
    >
      <dt className={emphasis ? 'font-semibold text-slate-900' : 'text-slate-600'}>
        {label}
      </dt>
      <dd
        className={`tabular-nums ${
          emphasis ? 'text-lg font-semibold text-slate-900' : 'text-slate-800'
        }`}
      >
        {value}
      </dd>
    </div>
  )
}

export function PriceBreakdownModal({
  book,
  onClose,
  onCalculated,
}: PriceBreakdownModalProps) {
  const [result, setResult] = useState<PriceCalculation | null>(null)
  const [error, setError] = useState<ApiError | null>(null)
  const [loading, setLoading] = useState(false)

  const calculate = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const calculation = await booksApi.calculatePrice(book.id)
      setResult(calculation)
      onCalculated()
    } catch (cause) {
      setError(cause instanceof ApiError ? cause : new ApiError(0, 'Unexpected error'))
    } finally {
      setLoading(false)
    }
  }, [book.id, onCalculated])

  // El cálculo se dispara al abrir: la acción explícita es el botón de la
  // tabla, y este diálogo es su resultado.
  useEffect(() => {
    void calculate()
  }, [calculate])

  return (
    <Modal title="Precio de venta sugerido" onClose={onClose}>
      <div className="px-5 py-5">
        <p className="mb-4 text-sm text-slate-500">{book.title}</p>

        {loading && (
          <div className="flex justify-center py-10">
            <Spinner label="Consultando la tasa de cambio…" />
          </div>
        )}

        {!loading && error && (
          <div className="rounded-md border border-red-200 bg-red-50 px-4 py-3">
            <p className="text-sm font-medium text-red-800">{error.userMessage}</p>
            <button
              type="button"
              onClick={() => void calculate()}
              className="mt-2 text-sm font-medium text-red-700 underline"
            >
              Reintentar
            </button>
          </div>
        )}

        {!loading && !error && result && (
          <>
            {result.rate_source === 'fallback' && (
              <p className="mb-4 rounded-md border border-amber-200 bg-amber-50 px-3 py-2 text-xs text-amber-800">
                El proveedor de tasas no respondió. El cálculo usa la tasa de
                respaldo configurada, no una cotización en tiempo real.
              </p>
            )}

            <dl className="text-sm">
              <Row label="Costo original" value={`${result.cost_usd.toFixed(2)} USD`} />
              <Row
                label={`Tasa de cambio (USD → ${result.currency})`}
                value={result.exchange_rate.toString()}
              />
              <Row
                label="Costo en moneda local"
                value={`${result.cost_local.toFixed(2)} ${result.currency}`}
              />
              <Row label="Margen de ganancia" value={`${result.margin_percentage}%`} />
              <Row
                label="Precio de venta"
                value={`${result.selling_price_local.toFixed(2)} ${result.currency}`}
                emphasis
              />
            </dl>

            <p className="mt-4 text-xs text-slate-400">
              Calculado el{' '}
              {new Date(result.calculation_timestamp).toLocaleString('es-ES')}
            </p>
          </>
        )}
      </div>

      <footer className="flex justify-end border-t border-slate-200 px-5 py-4">
        <button
          type="button"
          onClick={onClose}
          className="rounded-md border border-slate-300 px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50"
        >
          Cerrar
        </button>
      </footer>
    </Modal>
  )
}
