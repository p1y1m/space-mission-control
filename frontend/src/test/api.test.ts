import { afterEach, expect, test, vi } from 'vitest'
import { api } from '../api'

afterEach(() => vi.unstubAllGlobals())

test('reuses an exposed cross-origin CSRF token for protected writes', async () => {
  const fetchMock = vi.fn()
    .mockResolvedValueOnce(new Response(JSON.stringify({ id: 1 }), {
      status: 201,
      headers: { 'Content-Type': 'application/json', 'X-CSRF-Token': 'server-token' },
    }))
    .mockResolvedValueOnce(new Response(JSON.stringify({ id: 2 }), {
      status: 201,
      headers: { 'Content-Type': 'application/json' },
    }))
  vi.stubGlobal('fetch', fetchMock)

  await api('/auth/register', { method: 'POST', body: '{}' })
  await api('/watchlist', { method: 'POST', body: '{}' })

  const secondRequest = fetchMock.mock.calls[1][1] as RequestInit
  expect(new Headers(secondRequest.headers).get('X-CSRF-Token')).toBe('server-token')
})
