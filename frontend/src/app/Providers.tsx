import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import type { ReactNode } from 'react'
import { useEffect } from 'react'
import { socketClient } from '../lib/api/socket'

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 30_000,
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
})

export function Providers({ children }: { children: ReactNode }) {
  useEffect(() => {
    socketClient.connect()
    return () => socketClient.disconnect()
  }, [])

  return (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  )
}
