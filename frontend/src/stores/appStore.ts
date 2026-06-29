import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import type { Notification } from '@/types/models'

interface AppState {
  sidebarCollapsed: boolean
  sidebarMobileOpen: boolean
  commandPaletteOpen: boolean
  notificationCenterOpen: boolean
  globalSearchQuery: string
  notifications: Notification[]

  toggleSidebar: () => void
  setSidebarCollapsed: (collapsed: boolean) => void
  setSidebarMobileOpen: (open: boolean) => void
  toggleCommandPalette: () => void
  setCommandPaletteOpen: (open: boolean) => void
  toggleNotificationCenter: () => void
  setNotificationCenterOpen: (open: boolean) => void
  setGlobalSearchQuery: (query: string) => void
  addNotification: (notification: Omit<Notification, 'id' | 'read'>) => void
  markNotificationRead: (id: string) => void
  markAllNotificationsRead: () => void
  clearNotifications: () => void
}

export const useAppStore = create<AppState>()(
  persist(
    (set) => ({
      sidebarCollapsed: false,
      sidebarMobileOpen: false,
      commandPaletteOpen: false,
      notificationCenterOpen: false,
      globalSearchQuery: '',
      notifications: [],

      toggleSidebar: () =>
        set((state) => ({ sidebarCollapsed: !state.sidebarCollapsed })),
      setSidebarCollapsed: (collapsed) => set({ sidebarCollapsed: collapsed }),
      setSidebarMobileOpen: (open) => set({ sidebarMobileOpen: open }),
      toggleCommandPalette: () =>
        set((state) => ({ commandPaletteOpen: !state.commandPaletteOpen })),
      setCommandPaletteOpen: (open) => set({ commandPaletteOpen: open }),
      toggleNotificationCenter: () =>
        set((state) => ({ notificationCenterOpen: !state.notificationCenterOpen })),
      setNotificationCenterOpen: (open) => set({ notificationCenterOpen: open }),
      setGlobalSearchQuery: (query) => set({ globalSearchQuery: query }),
      addNotification: (notification) =>
        set((state) => ({
          notifications: [
            {
              ...notification,
              id: crypto.randomUUID(),
              read: false,
            },
            ...state.notifications,
          ].slice(0, 50),
        })),
      markNotificationRead: (id) =>
        set((state) => ({
          notifications: state.notifications.map((n) =>
            n.id === id ? { ...n, read: true } : n,
          ),
        })),
      markAllNotificationsRead: () =>
        set((state) => ({
          notifications: state.notifications.map((n) => ({ ...n, read: true })),
        })),
      clearNotifications: () => set({ notifications: [] }),
    }),
    {
      name: 'synapse-app',
      partialize: (state) => ({
        sidebarCollapsed: state.sidebarCollapsed,
      }),
    },
  ),
)

export const useUnreadNotificationCount = () =>
  useAppStore((state) => state.notifications.filter((n) => !n.read).length)
