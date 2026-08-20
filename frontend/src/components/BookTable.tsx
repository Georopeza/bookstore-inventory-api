import type { Book } from '../types/book'

interface BookTableProps {
  books: Book[]
  threshold: number
  /** Las acciones son opcionales: sin ellas la tabla es de solo lectura. */
  actions?: {
    onEdit: (book: Book) => void
    onDelete: (book: Book) => void
    onCalculatePrice: (book: Book) => void
  }
}

const currency = (value: number | null, code = '') =>
  value === null ? '—' : `${value.toFixed(2)}${code && ` ${code}`}`

export function BookTable({ books, threshold, actions }: BookTableProps) {
  const action =
    'rounded-md px-2.5 py-1 text-sm font-medium transition hover:bg-slate-100'

  return (
    <div className="overflow-x-auto">
      <table className="w-full min-w-4xl border-collapse text-left text-sm">
        <thead className="bg-slate-50 text-xs uppercase tracking-wide text-slate-500">
          <tr>
            <th scope="col" className="px-4 py-3 font-semibold">Título</th>
            <th scope="col" className="px-4 py-3 font-semibold">Autor</th>
            <th scope="col" className="px-4 py-3 font-semibold">ISBN</th>
            <th scope="col" className="px-4 py-3 font-semibold">Categoría</th>
            <th scope="col" className="px-4 py-3 text-right font-semibold">Costo USD</th>
            <th scope="col" className="px-4 py-3 text-right font-semibold">P. venta</th>
            <th scope="col" className="px-4 py-3 text-right font-semibold">Stock</th>
            {actions && (
              <th scope="col" className="px-4 py-3 font-semibold">Acciones</th>
            )}
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-100">
          {books.map((book) => (
            <tr key={book.id} className="hover:bg-slate-50/70">
              <td className="px-4 py-3 font-medium text-slate-900">{book.title}</td>
              <td className="px-4 py-3 text-slate-600">{book.author}</td>
              <td className="px-4 py-3 font-mono text-xs text-slate-500">{book.isbn}</td>
              <td className="px-4 py-3 text-slate-600">{book.category}</td>
              <td className="px-4 py-3 text-right tabular-nums">{currency(book.cost_usd)}</td>
              <td className="px-4 py-3 text-right tabular-nums text-slate-600">
                {currency(book.selling_price_local)}
              </td>
              <td className="px-4 py-3 text-right">
                <span
                  className={
                    book.stock_quantity <= threshold
                      ? 'rounded-full bg-amber-100 px-2 py-0.5 font-semibold tabular-nums text-amber-800'
                      : 'tabular-nums text-slate-700'
                  }
                >
                  {book.stock_quantity}
                </span>
              </td>
              {actions && (
                <td className="px-4 py-3">
                  <div className="flex items-center gap-1">
                    <button
                      type="button"
                      className={`${action} text-emerald-700`}
                      onClick={() => actions.onCalculatePrice(book)}
                    >
                      Calcular precio
                    </button>
                    <button
                      type="button"
                      className={`${action} text-slate-700`}
                      onClick={() => actions.onEdit(book)}
                    >
                      Editar
                    </button>
                    <button
                      type="button"
                      className={`${action} text-red-700`}
                      onClick={() => actions.onDelete(book)}
                    >
                      Eliminar
                    </button>
                  </div>
                </td>
              )}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
