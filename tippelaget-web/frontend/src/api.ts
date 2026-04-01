import type { DashboardData } from './types'
import { apiUrl } from './lib/apiBase'

async function json<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(apiUrl(path), {
    ...init,
    headers: { 'Content-Type': 'application/json', ...init?.headers },
  })
  if (!res.ok) {
    const text = await res.text()
    throw new Error(text || res.statusText)
  }
  return res.json() as Promise<T>
}

export function fetchDashboard(): Promise<DashboardData> {
  return json<DashboardData>('/api/dashboard')
}

export function fetchEventsToday(): Promise<{ rows: Record<string, unknown>[] }> {
  return json('/api/events/today')
}

export function fetchLastWorkflowRun(): Promise<{
  created_time_ms: number | null
  display_utc_plus_2: string | null
}> {
  return json('/api/workflow/last-run')
}

export function runWorkflow(): Promise<{ execution_id: string | number }> {
  return json('/api/workflow/run', { method: 'POST' })
}

/** Cognite workflow execution id is often a UUID string; may be numeric in older APIs. */
export function workflowStatus(executionId: string | number): Promise<{ status: string }> {
  const id = encodeURIComponent(String(executionId))
  return json(`/api/workflow/status/${id}`)
}

export function askProphet(question: string): Promise<{ answer: string }> {
  return json('/api/assistants/prophet', {
    method: 'POST',
    body: JSON.stringify({ question }),
  })
}

export function askKing(question: string, player: string): Promise<{ answer: string }> {
  return json('/api/assistants/king', {
    method: 'POST',
    body: JSON.stringify({ question, player }),
  })
}
