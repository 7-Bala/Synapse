/**
 * @module ScrollableArea
 * @description A container that manages its own scroll state, hiding raw browser scrollbars where possible.
 * @version 1.0.0
 * @category Primitive
 * @maturity Beta
 */
import React from 'react';
import { cn } from '../utils/style';

export interface ScrollableAreaProps extends React.HTMLAttributes<HTMLDivElement> {
  orientation?: 'vertical' | 'horizontal' | 'both';
}

export const ScrollableArea = React.forwardRef<HTMLDivElement, ScrollableAreaProps>(
  ({ className, orientation = 'vertical', ...props }, ref) => {
    const overflowClass = 
      orientation === 'vertical' ? 'overflow-y-auto overflow-x-hidden' :
      orientation === 'horizontal' ? 'overflow-x-auto overflow-y-hidden' :
      'overflow-auto';

    return (
      <div ref={ref} className={cn(overflowClass, className)} {...props} />
    );
  }
);
ScrollableArea.displayName = 'ScrollableArea';
