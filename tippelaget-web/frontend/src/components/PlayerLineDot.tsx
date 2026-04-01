import { useId, useState } from 'react'
import { playerImageUrl } from '../lib/apiBase'

const LINE_DOT_PX = 22

type DotProps = {
  cx?: number
  cy?: number
  stroke?: string
}

/** SVG `<image>` + circular clip: same outer diameter for everyone; per-player bitmap scale balances different crops. */
export function PlayerLineDot({ cx, cy, player, stroke }: DotProps & { player: string }) {
  const clipId = useId().replace(/:/g, '')
  const [failed, setFailed] = useState(false)
  if (cx == null || cy == null) return null

  const s = LINE_DOT_PX
  const outerR = s / 2 - 1
  const innerR = Math.max(2, outerR - 2)
  const color = stroke ?? '#94a3b8'

  const name = player.trim().toLowerCase()
  let bitmapZoom = 1
  if (name === 'elias') bitmapZoom = 1.42
  else if (name === 'tobias' || name === 'mads') bitmapZoom = 0.88
  const imgSize = s * bitmapZoom

  if (failed) {
    return (
      <circle cx={cx} cy={cy} r={outerR} fill={color} stroke="#0c0d12" strokeWidth={1} />
    )
  }

  const src = playerImageUrl(player)

  return (
    <g>
      <defs>
        <clipPath id={clipId}>
          <circle cx={cx} cy={cy} r={innerR} />
        </clipPath>
      </defs>
      <image
        href={src}
        x={cx - imgSize / 2}
        y={cy - imgSize / 2}
        width={imgSize}
        height={imgSize}
        clipPath={`url(#${clipId})`}
        preserveAspectRatio="xMidYMid slice"
        onError={() => setFailed(true)}
      />
      <circle
        cx={cx}
        cy={cy}
        r={outerR}
        fill="none"
        stroke={color}
        strokeWidth={2}
        pointerEvents="none"
      />
    </g>
  )
}
