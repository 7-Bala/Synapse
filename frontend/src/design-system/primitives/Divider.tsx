/**
 * @module Divider
 * @description A visual separator for layouts.
 * @version 1.0.0
 * @category Primitive
 * @maturity Beta
 */
import React from 'react';
import { cva, type VariantProps } from 'class-variance-authority';
import { cn } from '../utils/style';

const dividerVariants = cva(
  'bg-border-subtle shrink-0',
  {
    variants: {
      orientation: {
        horizontal: 'h-px w-full',
        vertical: 'h-full w-px',
      },
    },
    defaultVariants: {
      orientation: 'horizontal',
    },
  }
);

export interface DividerProps extends React.HTMLAttributes<HTMLDivElement>, VariantProps<typeof dividerVariants> {}

export const Divider = React.forwardRef<HTMLDivElement, DividerProps>(
  ({ className, orientation, ...props }, ref) => {
    return (
      <div ref={ref} role="separator" className={cn(dividerVariants({ orientation, className }))} {...props} />
    );
  }
);
Divider.displayName = 'Divider';
