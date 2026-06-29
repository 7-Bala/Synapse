
import { Outlet } from 'react-router-dom'
import { AnimatePresence, motion } from 'framer-motion'
import { WorkspaceDock } from '@/components/layout/Sidebar'
import { WorkspaceHeader } from '@/components/layout/TopNav'
import { BottomUtilities } from '@/components/layout/BottomUtilities'
import { CommandPalette } from '@/components/layout/CommandPalette'
import { NotificationCenter } from '@/components/layout/NotificationCenter'
import { ErrorBoundary } from '@/components/ErrorBoundary'
import { useAppStore } from '@/stores/appStore'
import { useKeyboardShortcut, useIsMobile } from '@/hooks/useKeyboardShortcut'
import { useNavigationShortcuts } from '@/hooks/useNavigationShortcuts'

export function AppShell() {
  const setCommandPaletteOpen = useAppStore((s) => s.setCommandPaletteOpen)
  const sidebarMobileOpen = useAppStore((s) => s.sidebarMobileOpen)
  const setSidebarMobileOpen = useAppStore((s) => s.setSidebarMobileOpen)
  const isMobile = useIsMobile()

  useKeyboardShortcut('k', () => setCommandPaletteOpen(true), { meta: true })
  useNavigationShortcuts()

  return (
    <div className="flex flex-col h-screen w-screen overflow-hidden bg-background">
      <WorkspaceHeader onOpenCommandPalette={() => setCommandPaletteOpen(true)} />
      
      <div className="flex flex-1 min-h-0 w-full">
        {/* Desktop sidebar */}
        <div className="hidden lg:block h-full shrink-0">
          <WorkspaceDock />
        </div>

        {/* Mobile sidebar overlay */}
        <AnimatePresence>
          {isMobile && sidebarMobileOpen && (
            <>
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="fixed inset-0 z-40 bg-background/80 backdrop-blur-sm lg:hidden"
                onClick={() => setSidebarMobileOpen(false)}
              />
              <motion.div
                initial={{ x: '-100%' }}
                animate={{ x: 0 }}
                exit={{ x: '-100%' }}
                transition={{ type: 'spring', damping: 30, stiffness: 300 }}
                className="fixed inset-y-0 left-0 z-50 lg:hidden"
              >
                <WorkspaceDock mobile />
              </motion.div>
            </>
          )}
        </AnimatePresence>

        <main className="flex-1 min-w-0 overflow-hidden bg-background-dark h-full">
          <ErrorBoundary>
            <Outlet />
          </ErrorBoundary>
        </main>
      </div>

      <BottomUtilities />

      <CommandPalette />
      <NotificationCenter />
    </div>
  )
}
