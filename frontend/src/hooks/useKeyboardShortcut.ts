import { useEffect, useState } from 'react'

export function useKeyboardShortcut(
  key: string,
  callback: () => void,
  options: { meta?: boolean; ctrl?: boolean; shift?: boolean; enabled?: boolean } = {},
) {
  const { meta = false, ctrl = false, shift = false, enabled = true } = options

  useEffect(() => {
    if (!enabled) return

    const handler = (event: KeyboardEvent) => {
      const keyMatch = event.key.toLowerCase() === key.toLowerCase()
      const metaMatch = meta ? event.metaKey || event.ctrlKey : !event.metaKey && !event.ctrlKey
      const ctrlMatch = ctrl ? event.ctrlKey : true
      const shiftMatch = shift ? event.shiftKey : !event.shiftKey

      if (keyMatch && metaMatch && ctrlMatch && shiftMatch) {
        event.preventDefault()
        callback()
      }
    }

    window.addEventListener('keydown', handler)
    return () => window.removeEventListener('keydown', handler)
  }, [key, callback, meta, ctrl, shift, enabled])
}

export function useEscapeKey(callback: () => void, enabled = true) {
  useEffect(() => {
    if (!enabled) return

    const handler = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        callback()
      }
    }

    window.addEventListener('keydown', handler)
    return () => window.removeEventListener('keydown', handler)
  }, [callback, enabled])
}

export function useMediaQuery(query: string): boolean {
  const getMatches = () =>
    typeof window !== 'undefined' ? window.matchMedia(query).matches : false

  const [matches, setMatches] = useState(getMatches)

  useEffect(() => {
    const media = window.matchMedia(query)
    const handler = (event: MediaQueryListEvent) => setMatches(event.matches)
    setMatches(media.matches)
    media.addEventListener('change', handler)
    return () => media.removeEventListener('change', handler)
  }, [query])

  return matches
}

export function useIsMobile() {
  return useMediaQuery('(max-width: 1023px)')
}
