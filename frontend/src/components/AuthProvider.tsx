import { createContext, ReactNode, useContext } from 'react'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import { api, ApiError } from '../api'
import type { User } from '../types'

type AuthContextValue = { user: User | null; loading: boolean; refresh: () => Promise<void>; logout: () => Promise<void> }
const AuthContext = createContext<AuthContextValue | null>(null)

export function AuthProvider({ children }: { children: ReactNode }) {
  const queryClient = useQueryClient()
  const query = useQuery({ queryKey: ['me'], queryFn: () => api<User>('/auth/me'), retry: false })
  const user = query.error instanceof ApiError && query.error.status === 401 ? null : query.data ?? null
  async function refresh() { await queryClient.invalidateQueries({ queryKey: ['me'] }) }
  async function logout() {
    await api('/auth/logout', { method: 'POST' })
    queryClient.setQueryData(['me'], null)
    queryClient.removeQueries({ predicate: (item) => item.queryKey[0] !== 'me' })
  }
  return <AuthContext.Provider value={{ user, loading: query.isLoading, refresh, logout }}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const value = useContext(AuthContext)
  if (!value) throw new Error('useAuth must be used inside AuthProvider')
  return value
}
