/**
 * @module DockLayout
 * @description A layout featuring a main stage and a bottom-aligned dock for tools/logs.
 * @version 1.0.0
 * @category Layout
 * @maturity Beta
 */
import React from 'react';
import { cn } from '../utils/style';
import { Surface } from '../primitives/Surface';
import { Divider } from '../primitives/Divider';

export interface DockLayoutProps extends React.HTMLAttributes<HTMLDivElement> {
  dock: React.ReactNode;
  dockOpen?: boolean;
  dockHeight?: number;
}

export const DockLayout = React.forwardRef<HTMLDivElement, DockLayoutProps>(
  ({ className, children, dock, dockOpen = true, dockHeight = 250, ...props }, ref) => {
    return (
      <div ref={ref} className={cn('flex flex-col w-full h-full overflow-hidden', className)} {...props}>
        <div className="flex-1 min-h-0 relative w-full">
          {children}
        </div>
        {dockOpen && (
          <>
            <Divider orientation="horizontal" />
            <Surface 
              variant="elevated" 
              className="w-full shrink-0 overflow-y-auto" 
              style={{ height: dockHeight }}
            >
              {dock}
            </Surface>
          </>
        )}
      </div>
    );
  }
);
DockLayout.displayName = 'DockLayout';
