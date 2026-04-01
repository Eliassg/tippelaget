import type { ReactNode } from 'react'

export function ChartFrame({
  title,
  subtitle,
  children,
}: {
  title: string
  subtitle?: string
  children: ReactNode
}) {
  return (
    <section className="rounded-2xl border border-[var(--color-border)] bg-[var(--color-surface-elevated)] p-6 shadow-[0_20px_50px_-24px_rgba(0,0,0,0.65)]">
      <header className="mb-4">
        <h2 className="text-lg font-semibold tracking-tight text-white">{title}</h2>
        {subtitle ? <p className="mt-1 text-sm text-[var(--color-muted)]">{subtitle}</p> : null}
      </header>
      <div className="h-[min(420px,70vw)] w-full min-h-[280px]">{children}</div>
    </section>
  )
}
