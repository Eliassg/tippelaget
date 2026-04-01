import { useId, useState } from 'react'
import { playerImageUrl } from '../lib/apiBase'

const LINE_DOT_PX = 33

type DotProps = {
  cx?: number
  cy?: number
  stroke?: string
}

/** SVG `<image>` + circular clip, no ring; optional bitmap scale for tighter source crops (e.g. mads/tobias). */
export function PlayerLineDot({ cx, cy, player, stroke }: DotProps & { player: string }) {
  const clipId = useId().replace(/:/g, '')
  const [failed, setFailed] = useState(false)
  if (cx == null || cy == null) return null

  const s = LINE_DOT_PX
  const r = s / 2 - 1
  const color = stroke ?? '#94a3b8'

  const name = player.trim().toLowerCase()
  let bitmapZoom = 1
  if (name === 'tobias' || name === 'mads') bitmapZoom = 0.88
  const imgSize = s * bitmapZoom

  if (failed) {
    return <circle cx={cx} cy={cy} r={r} fill={color} />
  }

  const src = playerImageUrl(player)

  return (
    <g>
      <defs>
        <clipPath id={clipId}>
          <circle cx={cx} cy={cy} r={r} />
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
    </g>
  )
}
