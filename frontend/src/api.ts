const API = import.meta.env.VITE_API_URL || (import.meta.env.DEV ? 'http://localhost:8000/api/v1' : '/api/v1')
let csrfToken: string | undefined

function cookie(name: string) {
  return document.cookie.split('; ').find((part) => part.startsWith(`${name}=`))?.split('=').slice(1).join('=')
}

export class ApiError extends Error { constructor(public status: number, message: string) { super(message) } }

export async function api<T>(path: string, options: RequestInit = {}): Promise<T> {
  const method = options.method || 'GET'
  const headers = new Headers(options.headers)
  if (options.body) headers.set('Content-Type', 'application/json')
  if (!['GET', 'HEAD'].includes(method)) {
    // Same-origin development can read the cookie. Cross-origin GitHub Pages
    // receives the same double-submit token through an exposed CORS header.
    const csrf = cookie('smc_csrf') || csrfToken
    if (csrf) headers.set('X-CSRF-Token', decodeURIComponent(csrf))
  }
  const response = await fetch(`${API}${path}`, { ...options, headers, credentials: 'include' })
  const responseCsrf = response.headers.get('X-CSRF-Token')
  if (responseCsrf !== null) csrfToken = responseCsrf || undefined
  if (!response.ok) {
    const body = await response.json().catch(() => ({ detail: 'Request failed' }))
    const detail = Array.isArray(body.detail) ? body.detail[0]?.msg : body.detail
    throw new ApiError(response.status, detail || 'Request failed')
  }
  return response.status === 204 ? undefined as T : response.json()
}
