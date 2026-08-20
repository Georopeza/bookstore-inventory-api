/**
 * Traduce al español los mensajes de error que emite la API.
 *
 * El contrato de la API se mantiene en inglés, que es lo habitual en un
 * servicio REST; la traducción vive en el cliente, que es quien conoce el
 * idioma de la persona que lo usa. Un mensaje no contemplado se muestra tal
 * cual antes que ocultarse.
 */
const TRANSLATIONS: Array<[RegExp, string]> = [
  [/already exists/i, 'Ya existe un libro con este ISBN.'],
  [/ISBN must contain/i, 'El ISBN debe tener 10 o 13 dígitos.'],
  [/two-letter country code/i, 'Usa un código de país de dos letras (ES, AR, MX).'],
  [/three-letter currency code/i, 'Usa un código de moneda de tres letras (EUR, USD).'],
  [/greater than or equal to 0\.01/i, 'El costo debe ser mayor que 0.'],
  [/greater than or equal to 0/i, 'El valor no puede ser negativo.'],
  [/may not be blank/i, 'Este campo es obligatorio.'],
  [/is required/i, 'Este campo es obligatorio.'],
  [/Must be an integer/i, 'Debe ser un número entero.'],
  [/no more than (\d+) characters/i, 'El valor es demasiado largo.'],
]

export function translateApiMessage(message: string): string {
  const match = TRANSLATIONS.find(([pattern]) => pattern.test(message))
  return match ? match[1] : message
}
