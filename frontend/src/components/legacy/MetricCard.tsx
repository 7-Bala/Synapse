import { motion } from 'framer-motion'
import type { LucideIcon } from 'lucide-react'
import { TrendingDown, TrendingUp } from 'lucide-react'
import { cn } from '@/lib/utils'

interface MetricCardProps {
  title: string
  value: string | number
  subtitle?: string
  icon?: LucideIcon
  trend?: {
    value: number
    label?: string
  }
  loading?: boolean
  className?: string
}

export function MetricCard({
  title,
  value,
  subtitle,
  icon: Icon,
  trend,
  loading = false,
  className,
}: MetricCardProps) {
  const trendPositive = trend && trend.value >= 0

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, ease: 'easeOut' }}
      className={cn('panel p-4 flex flex-col gap-3', className)}
    >
      <div className="flex items-start justify-between gap-2">
        <span className="label">{title}</span>
        {Icon && (
          <div className="flex items-center justify-center size-8 rounded-md bg-accent-muted text-accent">
            <Icon className="size-4" />
          </div>
        )}
      </div>

      {loading ? (
        <div className="space-y-2">
          <div className="h-8 w-24 bg-elevated rounded animate-pulse" />
          <div className="h-3 w-16 bg-elevated rounded animate-pulse" />
        </div>
      ) : (
        <>
          <div className="flex items-end gap-2">
            <span className="text-2xl font-semibold tracking-tight text-foreground font-mono">
              {value}
            </span>
            {trend && (
              <span
                className={cn(
                  'flex items-center gap-0.5 text-2xs font-medium mb-1',
                  trendPositive ? 'text-success' : 'text-danger',
                )}
              >
                {trendPositive ? (
                  <TrendingUp className="size-3" />
                ) : (
                  <TrendingDown className="size-3" />
                )}
                {Math.abs(trend.value)}%
              </span>
            )}
          </div>
          {(subtitle || trend?.label) && (
            <p className="text-xs text-muted">{subtitle ?? trend?.label}</p>
          )}
        </>
      )}
    </motion.div>
  )
}
