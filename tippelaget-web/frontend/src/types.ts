export interface TotalPayoutRow {
  player: string
  payout: number
}

export interface AverageOddsRow {
  player: string
  odds: number
}

export interface CumulativePlayerSeries {
  player: string
  points: { gameweek_num: number; cumulative_payout: number }[]
  last_label: string
}

export interface WinRateRow {
  player: string
  win_rate: number
}

export interface CumulativeVsBaseline {
  players: CumulativePlayerSeries[]
  baseline: { gameweek_num: number; per_player_stake: number }[]
  baseline_last_label: string
}

export interface TeamTotal {
  series: {
    gameweek_num: number
    cumulative_payout: number
    cumulative_stake: number
  }[]
  diff: number | null
  last_gameweek: number
}

export interface LuckinessPayload {
  bars: { player: string; luck_ratio: number }[]
  luckiest: { player: string; luck_ratio: number } | null
  unluckiest: { player: string; luck_ratio: number } | null
}

export interface TippekassaPayload {
  series: {
    gameweek_num: number
    cum_payout_plus_innskudd: number
    cum_stake_plus_innskudd: number
  }[]
}

export interface DashboardData {
  total_payout: TotalPayoutRow[]
  average_odds: AverageOddsRow[]
  cumulative_payout: CumulativePlayerSeries[]
  win_rate: WinRateRow[]
  cumulative_vs_baseline: CumulativeVsBaseline
  team_total: TeamTotal
  luckiness: LuckinessPayload
  tippekassa_vs_baseline: TippekassaPayload
}
