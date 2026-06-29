import { cn } from '@/lib/utils'

interface LoadingSkeletonProps {
  className?: string
  lines?: number
}

export function LoadingSkeleton({ className, lines = 1 }: LoadingSkeletonProps) {
  return (
    <div className={cn('space-y-2', className)}>
      {Array.from({ length: lines }).map((_, i) => (
        <div
          key={i}
          className="h-4 bg-elevated rounded animate-pulse"
          style={{ width: `${Math.max(40, 100 - i * 15)}%` }}
        />
      ))}
    </div>
  )
}

export function PageSkeleton() {
  return (
    <div className="space-y-6 animate-pulse">
      <div className="h-8 w-48 bg-elevated rounded" />
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {Array.from({ length: 4 }).map((_, i) => (
          <div key={i} className="panel h-28 bg-elevated/50" />
        ))}
      </div>
      <div className="panel h-64 bg-elevated/50" />
    </div>
  )
}

export function TableSkeleton({ rows = 5 }: { rows?: number }) {
  return (
    <div className="space-y-2">
      <div className="h-8 bg-elevated rounded animate-pulse" />
      {Array.from({ length: rows }).map((_, i) => (
        <div key={i} className="h-10 bg-elevated/60 rounded animate-pulse" />
      ))}
    </div>
  )
}
