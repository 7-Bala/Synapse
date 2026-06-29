/**
 * @module WorkspaceGrid
 * @description A rigid 2D grid used as the canvas for topological workspaces (like Mission Control).
 * @version 1.0.0
 * @category Layout
 * @maturity Beta
 */
import React from 'react';
import { cn } from '../utils/style';

export interface WorkspaceGridProps extends React.HTMLAttributes<HTMLDivElement> {
  gridSize?: number;
}

export const WorkspaceGrid = React.forwardRef<HTMLDivElement, WorkspaceGridProps>(
  ({ className, children, gridSize = 40, ...props }, ref) => {
    return (
      <div 
        ref={ref} 
        className={cn('w-full h-full relative overflow-hidden bg-background', className)} 
        style={{
          backgroundImage: `radial-gradient(var(--color-border-subtle) 1px, transparent 1px)`,
          backgroundSize: `${gridSize}px ${gridSize}px`,
        }}
        {...props}
      >
        {children}
      </div>
    );
  }
);
WorkspaceGrid.displayName = 'WorkspaceGrid';
