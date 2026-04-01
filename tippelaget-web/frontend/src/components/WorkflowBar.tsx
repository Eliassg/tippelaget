import { useQuery, useQueryClient } from '@tanstack/react-query'
import { useState } from 'react'
import { fetchLastWorkflowRun, runWorkflow, workflowStatus } from '../api'

export function WorkflowBar({ onShowEvents }: { onShowEvents: () => void }) {
  const qc = useQueryClient()
  const last = useQuery({
    queryKey: ['lastRun'],
    queryFn: fetchLastWorkflowRun,
    staleTime: 30_000,
  })
  const [busy, setBusy] = useState(false)
  const [log, setLog] = useState<string | null>(null)

  async function populate() {
    setBusy(true)
    setLog(null)
    try {
      const { execution_id } = await runWorkflow()
      setLog(`Started workflow (execution id ${execution_id}). Polling…`)
      let status = 'running'
      while (status === 'running') {
        await new Promise((r) => setTimeout(r, 3000))
        const s = await workflowStatus(execution_id)
        status = s.status
        setLog(`Workflow status: ${status}`)
      }
      await qc.invalidateQueries({ queryKey: ['dashboard'] })
      await qc.invalidateQueries({ queryKey: ['lastRun'] })
      setLog((prev) => `${prev}\nDone. Charts were refreshed.`)
    } catch (e) {
      setLog(String(e))
    } finally {
      setBusy(false)
    }
  }

  const display = last.data?.display_utc_plus_2
  const lastText =
    display != null
      ? `Last data model update (UTC+2): ${display}`
      : last.data?.created_time_ms == null
        ? 'Last data model update: no previous runs found.'
        : 'Last data model update: invalid timestamp.'

  return (
    <div className="space-y-3 rounded-xl border border-[var(--color-border)] bg-[var(--color-surface-elevated)]/80 p-4 backdrop-blur">
      <p className="text-sm text-[var(--color-muted)]">{lastText}</p>
      <div className="flex flex-wrap gap-2">
        <button
          type="button"
          disabled={busy}
          onClick={populate}
          className="rounded-xl bg-[var(--color-accent)] px-4 py-2 text-sm font-semibold text-[#042f2e] shadow-lg shadow-teal-500/20 hover:brightness-110 disabled:opacity-50"
        >
          {busy ? 'Updating…' : 'Populate data model'}
        </button>
        <button
          type="button"
          onClick={onShowEvents}
          className="rounded-xl border border-[var(--color-border)] bg-white/5 px-4 py-2 text-sm font-medium text-white hover:bg-white/10"
        >
          Show today&apos;s events
        </button>
      </div>
      {log ? (
        <pre className="max-h-28 overflow-auto whitespace-pre-wrap rounded-lg bg-black/30 p-2 text-xs text-white/80">
          {log}
        </pre>
      ) : null}
    </div>
  )
}
