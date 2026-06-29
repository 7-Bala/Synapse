import { useEffect, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import { navigation } from '@/config/navigation'

const shortcutMap: Record<string, string> = {
  d: '/',
  p: '/pipeline',
  r: '/replays',
  v: '/provenance',
  e: '/evaluation',
  b: '/benchmark',
  o: '/operations',
  f: '/failure-injection',
  '?': '/docs',
}

export function useNavigationShortcuts() {
  const navigate = useNavigate()
  const pendingRef = useRef(false)
  const timeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null)

  useEffect(() => {
    const handler = (event: KeyboardEvent) => {
      const target = event.target as HTMLElement
      if (
        target.tagName === 'INPUT' ||
        target.tagName === 'TEXTAREA' ||
        target.isContentEditable
      ) {
        return
      }

      if (event.metaKey || event.ctrlKey || event.altKey) return

      if (event.key.toLowerCase() === 'g') {
        pendingRef.current = true
        if (timeoutRef.current) clearTimeout(timeoutRef.current)
        timeoutRef.current = setTimeout(() => {
          pendingRef.current = false
        }, 1000)
        return
      }

      if (pendingRef.current) {
        const path = shortcutMap[event.key.toLowerCase()]
        if (path) {
          event.preventDefault()
          navigate(path)
        }
        pendingRef.current = false
        if (timeoutRef.current) clearTimeout(timeoutRef.current)
      }
    }

    window.addEventListener('keydown', handler)
    return () => {
      window.removeEventListener('keydown', handler)
      if (timeoutRef.current) clearTimeout(timeoutRef.current)
    }
  }, [navigate])
}

export { navigation }
