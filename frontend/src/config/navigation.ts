export const navigation = [
  {
    id: 'dashboard',
    label: 'Dashboard',
    path: '/',
    shortcut: 'G D',
  },
] as const

export type NavigationId = (typeof navigation)[number]['id']

export const navigationById = Object.fromEntries(
  navigation.map((item) => [item.id, item]),
) as Record<NavigationId, (typeof navigation)[number]>

export function getPageTitle(pathname: string): string {
  const item = navigation.find((n) =>
    n.path === '/' ? pathname === '/' : pathname.startsWith(n.path),
  )
  return item?.label ?? 'Synapse'
}
