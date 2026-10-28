import { useState } from 'react';
import { ChevronDown, ChevronRight } from 'lucide-react';
import { NavLink } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { cn } from '@/lib/utils';
import { getNavigationGroups, type WorkspaceGroup } from '@/config/navigation';

interface WorkspaceDockProps {
  mobile?: boolean;
}

export function WorkspaceDock(_props: WorkspaceDockProps) {
  const groups = getNavigationGroups();
  
  // Track collapsed state for each group (default open)
  const [collapsedGroups, setCollapsedGroups] = useState<Record<string, boolean>>({});

  const toggleGroup = (group: WorkspaceGroup) => {
    setCollapsedGroups(prev => ({
      ...prev,
      [group]: !prev[group]
    }));
  };

  return (
    <div className="flex flex-col h-full w-[240px] bg-background-dark border-r border-border shrink-0 py-4 z-50 overflow-y-auto overflow-x-hidden">
      {/* Brand Header */}
      <div className="flex items-center gap-3 px-6 mb-8 relative group">
        <div className="flex items-center justify-center size-8 rounded-[6px] relative">
          <img src="/logo.png" alt="Synapse Logo" className="w-full h-full object-contain mix-blend-screen" />
          {/* Glow effect */}
          <div className="absolute inset-0 bg-accent/20 blur-md rounded-full opacity-0 group-hover:opacity-100 transition-opacity duration-300 pointer-events-none" />
        </div>
        <span className="font-semibold text-foreground tracking-tight">Synapse OS</span>
      </div>

      <nav className="flex flex-col gap-6 w-full px-4">
        {(Object.entries(groups) as [WorkspaceGroup, typeof groups[WorkspaceGroup]][]).map(([groupName, items]) => {
          if (items.length === 0) return null;
          
          const isCollapsed = collapsedGroups[groupName];

          return (
            <div key={groupName} className="flex flex-col gap-1">
              <button 
                onClick={() => toggleGroup(groupName)}
                className="flex items-center justify-between px-2 py-1 mb-1 group/header w-full text-left"
              >
                <span className="text-2xs font-mono font-semibold uppercase tracking-wider text-muted group-hover/header:text-foreground transition-colors">
                  {groupName}
                </span>
                {isCollapsed ? (
                  <ChevronRight className="size-3 text-muted" />
                ) : (
                  <ChevronDown className="size-3 text-muted" />
                )}
              </button>
              
              <AnimatePresence initial={false}>
                {!isCollapsed && (
                  <motion.div
                    initial={{ height: 0, opacity: 0 }}
                    animate={{ height: 'auto', opacity: 1 }}
                    exit={{ height: 0, opacity: 0 }}
                    transition={{ duration: 0.2 }}
                    className="flex flex-col gap-1 overflow-hidden"
                  >
                    {items.map((item) => {
                      const Icon = item.icon;
                      return (
                        <NavLink
                          key={item.id}
                          to={item.route}
                          className={({ isActive }) =>
                            cn(
                              'relative group flex items-center justify-between w-full px-2 py-2 rounded-md transition-all duration-200',
                              isActive
                                ? 'text-accent bg-surface-elevated shadow-sm'
                                : 'text-muted hover:text-foreground hover:bg-surface'
                            )
                          }
                          title={item.title}
                        >
                          {({ isActive }) => (
                            <>
                              <div className="flex items-center gap-3 overflow-hidden">
                                <Icon className="size-4 shrink-0" strokeWidth={1.5} />
                                <span className="text-sm font-medium truncate">{item.title}</span>

                              </div>
                              
                              {/* Keyboard Shortcut Display */}
                              {item.shortcut && (
                                <span className="text-2xs font-mono px-1.5 py-0.5 rounded border border-border-subtle bg-surface text-muted opacity-0 group-hover:opacity-100 transition-opacity shrink-0">
                                  {item.shortcut}
                                </span>
                              )}

                              {/* Active Indicator */}
                              {isActive && (
                                <motion.div
                                  layoutId="active-dock-indicator"
                                  className="absolute left-0 w-0.5 h-6 bg-accent rounded-r-full"
                                  transition={{ type: 'spring', stiffness: 300, damping: 30 }}
                                />
                              )}
                            </>
                          )}
                        </NavLink>
                      );
                    })}
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          );
        })}
      </nav>
    </div>
  );
}
