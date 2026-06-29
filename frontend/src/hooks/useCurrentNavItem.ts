import { useLocation } from 'react-router-dom'
import { navigation } from '@/config/navigation'

export function useCurrentNavItem() {
  const location = useLocation()
  return navigation.find((n) =>
    n.route === '/' ? location.pathname === '/' : location.pathname.startsWith(n.route),
  )
}
