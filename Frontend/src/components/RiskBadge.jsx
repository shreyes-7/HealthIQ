import { CircleAlert, CircleCheck, TriangleAlert } from 'lucide-react'
import { Badge } from '@/components/ui/badge'

const RISK_CONFIG = {
  low: { variant: 'success', icon: CircleCheck },
  moderate: { variant: 'warning', icon: TriangleAlert },
  high: { variant: 'destructive', icon: CircleAlert },
}

export default function RiskBadge({ riskCategory }) {
  const config = RISK_CONFIG[riskCategory] ?? { variant: 'secondary', icon: CircleAlert }
  const Icon = config.icon

  return (
    <Badge variant={config.variant} className="h-6 gap-1.5 rounded-full px-2.5 capitalize">
      <Icon data-icon="inline-start" className="size-3.5" />
      {riskCategory} risk
    </Badge>
  )
}
