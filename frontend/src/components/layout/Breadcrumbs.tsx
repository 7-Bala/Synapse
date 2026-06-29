import { Link, useLocation } from 'react-router-dom'
import { ChevronRight } from 'lucide-react'
import { getPageTitle } from '@/config/navigation'
import { cn } from '@/lib/utils'

interface BreadcrumbsProps {
  className?: string
  items?: { label: string; path?: string }[]
}

export function Breadcrumbs({ className, items }: BreadcrumbsProps) {
  const location = useLocation()
  const pageTitle = getPageTitle(location.pathname)

  const crumbs = items ?? [
    { label: 'Synapse', path: '/' },
    ...(location.pathname !== '/' ? [{ label: pageTitle }] : []),
  ]

  return (
    <nav aria-label="Breadcrumb" className={cn('flex items-center gap-1 text-sm', className)}>
      {crumbs.map((crumb, index) => {
        const isLast = index === crumbs.length - 1
        return (
          <div key={crumb.label} className="flex items-center gap-1 min-w-0">
            {index > 0 && <ChevronRight className="size-3.5 text-muted shrink-0" />}
            {crumb.path && !isLast ? (
              <Link
                to={crumb.path}
                className="flex items-center gap-1.5 text-muted hover:text-foreground transition-colors truncate"
              >
                {index === 0 && <img src="/logo.png" alt="Synapse Logo" className="size-3.5 object-contain shrink-0" />}
                <span className="truncate">{crumb.label}</span>
              </Link>
            ) : (
              <span
                className={cn(
                  'truncate',
                  isLast ? 'text-foreground font-medium' : 'text-muted',
                )}
              >
                {crumb.label}
              </span>
            )}
          </div>
        )
      })}
    </nav>
  )
}
