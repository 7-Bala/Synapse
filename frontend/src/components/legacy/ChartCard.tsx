import type { ReactNode } from 'react'
import { cn } from '@/lib/utils'

interface ChartCardProps {
  title: string
  description?: string
  action?: ReactNode
  children: ReactNode
  className?: string
  loading?: boolean
}

export function ChartCard({
  title,
  description,
  action,
  children,
  className,
  loading = false,
}: ChartCardProps) {
  return (
    <div className={cn('panel flex flex-col', className)}>
      <div className="flex items-start justify-between gap-4 px-4 pt-4 pb-2">
        <div>
          <h3 className="text-sm font-medium text-foreground">{title}</h3>
          {description && <p className="text-xs text-muted mt-0.5">{description}</p>}
        </div>
        {action}
      </div>
      <div className="flex-1 p-4 pt-2 min-h-[200px]">
        {loading ? (
          <div className="h-full bg-elevated/50 rounded animate-pulse" />
        ) : (
          children
        )}
      </div>
    </div>
  )
}
