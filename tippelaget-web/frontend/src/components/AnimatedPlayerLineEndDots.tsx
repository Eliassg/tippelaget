import { useEffect, useMemo, useState } from 'react'
import { DefaultZIndexes, useXAxisScale, useYAxisScale, ZIndexLayer } from 'recharts'
import { PlayerLineDot } from './PlayerLineDot'

/** Matches Recharts `animationEasing="ease-out"` (cubic-bezier 0.42, 0, 0.58, 1). */
function easeOutLikeRecharts(linearT: number): number {
  const t = Math.min(1, Math.max(0, linearT))
  const x1 = 0.42
  const y1 = 0
  const x2 = 0.58
  const y2 = 1
  let u = t
  for (let i = 0; i < 10; i++) {
    const cx = 3 * x1
    const bx = 3 * (x2 - x1) - cx
    const ax = 1 - cx - bx
    const x = ((ax * u + bx) * u + cx) * u
    const dx = (3 * ax * u + 2 * bx) * u + cx
    if (Math.abs(dx) < 1e-6) break
    u -= (x - t) / dx
    u = Math.min(1, Math.max(0, u))
  }
  const cy = 3 * y1
  const by = 3 * (y2 - y1) - cy
  const ay = 1 - cy - by
  return ((ay * u + by) * u + cy) * u
}

type Row = Record<string, string | number | undefined>

function buildPolyline(
  rows: Row[],
  player: string,
  xDataKey: string,
  xScale: (v: unknown) => number | undefined,
  yScale: (v: unknown) => number | undefined,
): { x: number; y: number }[] {
  const out: { x: number; y: number }[] = []
  for (const row of rows) {
    const yv = row[player]
    if (yv === undefined || yv === null || (typeof yv === 'number' && Number.isNaN(yv))) continue
    const xv = row[xDataKey]
    if (xv === undefined || xv === null) continue
    const x = xScale(xv)
    const y = yScale(Number(yv))
    if (x == null || y == null) continue
    out.push({ x, y })
  }
  return out
}

function polylineLength(points: { x: number; y: number }[]): number {
  let sum = 0
  for (let i = 1; i < points.length; i++) {
    const a = points[i - 1]
    const b = points[i]
    sum += Math.hypot(b.x - a.x, b.y - a.y)
  }
  return sum
}

function pointAtDistance(
  points: { x: number; y: number }[],
  dist: number,
): { x: number; y: number } {
  if (points.length === 0) return { x: 0, y: 0 }
  if (points.length === 1) return points[0]
  let remaining = dist
  for (let i = 0; i < points.length - 1; i++) {
    const a = points[i]
    const b = points[i + 1]
    const len = Math.hypot(b.x - a.x, b.y - a.y)
    if (remaining <= len || len === 0) {
      const u = len === 0 ? 0 : remaining / len
      return { x: a.x + u * (b.x - a.x), y: a.y + u * (b.y - a.y) }
    }
    remaining -= len
  }
  return points[points.length - 1]
}

type Props = {
  data: Row[]
  players: string[]
  playerColors: Map<string, string>
  xDataKey: string
  animationDuration?: number
  animationEasing?: string
}

/**
 * Renders one player avatar at the end of each series, animated along the same pixel polyline
 * the Line uses (via axis scales). Matches Recharts line timing/easing when configured the same.
 */
export function AnimatedPlayerLineEndDots({
  data,
  players,
  playerColors,
  xDataKey,
  animationDuration = 1100,
  animationEasing = 'ease-out',
}: Props) {
  const xScale = useXAxisScale(0)
  const yScale = useYAxisScale(0)

  const ease = useMemo(() => {
    if (animationEasing === 'ease-out') return easeOutLikeRecharts
    if (animationEasing === 'linear') return (t: number) => t
    return easeOutLikeRecharts
  }, [animationEasing])

  const polylines = useMemo(() => {
    if (!xScale || !yScale || !data.length) return new Map<string, { x: number; y: number }[]>()
    const m = new Map<string, { x: number; y: number }[]>()
    for (const p of players) {
      m.set(p, buildPolyline(data, p, xDataKey, xScale, yScale))
    }
    return m
  }, [data, players, xDataKey, xScale, yScale])

  const animKey = useMemo(() => {
    const last = data[data.length - 1]
    if (!last) return '0'
    return `${data.length}-${players.map((p) => String(last[p] ?? '')).join(',')}`
  }, [data, players])

  const [progress, setProgress] = useState(0)

  useEffect(() => {
    setProgress(0)
    let start: number | undefined
    let frame = 0
    const tick = (now: number) => {
      if (start === undefined) start = now
      const linear = Math.min(1, (now - start) / animationDuration)
      setProgress(ease(linear))
      if (linear < 1) frame = requestAnimationFrame(tick)
    }
    frame = requestAnimationFrame(tick)
    return () => cancelAnimationFrame(frame)
  }, [animKey, animationDuration, ease])

  if (!xScale || !yScale) return null

  return (
    <ZIndexLayer zIndex={DefaultZIndexes.activeDot}>
      <g className="animated-player-line-end-dots" pointerEvents="none">
        {players.map((p) => {
          const pts = polylines.get(p) ?? []
          if (pts.length === 0) return null
          const total = polylineLength(pts)
          const dist = progress * total
          const { x, y } = pointAtDistance(pts, dist)
          const stroke = playerColors.get(p)
          return <PlayerLineDot key={p} cx={x} cy={y} player={p} stroke={stroke} />
        })}
      </g>
    </ZIndexLayer>
  )
}
