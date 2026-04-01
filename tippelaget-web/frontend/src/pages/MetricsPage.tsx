import { useQuery } from '@tanstack/react-query'
import { Navigate, useParams } from 'react-router-dom'
import {
  Bar,
  BarChart,
  CartesianGrid,
  LabelList,
  Legend,
  Line,
  LineChart,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import { fetchDashboard } from '../api'
import { ChartFrame } from '../components/ChartFrame'
import { formatNok, formatOther, formatPercent100 } from '../lib/formatNumbers'
import { mergeBaseline, pivotPlayerLines, playerColorMap } from '../lib/chartUtils'

const tipStyle = {
  backgroundColor: '#1a1b24',
  border: '1px solid #252836',
  borderRadius: 8,
  color: '#e8eaef',
}

function num(v: string | number | undefined, fallback = 0): number {
  if (v === undefined) return fallback
  return typeof v === 'number' ? v : Number(v) || fallback
}

function barLabelNok(props: { x?: string | number; y?: string | number; width?: string | number; value?: unknown }) {
  const x = num(props.x)
  const y = num(props.y)
  const width = num(props.width)
  return (
    <text x={x + width / 2} y={y} dy={-4} fill="#e8eaef" fontSize={11} textAnchor="middle">
      {formatNok(Number(props.value))}
    </text>
  )
}

function barLabelOther(props: { x?: string | number; y?: string | number; width?: string | number; value?: unknown }) {
  const x = num(props.x)
  const y = num(props.y)
  const width = num(props.width)
  return (
    <text x={x + width / 2} y={y} dy={-4} fill="#e8eaef" fontSize={11} textAnchor="middle">
      {formatOther(Number(props.value))}
    </text>
  )
}

function barLabelPercent(props: { x?: string | number; y?: string | number; width?: string | number; value?: unknown }) {
  const x = num(props.x)
  const y = num(props.y)
  const width = num(props.width)
  return (
    <text x={x + width / 2} y={y} dy={-4} fill="#e8eaef" fontSize={11} textAnchor="middle">
      {formatPercent100(Number(props.value))}
    </text>
  )
}

const tooltipNok = (value: unknown) => [formatNok(Number(value)), 'NOK'] as [string, string]
const lineTooltipNok = (value: unknown, name: unknown) =>
  [formatNok(Number(value)), String(name)] as [string, string]

export function MetricsPage() {
  const { slug } = useParams()
  const { data, isLoading, isError, error } = useQuery({
    queryKey: ['dashboard'],
    queryFn: fetchDashboard,
  })

  if (!slug) return <Navigate to="/metrics/total-payout" replace />

  if (isLoading) {
    return (
      <ChartFrame title="Loading">
        <p className="text-sm text-[var(--color-muted)]">Fetching data from Cognite…</p>
      </ChartFrame>
    )
  }

  if (isError) {
    return (
      <ChartFrame title="Error">
        <p className="text-sm text-red-400">{(error as Error).message}</p>
      </ChartFrame>
    )
  }

  if (!data) return null

  const empty = !data.total_payout?.length

  if (empty) {
    return (
      <ChartFrame title="No data">
        <p className="text-sm text-[var(--color-muted)]">
          No bet rows returned. Check Cognite connection and populate the data model.
        </p>
      </ChartFrame>
    )
  }

  switch (slug) {
    case 'total-payout':
      return <TotalPayout data={data.total_payout} />
    case 'average-odds':
      return <AverageOdds data={data.average_odds} />
    case 'cumulative-payout':
      return <CumulativePayout data={data.cumulative_payout} />
    case 'win-rate':
      return <WinRate data={data.win_rate} />
    case 'cumulative-baseline':
      return <CumulativeBaseline data={data.cumulative_vs_baseline} />
    case 'team-total':
      return <TeamTotal data={data.team_total} />
    case 'luckiness':
      return <Luckiness data={data.luckiness} />
    case 'tippekassa':
      return <Tippekassa data={data.tippekassa_vs_baseline} />
    default:
      return <Navigate to="/metrics/total-payout" replace />
  }
}

function TotalPayout({ data }: { data: { player: string; payout: number }[] }) {
  return (
    <ChartFrame title="Total payout per player" subtitle="Sum of payouts (NOK)">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data} margin={{ top: 8, right: 8, left: 0, bottom: 8 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#252836" />
          <XAxis dataKey="player" tick={{ fill: '#8b92a8', fontSize: 12 }} />
          <YAxis tick={{ fill: '#8b92a8', fontSize: 12 }} tickFormatter={(v) => formatNok(Number(v))} />
          <Tooltip contentStyle={tipStyle} formatter={tooltipNok} />
          <Bar dataKey="payout" fill="#5eead4" radius={[6, 6, 0, 0]} name="NOK">
            <LabelList dataKey="payout" position="top" content={barLabelNok} />
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </ChartFrame>
  )
}

function AverageOdds({ data }: { data: { player: string; odds: number }[] }) {
  return (
    <ChartFrame title="Average odds per player" subtitle="Mean odds across bets">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data} margin={{ top: 8, right: 8, left: 0, bottom: 8 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#252836" />
          <XAxis dataKey="player" tick={{ fill: '#8b92a8', fontSize: 12 }} />
          <YAxis tick={{ fill: '#8b92a8', fontSize: 12 }} tickFormatter={(v) => formatOther(Number(v))} />
          <Tooltip contentStyle={tipStyle} formatter={(v) => [formatOther(Number(v)), 'Odds'] as [string, string]} />
          <Bar dataKey="odds" fill="#a78bfa" radius={[6, 6, 0, 0]}>
            <LabelList dataKey="odds" position="top" content={barLabelOther} />
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </ChartFrame>
  )
}

function CumulativePayout({ data }: { data: import('../types').CumulativePlayerSeries[] }) {
  const merged = pivotPlayerLines(data)
  const players = data.map((d) => d.player)
  const colors = playerColorMap(players)
  return (
    <ChartFrame title="Cumulative payout per player" subtitle="Running total by gameweek (NOK)">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={merged} margin={{ top: 8, right: 24, left: 0, bottom: 8 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#252836" />
          <XAxis dataKey="gameweek_num" tick={{ fill: '#8b92a8', fontSize: 12 }} label={{ value: 'Gameweek', fill: '#8b92a8', position: 'bottom', offset: 0 }} />
          <YAxis tick={{ fill: '#8b92a8', fontSize: 12 }} tickFormatter={(v) => formatNok(Number(v))} />
          <Tooltip contentStyle={tipStyle} formatter={lineTooltipNok} />
          <Legend wrapperStyle={{ color: '#8b92a8' }} />
          {players.map((p) => (
            <Line key={p} type="monotone" dataKey={p} stroke={colors.get(p)} strokeWidth={2} dot={{ r: 4 }} />
          ))}
        </LineChart>
      </ResponsiveContainer>
    </ChartFrame>
  )
}

function WinRate({ data }: { data: { player: string; win_rate: number }[] }) {
  const chartData = data.map((r) => ({ ...r, win_pct: r.win_rate * 100 }))
  return (
    <ChartFrame title="Win rate per player" subtitle="Share of gameweeks where total payout ≥ total stake">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={chartData} margin={{ top: 8, right: 8, left: 0, bottom: 8 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#252836" />
          <XAxis dataKey="player" tick={{ fill: '#8b92a8', fontSize: 12 }} />
          <YAxis
            tick={{ fill: '#8b92a8', fontSize: 12 }}
            domain={[0, 100]}
            tickFormatter={(v) => formatPercent100(Number(v))}
          />
          <Tooltip
            contentStyle={tipStyle}
            formatter={(value) => [formatPercent100(Number(value)), 'Win rate'] as [string, string]}
          />
          <Bar dataKey="win_pct" fill="#fb923c" radius={[6, 6, 0, 0]} name="Win rate">
            <LabelList dataKey="win_pct" position="top" content={barLabelPercent} />
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </ChartFrame>
  )
}

function CumulativeBaseline({ data }: { data: import('../types').CumulativeVsBaseline }) {
  const pivoted = pivotPlayerLines(data.players)
  const merged = mergeBaseline(pivoted, data.baseline)
  const players = data.players.map((d) => d.player)
  const colors = playerColorMap(players)
  return (
    <ChartFrame
      title="Cumulative payout vs baseline"
      subtitle="Baseline: equal share of total weekly stake (NOK)"
    >
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={merged} margin={{ top: 8, right: 24, left: 0, bottom: 8 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#252836" />
          <XAxis dataKey="gameweek_num" tick={{ fill: '#8b92a8', fontSize: 12 }} />
          <YAxis tick={{ fill: '#8b92a8', fontSize: 12 }} tickFormatter={(v) => formatNok(Number(v))} />
          <Tooltip contentStyle={tipStyle} formatter={lineTooltipNok} />
          <Legend wrapperStyle={{ color: '#8b92a8' }} />
          {players.map((p) => (
            <Line key={p} type="monotone" dataKey={p} stroke={colors.get(p)} strokeWidth={2} dot={{ r: 3 }} />
          ))}
          <Line
            type="monotone"
            dataKey="Baseline (stake/share)"
            stroke="#f8fafc"
            strokeWidth={2}
            dot={false}
            strokeDasharray="6 4"
          />
        </LineChart>
      </ResponsiveContainer>
    </ChartFrame>
  )
}

function TeamTotal({ data }: { data: import('../types').TeamTotal }) {
  if (!data.series.length) {
    return (
      <ChartFrame title="Team cumulative payout vs stake">
        <p className="text-sm text-[var(--color-muted)]">No data.</p>
      </ChartFrame>
    )
  }
  return (
    <ChartFrame
      title="Team cumulative payout vs stake"
      subtitle={data.diff != null ? `Latest gap (payout − stake): ${formatNok(data.diff)} NOK` : undefined}
    >
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={data.series} margin={{ top: 8, right: 24, left: 0, bottom: 8 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#252836" />
          <XAxis dataKey="gameweek_num" tick={{ fill: '#8b92a8', fontSize: 12 }} />
          <YAxis tick={{ fill: '#8b92a8', fontSize: 12 }} tickFormatter={(v) => formatNok(Number(v))} />
          <Tooltip contentStyle={tipStyle} formatter={lineTooltipNok} />
          <Legend wrapperStyle={{ color: '#8b92a8' }} />
          <Line type="monotone" dataKey="cumulative_payout" name="Team payout" stroke="#4ade80" strokeWidth={2.5} dot />
          <Line
            type="monotone"
            dataKey="cumulative_stake"
            name="Baseline (stake)"
            stroke="#fb923c"
            strokeWidth={2.5}
            strokeDasharray="6 4"
            dot={false}
          />
        </LineChart>
      </ResponsiveContainer>
    </ChartFrame>
  )
}

function Luckiness({ data }: { data: import('../types').LuckinessPayload }) {
  const chartData = data.bars.map((b) => ({ ...b, luck_pct: b.luck_ratio * 100 }))
  return (
    <div className="space-y-6">
      <ChartFrame title="Luckiness / ball knowledge?" subtitle="Actual payout ÷ expected value from odds">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={chartData} margin={{ top: 8, right: 8, left: 0, bottom: 8 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#252836" />
            <XAxis dataKey="player" tick={{ fill: '#8b92a8', fontSize: 12 }} />
            <YAxis tick={{ fill: '#8b92a8', fontSize: 12 }} tickFormatter={(v) => formatPercent100(Number(v))} />
            <Tooltip
              contentStyle={tipStyle}
              formatter={(value) => [formatPercent100(Number(value)), 'Luck ratio'] as [string, string]}
            />
            <ReferenceLine y={100} stroke="#94a3b8" strokeDasharray="4 4" />
            <Bar dataKey="luck_pct" fill="#5eead4" radius={[6, 6, 0, 0]}>
              <LabelList dataKey="luck_pct" position="top" content={barLabelPercent} />
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </ChartFrame>
      <section className="rounded-2xl border border-[var(--color-border)] bg-[var(--color-surface-elevated)] p-6 text-sm leading-relaxed text-[var(--color-muted)]">
        <h3 className="mb-2 text-base font-semibold text-white">How luck is calculated</h3>
        <p>
          For each player, we compare <strong className="text-white">actual payout</strong> to the{' '}
          <strong className="text-white">expected payout</strong> implied by odds (stake / odds). A ratio above 100%
          means results beat the odds; below 100% means underperformance versus EV.
        </p>
        {data.luckiest && data.unluckiest ? (
          <ul className="mt-4 list-inside list-disc space-y-1 text-white/90">
            <li>
              Luckiest: <strong>{data.luckiest.player}</strong> ({formatOther(data.luckiest.luck_ratio)})
            </li>
            <li>
              Unluckiest: <strong>{data.unluckiest.player}</strong> ({formatOther(data.unluckiest.luck_ratio)})
            </li>
          </ul>
        ) : null}
      </section>
    </div>
  )
}

function Tippekassa({ data }: { data: import('../types').TippekassaPayload }) {
  if (!data.series.length) {
    return (
      <ChartFrame title="Tippekassa vs baseline">
        <p className="text-sm text-[var(--color-muted)]">No data.</p>
      </ChartFrame>
    )
  }
  return (
    <ChartFrame title="Tippekassa vs baseline" subtitle="Cumulative payouts + innskudd vs stake + innskudd">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={data.series} margin={{ top: 8, right: 24, left: 0, bottom: 8 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#252836" />
          <XAxis dataKey="gameweek_num" tick={{ fill: '#8b92a8', fontSize: 12 }} />
          <YAxis tick={{ fill: '#8b92a8', fontSize: 12 }} tickFormatter={(v) => formatNok(Number(v))} />
          <Tooltip contentStyle={tipStyle} formatter={lineTooltipNok} />
          <Legend wrapperStyle={{ color: '#8b92a8' }} />
          <Line type="monotone" dataKey="cum_payout_plus_innskudd" name="Winnings + innskudd" stroke="#4ade80" strokeWidth={2.5} dot />
          <Line
            type="monotone"
            dataKey="cum_stake_plus_innskudd"
            name="Stake + innskudd (baseline)"
            stroke="#e2e8f0"
            strokeWidth={2}
            strokeDasharray="6 4"
            dot={false}
          />
        </LineChart>
      </ResponsiveContainer>
    </ChartFrame>
  )
}
