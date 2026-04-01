import type { CumulativePlayerSeries } from '../types'

/** Merge per-player series into rows keyed by gameweek for Recharts. */
export function pivotPlayerLines(players: CumulativePlayerSeries[]): Record<string, string | number>[] {
  const map = new Map<number, Record<string, string | number>>()
  for (const pl of players) {
    for (const pt of pl.points) {
      let row = map.get(pt.gameweek_num)
      if (!row) {
        row = { gameweek_num: pt.gameweek_num }
        map.set(pt.gameweek_num, row)
      }
      row[pl.player] = pt.cumulative_payout
    }
  }
  return Array.from(map.values()).sort(
    (a, b) => (a.gameweek_num as number) - (b.gameweek_num as number),
  )
}

export function mergeBaseline(
  rows: Record<string, string | number>[],
  baseline: { gameweek_num: number; per_player_stake: number }[],
): Record<string, string | number | undefined>[] {
  const bMap = new Map(baseline.map((b) => [b.gameweek_num, b.per_player_stake]))
  return rows.map((r) => ({
    ...r,
    'Baseline (stake/share)': bMap.get(r.gameweek_num as number),
  }))
}

export function playerColorMap(players: string[]): Map<string, string> {
  const palette = ['#5eead4', '#a78bfa', '#fb923c', '#f472b6', '#34d399', '#60a5fa', '#fbbf24']
  const m = new Map<string, string>()
  players.forEach((p, i) => m.set(p, palette[i % palette.length]))
  return m
}
