import { Card, CardContent } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import { cn } from '@/lib/utils'

const TONE_CLASSES = {
  default: 'text-foreground',
  success: 'text-success',
  warning: 'text-warning',
  destructive: 'text-destructive',
}

const TONE_CHIP_CLASSES = {
  default: 'bg-primary/10 text-primary',
  success: 'bg-success/10 text-success',
  warning: 'bg-warning/10 text-warning',
  destructive: 'bg-destructive/10 text-destructive',
}

export default function StatTile({ label, value, icon: Icon, tone = 'default', loading = false, hint }) {
  return (
    <Card size="sm" className="transition-all duration-200 hover:-translate-y-0.5 hover:shadow-md">
      <CardContent className="flex items-start justify-between gap-3">
        <div className="min-w-0 space-y-1.5">
          <p className="text-sm text-muted-foreground">{label}</p>
          {loading ? (
            <Skeleton className="h-7 w-20" />
          ) : (
            <p className={cn('text-2xl font-semibold tracking-tight tabular-nums', TONE_CLASSES[tone])}>{value}</p>
          )}
          {hint && !loading && <p className="text-xs text-muted-foreground">{hint}</p>}
        </div>
        {Icon && (
          <div className={cn('flex size-9 shrink-0 items-center justify-center rounded-lg', TONE_CHIP_CLASSES[tone])}>
            <Icon className="size-4.5" />
          </div>
        )}
      </CardContent>
    </Card>
  )
}
