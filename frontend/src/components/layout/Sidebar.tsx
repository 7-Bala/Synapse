import {
  LayoutDashboard,
  SquareTerminal,
} from 'lucide-react';
import { NavLink } from 'react-router-dom';
import { motion } from 'framer-motion';
import { cn } from '@/lib/utils';
import { navigation, type NavigationId } from '@/config/navigation';

const iconMap: Record<NavigationId, typeof LayoutDashboard> = {
  dashboard: LayoutDashboard,
};

interface WorkspaceDockProps {
  mobile?: boolean;
}

export function WorkspaceDock(_props: WorkspaceDockProps) {
  return (
    <div className="flex flex-col h-full w-14 bg-background-dark border-r border-border shrink-0 items-center py-4 z-50">
      {/* Abstract Geometric Logo (Placeholder until SVG asset is ready) */}
      <div className="flex items-center justify-center size-8 rounded-[6px] bg-accent/10 text-accent mb-8 relative group">
        <SquareTerminal className="size-4" strokeWidth={1.5} />
        {/* Glow effect */}
        <div className="absolute inset-0 bg-accent/20 blur-md rounded-full opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
      </div>

      <nav className="flex flex-col gap-3 w-full px-2">
        {navigation.map((item) => {
          const Icon = iconMap[item.id];
          return (
            <NavLink
              key={item.id}
              to={item.path}
              className={({ isActive }) =>
                cn(
                  'relative group flex items-center justify-center size-10 rounded-md transition-all duration-200',
                  isActive
                    ? 'text-accent bg-surface-elevated shadow-sm'
                    : 'text-muted hover:text-foreground hover:bg-surface'
                )
              }
              title={item.label}
            >
              {({ isActive }) => (
                <>
                  <Icon className="size-4" strokeWidth={1.5} />
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
      </nav>
    </div>
  );
}
