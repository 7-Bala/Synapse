/**
 * @module Toolbar
 * @description A flex container specifically designed for action bars.
 * @version 1.0.0
 * @category Primitive
 * @maturity Beta
 */
import React from 'react';
import { cva, type VariantProps } from 'class-variance-authority';
import { cn } from '../utils/style';
import { Surface } from './Surface';

const toolbarVariants = cva(
  'flex items-center',
  {
    variants: {
      padding: {
        none: 'p-0',
        sm: 'px-2 py-1',
        md: 'px-4 py-2',
      },
      gap: {
        sm: 'gap-1',
        md: 'gap-2',
        lg: 'gap-4',
      }
    },
    defaultVariants: {
      padding: 'md',
      gap: 'md',
    },
  }
);

export interface ToolbarProps extends React.HTMLAttributes<HTMLDivElement>, VariantProps<typeof toolbarVariants> {}

export const Toolbar = React.forwardRef<HTMLDivElement, ToolbarProps>(
  ({ className, padding, gap, ...props }, ref) => {
    return (
      <Surface ref={ref} variant="transparent" border="none" className={cn(toolbarVariants({ padding, gap, className }))} {...props} />
    );
  }
);
Toolbar.displayName = 'Toolbar';
