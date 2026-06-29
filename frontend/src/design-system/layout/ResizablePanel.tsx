/**
 * @module ResizablePanel
 * @description A primitive that allows a panel to be resized via a drag handle. (Stub for future dragging logic).
 * @version 1.0.0
 * @category Layout
 * @maturity Beta
 */
import React, { useState } from 'react';
import { cn } from '../utils/style';

export interface ResizablePanelProps extends React.HTMLAttributes<HTMLDivElement> {
  defaultSize?: number;
  minSize?: number;
  maxSize?: number;
  orientation?: 'horizontal' | 'vertical';
}

export const ResizablePanel = React.forwardRef<HTMLDivElement, ResizablePanelProps>(
  ({ className, children, defaultSize = 300, orientation = 'horizontal', ...props }, ref) => {
    const [size] = useState(defaultSize);

    return (
      <div 
        ref={ref} 
        className={cn('relative flex-shrink-0', className)} 
        style={{ [orientation === 'horizontal' ? 'width' : 'height']: size }}
        {...props}
      >
        {children}
        {/* Resize Handle Stub */}
        <div className={cn(
          'absolute bg-border-subtle hover:bg-accent-default cursor-pointer transition-colors',
          orientation === 'horizontal' 
            ? 'top-0 right-0 w-1 h-full cursor-col-resize' 
            : 'bottom-0 left-0 h-1 w-full cursor-row-resize'
        )} />
      </div>
    );
  }
);
ResizablePanel.displayName = 'ResizablePanel';
