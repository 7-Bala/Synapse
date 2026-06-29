/**
 * @module Surface
 * @description The foundational layer for structural components. Handles background, elevation, and borders.
 * @version 1.0.0
 * @category Primitive
 * @maturity Beta
 */
import React from 'react';
import { cva, type VariantProps } from 'class-variance-authority';
import { cn } from '../utils/style';

const surfaceVariants = cva(
  'transition-colors duration-200',
  {
    variants: {
      variant: {
        default: 'bg-background',
        elevated: 'bg-surface-elevated',
        panel: 'bg-surface',
        transparent: 'bg-transparent',
      },
      elevation: {
        none: 'shadow-none',
        sm: 'shadow-sm',
        panel: 'shadow-panel',
        modal: 'shadow-modal',
      },
      border: {
        none: 'border-none',
        subtle: 'border border-border-subtle',
        strong: 'border border-border-strong',
      },
      radius: {
        none: 'rounded-none',
        sm: 'rounded-sm',
        md: 'rounded-md',
        lg: 'rounded-lg',
      }
    },
    defaultVariants: {
      variant: 'default',
      elevation: 'none',
      border: 'none',
      radius: 'none',
    },
  }
);

export interface SurfaceProps extends React.HTMLAttributes<HTMLDivElement>, VariantProps<typeof surfaceVariants> {}

export const Surface = React.forwardRef<HTMLDivElement, SurfaceProps>(
  ({ className, variant, elevation, border, radius, ...props }, ref) => {
    return (
      <div ref={ref} className={cn(surfaceVariants({ variant, elevation, border, radius, className }))} {...props} />
    );
  }
);
Surface.displayName = 'Surface';
