import { useQuery } from '@tanstack/react-query'
import { fetchEventsToday } from '../api'

export function EventsModal({ open, onClose }: { open: boolean; onClose: () => void }) {
  const { data, isLoading, isError, error } = useQuery({
    queryKey: ['events-today'],
    queryFn: fetchEventsToday,
    enabled: open,
  })

  if (!open) return null

  const rows = data?.rows ?? []

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4"
      role="dialog"
      aria-modal="true"
      aria-labelledby="events-title"
    >
      <button
        type="button"
        className="absolute inset-0 bg-black/70 backdrop-blur-sm"
        aria-label="Close"
        onClick={onClose}
      />
      <div className="relative z-10 max-h-[85vh] w-full max-w-4xl overflow-hidden rounded-2xl border border-[var(--color-border)] bg-[var(--color-surface-elevated)] shadow-2xl">
        <div className="flex items-center justify-between border-b border-[var(--color-border)] px-5 py-4">
          <h2 id="events-title" className="text-lg font-semibold text-white">
            Today&apos;s events
          </h2>
          <button
            type="button"
            onClick={onClose}
            className="rounded-lg px-3 py-1.5 text-sm text-[var(--color-muted)] hover:bg-white/5 hover:text-white"
          >
            Close
          </button>
        </div>
        <div className="max-h-[calc(85vh-4rem)] overflow-auto p-5">
          {isLoading ? (
            <p className="text-sm text-[var(--color-muted)]">Loading…</p>
          ) : isError ? (
            <p className="text-sm text-red-400">{(error as Error).message}</p>
          ) : rows.length === 0 ? (
            <p className="text-sm text-[var(--color-muted)]">No events found for today.</p>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-sm">
                <thead>
                  <tr className="border-b border-[var(--color-border)] text-[var(--color-muted)]">
                    {Object.keys(rows[0]).map((k) => (
                      <th key={k} className="px-2 py-2 font-medium">
                        {k}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {rows.map((row, i) => (
                    <tr key={i} className="border-b border-[var(--color-border)]/60">
                      {Object.values(row).map((v, j) => (
                        <td key={j} className="px-2 py-2 text-white/90">
                          {v === null || v === undefined ? '—' : String(v)}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
