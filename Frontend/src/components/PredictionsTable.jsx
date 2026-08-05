import { ArrowDown, ArrowUp, ArrowUpDown } from 'lucide-react'
import RiskBadge from '@/components/RiskBadge'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import { formatPercentage } from '@/utils/formatPercentage'

function SortableHead({ label, sortKey, sortState, onSortChange, className }) {
  if (!onSortChange) {
    return <TableHead className={className}>{label}</TableHead>
  }

  const isActive = sortState?.key === sortKey
  const Icon = isActive ? (sortState.direction === 'asc' ? ArrowUp : ArrowDown) : ArrowUpDown

  return (
    <TableHead className={className}>
      <button
        type="button"
        onClick={() => onSortChange(sortKey)}
        className="inline-flex items-center gap-1 text-foreground hover:text-foreground"
      >
        {label}
        <Icon className={`size-3.5 ${isActive ? 'text-foreground' : 'text-muted-foreground/50'}`} />
      </button>
    </TableHead>
  )
}

/**
 * Shared between the Dashboard's condensed "Recent Predictions" card and
 * the full Prediction History page -- one table implementation, two
 * levels of detail via `compact`, rather than two parallel components.
 * Sorting is opt-in: pass `sortState`/`onSortChange` (History) to get
 * clickable, sort-indicating headers, or omit them (Dashboard) for plain
 * headers.
 */
export default function PredictionsTable({ predictions, compact = false, sortState, onSortChange }) {
  return (
    <Table>
      <TableHeader>
        <TableRow>
          <SortableHead label="Timestamp" sortKey="created_at" sortState={sortState} onSortChange={onSortChange} />
          <TableHead>Outcome</TableHead>
          <SortableHead
            label="Probability"
            sortKey="admission_probability"
            sortState={sortState}
            onSortChange={onSortChange}
          />
          <SortableHead label="Risk" sortKey="risk_category" sortState={sortState} onSortChange={onSortChange} />
          {!compact && <TableHead>Model</TableHead>}
          {!compact && <TableHead className="text-right">Processing time</TableHead>}
        </TableRow>
      </TableHeader>
      <TableBody>
        {predictions.map((prediction) => (
          <TableRow key={prediction.id}>
            <TableCell className="text-muted-foreground">
              {new Date(prediction.created_at).toLocaleString()}
            </TableCell>
            <TableCell>{prediction.predicted_admission ? 'Admission' : 'No admission'}</TableCell>
            <TableCell className="tabular-nums">{formatPercentage(prediction.admission_probability)}</TableCell>
            <TableCell>
              <RiskBadge riskCategory={prediction.risk_category} />
            </TableCell>
            {!compact && (
              <TableCell className="text-muted-foreground">
                {prediction.model_name} v{prediction.model_version}
              </TableCell>
            )}
            {!compact && (
              <TableCell className="text-right tabular-nums text-muted-foreground">
                {prediction.processing_time_ms.toFixed(0)} ms
              </TableCell>
            )}
          </TableRow>
        ))}
      </TableBody>
    </Table>
  )
}
