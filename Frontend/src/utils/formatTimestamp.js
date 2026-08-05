/**
 * Formats a backend timestamp string or Date object into a localized date-time string.
 * Ensures ISO strings without an explicit timezone designator ('Z') are treated as UTC,
 * preventing offset drift when converting to local browser time.
 */
export function formatTimestamp(raw) {
  if (!raw) return '—'

  let isoString = String(raw)
  // SQLite / Pydantic strings like "2026-08-05T16:12:52" lack 'Z' or offset.
  if (typeof raw === 'string' && !isoString.endsWith('Z') && !isoString.includes('+') && !isoString.includes('T') === false) {
    if (!isoString.includes('+') && !isoString.endsWith('Z')) {
      isoString += 'Z'
    }
  }

  const date = new Date(isoString)
  if (Number.isNaN(date.getTime())) {
    return String(raw)
  }

  return date.toLocaleString(undefined, {
    month: 'numeric',
    day: 'numeric',
    year: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
    second: '2-digit',
    hour12: true,
  })
}
