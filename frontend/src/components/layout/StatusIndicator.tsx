import { useQuery } from '@tanstack/react-query'
import { healthApi } from '@/lib/api/services'
import { StatusBadge } from '@/components/legacy/StatusBadge'
import { cn } from '@/lib/utils'

interface StatusIndicatorProps {
  compact?: boolean
  className?: string
}

export function StatusIndicator({ compact = false, className }: StatusIndicatorProps) {
  const { data, isLoading, isError } = useQuery({
    queryKey: ['health', 'system'],
    queryFn: healthApi.getSystem,
    refetchInterval: 30_000,
    retry: 1,
    staleTime: 15_000,
  })

  const status = isError ? 'UNKNOWN' : isLoading ? 'UNKNOWN' : data?.overall_status ?? 'UNKNOWN'

  if (compact) {
    return (
      <span
        className={cn(
          'size-2 rounded-full',
          status === 'HEALTHY' && 'bg-success',
          status === 'DEGRADED' && 'bg-warning',
          status === 'FAILED' && 'bg-danger',
          status === 'UNKNOWN' && 'bg-muted animate-pulse',
          className,
        )}
        title={`System ${status}`}
      />
    )
  }

  return (
    <StatusBadge
      status={status}
      pulse={isLoading}
      className={className}
    />
  )
}
