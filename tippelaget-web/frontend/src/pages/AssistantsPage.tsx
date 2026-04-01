import { useMutation } from '@tanstack/react-query'
import { useState } from 'react'
import { useParams } from 'react-router-dom'
import { askKing, askProphet } from '../api'
import { ChartFrame } from '../components/ChartFrame'

const PLAYERS = ['Elias', 'Mads', 'Tobias'] as const

export function AssistantsPage() {
  const { slug } = useParams()

  if (slug === 'king') return <KingAssistant />
  return <ProphetAssistant />
}

function ProphetAssistant() {
  const [question, setQuestion] = useState('')
  const mutation = useMutation({ mutationFn: askProphet })

  return (
    <ChartFrame
      title="The Prophet"
      subtitle="Ask about the betting season — expect stats, roasts, and strong opinions."
    >
      <div className="flex h-full min-h-[200px] flex-col gap-4 text-left">
        <input
          type="text"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="e.g. Which player has the best ball knowledge?"
          className="w-full rounded-xl border border-[var(--color-border)] bg-black/20 px-4 py-3 text-sm text-white placeholder:text-[var(--color-muted)] focus:border-[var(--color-accent)] focus:outline-none focus:ring-1 focus:ring-[var(--color-accent)]"
        />
        <button
          type="button"
          disabled={!question.trim() || mutation.isPending}
          onClick={() => mutation.mutate(question.trim())}
          className="self-start rounded-xl bg-[var(--color-accent)] px-4 py-2 text-sm font-semibold text-[#042f2e] disabled:opacity-40"
        >
          {mutation.isPending ? 'Thinking…' : 'Ask'}
        </button>
        {mutation.isError ? (
          <p className="text-sm text-red-400">{(mutation.error as Error).message}</p>
        ) : null}
        {mutation.data?.answer ? (
          <div className="rounded-xl border border-[var(--color-border)] bg-black/25 p-4 text-sm leading-relaxed text-white/90">
            <strong className="text-[var(--color-accent)]">Prophet says:</strong> {mutation.data.answer}
          </div>
        ) : null}
      </div>
    </ChartFrame>
  )
}

function KingAssistant() {
  const [player, setPlayer] = useState<(typeof PLAYERS)[number]>('Elias')
  const [question, setQuestion] = useState('')
  const mutation = useMutation({ mutationFn: ({ q, p }: { q: string; p: string }) => askKing(q, p) })

  return (
    <ChartFrame
      title="King Carl Gustaf's wisdom"
      subtitle="Royal betting advice in Swedish — uses today's events and the selected player's history."
    >
      <div className="flex h-full min-h-[240px] flex-col gap-4 text-left">
        <div>
          <p className="mb-2 text-xs font-medium uppercase tracking-wider text-[var(--color-muted)]">Player</p>
          <div className="flex flex-wrap gap-2">
            {PLAYERS.map((p) => (
              <button
                key={p}
                type="button"
                onClick={() => setPlayer(p)}
                className={`rounded-lg px-3 py-1.5 text-sm font-medium transition ${
                  player === p
                    ? 'bg-[var(--color-accent)] text-[#042f2e]'
                    : 'border border-[var(--color-border)] bg-white/5 text-white hover:bg-white/10'
                }`}
              >
                {p}
              </button>
            ))}
          </div>
        </div>
        <input
          type="text"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="Ask King Carl Gustaf your question…"
          className="w-full rounded-xl border border-[var(--color-border)] bg-black/20 px-4 py-3 text-sm text-white placeholder:text-[var(--color-muted)] focus:border-[var(--color-accent)] focus:outline-none focus:ring-1 focus:ring-[var(--color-accent)]"
        />
        <button
          type="button"
          disabled={!question.trim() || mutation.isPending}
          onClick={() => mutation.mutate({ q: question.trim(), p: player })}
          className="self-start rounded-xl bg-[var(--color-accent)] px-4 py-2 text-sm font-semibold text-[#042f2e] disabled:opacity-40"
        >
          {mutation.isPending ? 'His Majesty is thinking…' : 'Ask'}
        </button>
        {mutation.isError ? (
          <p className="text-sm text-red-400">{(mutation.error as Error).message}</p>
        ) : null}
        {mutation.data?.answer ? (
          <div className="rounded-xl border border-[var(--color-border)] bg-black/25 p-4 text-sm leading-relaxed text-white/90">
            <strong className="text-[var(--color-accent)]">King Carl Gustaf proclaims:</strong> {mutation.data.answer}
          </div>
        ) : null}
      </div>
    </ChartFrame>
  )
}
