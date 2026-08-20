const BASE_URL = (import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000').replace(
  /\/$/,
  '',
)

export type FieldErrors = Record<string, string | string[]>

interface ErrorEnvelope {
  error?: {
    code?: number
    message?: string
    details?: FieldErrors | null
  }
}

/**
 * Error de la API con el estado HTTP y, cuando la respuesta es una validación
 * fallida, los mensajes por campo para pintarlos junto a cada input.
 */
export class ApiError extends Error {
  readonly status: number
  readonly fieldErrors: FieldErrors

  constructor(status: number, message: string, fieldErrors: FieldErrors = {}) {
    super(message)
    this.name = 'ApiError'
    this.status = status
    this.fieldErrors = fieldErrors
  }

  /** Mensaje orientado a la persona que usa la aplicación. */
  get userMessage(): string {
    switch (this.status) {
      case 0:
        return 'No se pudo contactar con el servidor. Verifica que la API esté en ejecución.'
      case 400:
        return 'Revisa los datos introducidos.'
      case 404:
        return 'El recurso solicitado ya no existe.'
      case 503:
        return 'El servicio de tasas de cambio no está disponible en este momento.'
      default:
        return this.status >= 500
          ? 'El servidor encontró un error inesperado.'
          : this.message
    }
  }
}

async function parseError(response: Response): Promise<ApiError> {
  let envelope: ErrorEnvelope = {}
  try {
    envelope = (await response.json()) as ErrorEnvelope
  } catch {
    // Una respuesta de error sin cuerpo JSON deja los valores por defecto.
  }
  return new ApiError(
    response.status,
    envelope.error?.message ?? response.statusText,
    envelope.error?.details ?? {},
  )
}

export async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  let response: Response
  try {
    response = await fetch(`${BASE_URL}${path}`, {
      ...init,
      headers: { 'Content-Type': 'application/json', ...init.headers },
    })
  } catch {
    // fetch solo rechaza ante un fallo de red; el estado 0 lo distingue de
    // cualquier respuesta que sí haya llegado desde el servidor.
    throw new ApiError(0, 'Network request failed')
  }

  if (!response.ok) throw await parseError(response)
  if (response.status === 204) return undefined as T

  return (await response.json()) as T
}
