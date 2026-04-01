import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'
import { AppShell } from './components/AppShell'
import { AssistantsPage } from './pages/AssistantsPage'
import { MetricsPage } from './pages/MetricsPage'

const queryClient = new QueryClient({
  defaultOptions: {
    queries: { staleTime: 60_000, retry: 1 },
  },
})

function routerBasename(): string | undefined {
  const b = import.meta.env.BASE_URL
  if (b === '/' || b === '') return undefined
  return b.endsWith('/') ? b.slice(0, -1) : b || undefined
}

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter basename={routerBasename()}>
        <Routes>
          <Route path="/" element={<AppShell />}>
            <Route index element={<Navigate to="/metrics/total-payout" replace />} />
            <Route path="metrics/:slug" element={<MetricsPage />} />
            <Route path="assistants/:slug" element={<AssistantsPage />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  )
}
