import type { HealthStatus, DeploymentDecision, StageStatus, PipelineStatus } from '@/types/models'
import { cn } from '@/lib/utils'

type StatusVariant = HealthStatus | DeploymentDecision | StageStatus | PipelineStatus | string

const statusStyles: Record<string, string> = {
  HEALTHY: 'bg-success-muted text-success border-success/20',
  READY: 'bg-success-muted text-success border-success/20',
  PASSED: 'bg-success-muted text-success border-success/20',
  completed: 'bg-success-muted text-success border-success/20',
  valid: 'bg-success-muted text-success border-success/20',

  DEGRADED: 'bg-warning-muted text-warning border-warning/20',
  READY_WITH_WARNINGS: 'bg-warning-muted text-warning border-warning/20',
  WARNING: 'bg-warning-muted text-warning border-warning/20',
  running: 'bg-warning-muted text-warning border-warning/20',
  pending: 'bg-warning-muted text-warning border-warning/20',

  FAILED: 'bg-danger-muted text-danger border-danger/20',
  NOT_READY: 'bg-danger-muted text-danger border-danger/20',
  failed: 'bg-danger-muted text-danger border-danger/20',
  invalid: 'bg-danger-muted text-danger border-danger/20',
  cancelled: 'bg-danger-muted text-danger border-danger/20',

  UNKNOWN: 'bg-elevated text-muted border-border',
  SKIPPED: 'bg-elevated text-muted border-border',
  idle: 'bg-elevated text-muted border-border',
}

interface StatusBadgeProps {
  status: StatusVariant
  label?: string
  size?: 'sm' | 'md'
  pulse?: boolean
  className?: string
}

export function StatusBadge({
  status,
  label,
  size = 'sm',
  pulse = false,
  className,
}: StatusBadgeProps) {
  const displayLabel = label ?? String(status).replace(/_/g, ' ')

  return (
    <span
      className={cn(
        'inline-flex items-center gap-1.5 font-medium border rounded-full',
        size === 'sm' ? 'px-2 py-0.5 text-2xs' : 'px-2.5 py-1 text-xs',
        statusStyles[String(status)] ?? statusStyles.UNKNOWN,
        pulse && 'animate-pulse-subtle',
        className,
      )}
    >
      <span className="size-1.5 rounded-full bg-current opacity-80" />
      {displayLabel}
    </span>
  )
}
