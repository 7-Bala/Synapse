/**
 * @module SplitView
 * @description A structural layout that divides space equally or proportionally between two children.
 * @version 1.0.0
 * @category Layout
 * @maturity Beta
 */
import React from 'react';
import { cn } from '../utils/style';

export interface SplitViewProps extends React.HTMLAttributes<HTMLDivElement> {
  orientation?: 'horizontal' | 'vertical';
  proportions?: [number, number];
}

export const SplitView = React.forwardRef<HTMLDivElement, SplitViewProps>(
  ({ className, orientation = 'horizontal', proportions = [1, 1], children, ...props }, ref) => {
    const isHorizontal = orientation === 'horizontal';
    const childrenArray = React.Children.toArray(children);
    
    if (childrenArray.length !== 2) {
      console.warn('SplitView requires exactly 2 children.');
    }

    return (
      <div 
        ref={ref} 
        className={cn('flex w-full h-full', isHorizontal ? 'flex-row' : 'flex-col', className)} 
        {...props}
      >
        <div style={{ flex: proportions[0] }} className="min-w-0 min-h-0 relative">
          {childrenArray[0]}
        </div>
        <div style={{ flex: proportions[1] }} className="min-w-0 min-h-0 relative">
          {childrenArray[1]}
        </div>
      </div>
    );
  }
);
SplitView.displayName = 'SplitView';
