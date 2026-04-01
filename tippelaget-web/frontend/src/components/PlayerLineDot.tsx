import { useState } from 'react'
import { playerImageUrl } from '../lib/apiBase'

const LINE_DOT_PX = 22

type DotProps = {
  cx?: number
  cy?: number
  stroke?: string
}

/** Line chart point: circular image from `/api/player-image/{player}`, or a dot if it fails to load. */
export function PlayerLineDot({ cx, cy, player, stroke }: DotProps & { player: string }) {
  const [failed, setFailed] = useState(false)
  if (cx == null || cy == null) return null

  const s = LINE_DOT_PX
  const half = s / 2
  const color = stroke ?? '#94a3b8'

  if (failed) {
    return <circle cx={cx} cy={cy} r={Math.max(4, s / 6)} fill={color} stroke="#0c0d12" strokeWidth={1} />
  }

  const src = playerImageUrl(player)

  return (
    <foreignObject x={cx - half} y={cy - half} width={s} height={s} style={{ overflow: 'visible' }}>
      <div
        className="pointer-events-none"
        style={{
          width: s,
          height: s,
          borderRadius: '50%',
          overflow: 'hidden',
          boxSizing: 'border-box',
          border: `2px solid ${color}`,
          background: '#13141c',
        }}
      >
        <img
          src={src}
          alt=""
          style={{
            width: '100%',
            height: '100%',
            objectFit: 'cover',
            display: 'block',
            margin: 0,
          }}
          onError={() => setFailed(true)}
        />
      </div>
    </foreignObject>
  )
}
