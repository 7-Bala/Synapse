import { Search, X } from 'lucide-react'
import { cn } from '@/lib/utils'

interface SearchBarProps {
  value: string
  onChange: (value: string) => void
  placeholder?: string
  className?: string
  onFocus?: () => void
  shortcut?: string
}

export function SearchBar({
  value,
  onChange,
  placeholder = 'Search...',
  className,
  onFocus,
  shortcut,
}: SearchBarProps) {
  return (
    <div className={cn('relative', className)}>
      <Search className="absolute left-3 top-1/2 -translate-y-1/2 size-4 text-muted pointer-events-none" />
      <input
        type="search"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        onFocus={onFocus}
        placeholder={placeholder}
        className={cn(
          'w-full h-9 pl-9 pr-16 text-sm bg-elevated border border-border rounded-md',
          'placeholder:text-muted/60 text-foreground',
          'focus:outline-none focus:ring-1 focus:ring-accent/50 focus:border-accent/50',
          'transition-colors',
        )}
      />
      <div className="absolute right-2 top-1/2 -translate-y-1/2 flex items-center gap-1">
        {value && (
          <button
            type="button"
            onClick={() => onChange('')}
            className="p-1 text-muted hover:text-foreground rounded transition-colors"
            aria-label="Clear search"
          >
            <X className="size-3.5" />
          </button>
        )}
        {shortcut && !value && <kbd className="kbd">{shortcut}</kbd>}
      </div>
    </div>
  )
}
