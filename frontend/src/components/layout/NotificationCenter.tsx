import { AnimatePresence, motion } from 'framer-motion'
import { Bell, Check, CheckCheck, Trash2, X } from 'lucide-react'
import { useAppStore } from '@/stores/appStore'
import { formatRelativeTime } from '@/lib/utils'
import { cn } from '@/lib/utils'
import { useEscapeKey } from '@/hooks/useKeyboardShortcut'

export function NotificationCenter() {
  const open = useAppStore((s) => s.notificationCenterOpen)
  const setOpen = useAppStore((s) => s.setNotificationCenterOpen)
  const notifications = useAppStore((s) => s.notifications)
  const markRead = useAppStore((s) => s.markNotificationRead)
  const markAllRead = useAppStore((s) => s.markAllNotificationsRead)
  const clearAll = useAppStore((s) => s.clearNotifications)

  useEscapeKey(() => setOpen(false), open)

  return (
    <AnimatePresence>
      {open && (
        <>
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-40"
            onClick={() => setOpen(false)}
          />
          <motion.aside
            initial={{ x: '100%' }}
            animate={{ x: 0 }}
            exit={{ x: '100%' }}
            transition={{ type: 'spring', damping: 30, stiffness: 300 }}
            className="fixed right-0 top-0 bottom-0 z-50 w-full max-w-sm bg-surface border-l border-border flex flex-col shadow-2xl"
            aria-label="Notifications"
          >
            <div className="flex items-center justify-between h-14 px-4 border-b border-border shrink-0">
              <div className="flex items-center gap-2">
                <Bell className="size-4 text-muted" />
                <h2 className="text-sm font-medium">Notifications</h2>
              </div>
              <div className="flex items-center gap-1">
                {notifications.length > 0 && (
                  <>
                    <button
                      type="button"
                      onClick={markAllRead}
                      className="p-2 text-muted hover:text-foreground rounded-md hover:bg-elevated transition-colors"
                      aria-label="Mark all as read"
                    >
                      <CheckCheck className="size-4" />
                    </button>
                    <button
                      type="button"
                      onClick={clearAll}
                      className="p-2 text-muted hover:text-foreground rounded-md hover:bg-elevated transition-colors"
                      aria-label="Clear all notifications"
                    >
                      <Trash2 className="size-4" />
                    </button>
                  </>
                )}
                <button
                  type="button"
                  onClick={() => setOpen(false)}
                  className="p-2 text-muted hover:text-foreground rounded-md hover:bg-elevated transition-colors"
                  aria-label="Close notifications"
                >
                  <X className="size-4" />
                </button>
              </div>
            </div>

            <div className="flex-1 overflow-y-auto">
              {notifications.length === 0 ? (
                <div className="flex flex-col items-center justify-center h-full text-center px-6">
                  <Bell className="size-8 text-muted/40 mb-3" />
                  <p className="text-sm text-muted">No notifications yet</p>
                  <p className="text-xs text-muted/60 mt-1">
                    System events and pipeline updates will appear here
                  </p>
                </div>
              ) : (
                <ul className="divide-y divide-border">
                  {notifications.map((notification) => (
                    <li
                      key={notification.id}
                      className={cn(
                        'px-4 py-3 transition-colors',
                        !notification.read && 'bg-elevated/50',
                      )}
                    >
                      <div className="flex items-start gap-3">
                        <div
                          className={cn(
                            'mt-0.5 size-2 rounded-full shrink-0',
                            notification.type === 'success' && 'bg-success',
                            notification.type === 'warning' && 'bg-warning',
                            notification.type === 'error' && 'bg-danger',
                            notification.type === 'info' && 'bg-accent',
                          )}
                        />
                        <div className="flex-1 min-w-0">
                          <div className="flex items-start justify-between gap-2">
                            <p className="text-sm font-medium text-foreground">
                              {notification.title}
                            </p>
                            {!notification.read && (
                              <button
                                type="button"
                                onClick={() => markRead(notification.id)}
                                className="p-1 text-muted hover:text-foreground rounded shrink-0"
                                aria-label="Mark as read"
                              >
                                <Check className="size-3.5" />
                              </button>
                            )}
                          </div>
                          <p className="text-xs text-muted mt-0.5">{notification.message}</p>
                          <p className="text-2xs text-muted/60 mt-1 font-mono">
                            {formatRelativeTime(notification.timestamp)}
                          </p>
                        </div>
                      </div>
                    </li>
                  ))}
                </ul>
              )}
            </div>
          </motion.aside>
        </>
      )}
    </AnimatePresence>
  )
}
