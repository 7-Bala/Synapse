import { useCallback, useEffect, useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import {
  LayoutDashboard,
  Search,
} from 'lucide-react'
import { navigation, type NavigationId } from '@/config/navigation'
import { useAppStore } from '@/stores/appStore'
import { useEscapeKey } from '@/hooks/useKeyboardShortcut'
import { cn } from '@/lib/utils'

const iconMap: Record<NavigationId, typeof LayoutDashboard> = {
  dashboard: LayoutDashboard,
}

export function CommandPalette() {
  const open = useAppStore((s) => s.commandPaletteOpen)
  const setOpen = useAppStore((s) => s.setCommandPaletteOpen)
  const [query, setQuery] = useState('')
  const [selectedIndex, setSelectedIndex] = useState(0)
  const navigate = useNavigate()

  const filtered = useMemo(() => {
    if (!query.trim()) return navigation
    const q = query.toLowerCase()
    return navigation.filter(
      (item) =>
        item.title.toLowerCase().includes(q) ||
        item.id.toLowerCase().includes(q),
    )
  }, [query])

  const close = useCallback(() => {
    setOpen(false)
    setQuery('')
    setSelectedIndex(0)
  }, [setOpen])

  const execute = useCallback(
    (path: string) => {
      navigate(path)
      close()
    },
    [navigate, close],
  )

  useEscapeKey(close, open)

  useEffect(() => {
    setSelectedIndex(0)
  }, [query])

  useEffect(() => {
    if (!open) return

    const handler = (event: KeyboardEvent) => {
      if (event.key === 'ArrowDown') {
        event.preventDefault()
        setSelectedIndex((i) => Math.min(i + 1, filtered.length - 1))
      } else if (event.key === 'ArrowUp') {
        event.preventDefault()
        setSelectedIndex((i) => Math.max(i - 1, 0))
      } else if (event.key === 'Enter' && filtered[selectedIndex]) {
        event.preventDefault()
        execute(filtered[selectedIndex].route)
      }
    }

    window.addEventListener('keydown', handler)
    return () => window.removeEventListener('keydown', handler)
  }, [open, filtered, selectedIndex, execute])

  return (
    <AnimatePresence>
      {open && (
        <>
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.15 }}
            className="fixed inset-0 z-50 bg-background/80 backdrop-blur-sm"
            onClick={close}
          />
          <motion.div
            initial={{ opacity: 0, scale: 0.98, y: -8 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.98, y: -8 }}
            transition={{ duration: 0.15, ease: 'easeOut' }}
            className="fixed inset-x-4 top-[15%] z-50 mx-auto max-w-lg"
            role="dialog"
            aria-modal="true"
            aria-label="Command palette"
          >
            <div className="panel-elevated overflow-hidden shadow-glow">
              <div className="flex items-center gap-3 px-4 border-b border-border">
                <Search className="size-4 text-muted shrink-0" />
                <input
                  autoFocus
                  type="text"
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  placeholder="Search pages and actions..."
                  className="flex-1 h-12 bg-transparent text-sm text-foreground placeholder:text-muted outline-none"
                />
                <kbd className="kbd">ESC</kbd>
              </div>

              <ul className="max-h-72 overflow-y-auto py-2" role="listbox">
                {filtered.length === 0 ? (
                  <li className="px-4 py-6 text-center text-sm text-muted">
                    No results found
                  </li>
                ) : (
                  filtered.map((item, index) => {
                    const Icon = iconMap[item.id]
                    return (
                      <li key={item.id} role="option" aria-selected={index === selectedIndex}>
                        <button
                          type="button"
                          onClick={() => execute(item.route)}
                          onMouseEnter={() => setSelectedIndex(index)}
                          className={cn(
                            'flex items-center gap-3 w-full px-4 py-2.5 text-sm text-left transition-colors',
                            index === selectedIndex
                              ? 'bg-accent-muted text-accent'
                              : 'text-foreground hover:bg-elevated',
                          )}
                        >
                          <Icon className="size-4 shrink-0" />
                          <span className="flex-1">{item.title}</span>
                          <kbd className="kbd text-2xs">{item.shortcut}</kbd>
                        </button>
                      </li>
                    )
                  })
                )}
              </ul>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  )
}
