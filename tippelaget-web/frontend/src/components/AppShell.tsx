import { useState } from 'react'
import { NavLink, Outlet } from 'react-router-dom'
import { EventsModal } from './EventsModal'
import { WorkflowBar } from './WorkflowBar'

const metricLinks = [
  { to: '/metrics/total-payout', label: 'Total payout' },
  { to: '/metrics/average-odds', label: 'Average odds' },
  { to: '/metrics/cumulative-payout', label: 'Cumulative payout' },
  { to: '/metrics/win-rate', label: 'Win rate' },
  { to: '/metrics/cumulative-baseline', label: 'Cumulative vs baseline' },
  { to: '/metrics/team-total', label: 'Team total' },
  { to: '/metrics/luckiness', label: 'Luckiness' },
  { to: '/metrics/tippekassa', label: 'Tippekassa vs baseline' },
] as const

const assistantLinks = [
  { to: '/assistants/prophet', label: 'The Prophet' },
  { to: '/assistants/king', label: "King Carl Gustaf" },
] as const

const navCls = ({ isActive }: { isActive: boolean }) =>
  `block rounded-lg px-3 py-2 text-sm transition ${
    isActive ? 'bg-white/10 text-white font-medium' : 'text-[var(--color-muted)] hover:bg-white/5 hover:text-white'
  }`

export function AppShell() {
  const [eventsOpen, setEventsOpen] = useState(false)

  return (
    <div className="flex min-h-svh">
      <aside className="hidden w-60 shrink-0 border-r border-[var(--color-border)] bg-[var(--color-surface-elevated)]/50 p-4 md:block">
        <div className="mb-6 px-2">
          <p className="text-xs font-semibold uppercase tracking-widest text-[var(--color-accent)]">Tippelaget</p>
          <p className="mt-1 text-lg font-bold text-white">Season 2</p>
        </div>
        <nav className="space-y-6">
          <div>
            <p className="mb-2 px-2 text-xs font-medium uppercase text-[var(--color-muted)]">Metrics</p>
            <div className="space-y-0.5">
              {metricLinks.map((l) => (
                <NavLink key={l.to} to={l.to} className={navCls} end>
                  {l.label}
                </NavLink>
              ))}
            </div>
          </div>
          <div>
            <p className="mb-2 px-2 text-xs font-medium uppercase text-[var(--color-muted)]">Assistants</p>
            <div className="space-y-0.5">
              {assistantLinks.map((l) => (
                <NavLink key={l.to} to={l.to} className={navCls}>
                  {l.label}
                </NavLink>
              ))}
            </div>
          </div>
        </nav>
      </aside>

      <div className="flex min-w-0 flex-1 flex-col">
        <header className="border-b border-[var(--color-border)] bg-[var(--color-surface)]/95 px-4 py-4 backdrop-blur md:px-8">
          <div className="mx-auto flex max-w-5xl flex-col gap-4">
            <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
              <div>
                <h1 className="text-2xl font-bold tracking-tight text-white md:text-3xl">Tippelaget</h1>
                <p className="text-sm text-[var(--color-muted)]">Betting analytics · modern web UI</p>
              </div>
            </div>
            <WorkflowBar onShowEvents={() => setEventsOpen(true)} />
          </div>
        </header>

        <main className="mx-auto w-full max-w-5xl flex-1 px-4 py-8 md:px-8">
          <div className="md:hidden mb-8 overflow-x-auto pb-2">
            <div className="flex min-w-max gap-1 rounded-xl border border-[var(--color-border)] bg-[var(--color-surface-elevated)] p-1">
              {[...metricLinks, ...assistantLinks].map((l) => (
                <NavLink
                  key={l.to}
                  to={l.to}
                  className={({ isActive }) =>
                    `whitespace-nowrap rounded-lg px-3 py-2 text-xs font-medium ${
                      isActive ? 'bg-[var(--color-accent)] text-[#042f2e]' : 'text-[var(--color-muted)]'
                    }`
                  }
                >
                  {l.label}
                </NavLink>
              ))}
            </div>
          </div>
          <Outlet />
        </main>
      </div>

      <EventsModal open={eventsOpen} onClose={() => setEventsOpen(false)} />
    </div>
  )
}
