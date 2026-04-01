/** Relative `/api/...` when unset (Vite dev proxy); full origin when `VITE_API_BASE_URL` is set (e.g. Cloud Run URL for GitHub Pages). */
export function apiUrl(path: string): string {
  const raw = import.meta.env.VITE_API_BASE_URL?.trim() ?? ''
  const base = raw.replace(/\/$/, '')
  const p = path.startsWith('/') ? path : `/${path}`
  if (!base) return p
  return `${base}${p}`
}
