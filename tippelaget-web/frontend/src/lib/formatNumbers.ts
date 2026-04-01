/** NOK and other monetary amounts: whole numbers only. */
export function formatNok(n: number): string {
  return Math.round(Number(n)).toLocaleString('nb-NO', { maximumFractionDigits: 0 })
}

/** Odds, ratios, etc.: at most two decimal places (trims trailing zeros via locale). */
export function formatOther(n: number): string {
  return Number(n).toLocaleString('nb-NO', { minimumFractionDigits: 0, maximumFractionDigits: 2 })
}

/** Percent values on a 0–100 scale (e.g. win rate, luck as %). */
export function formatPercent100(n: number): string {
  return `${formatOther(n)} %`
}
