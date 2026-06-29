/**
 * @module Stack
 * @description Flexbox layout primitive for organizing items in a 1D axis.
 * @version 1.0.0
 * @category Primitive
 * @maturity Beta
 */
import React from 'react';
import { cva, type VariantProps } from 'class-variance-authority';
import { cn } from '../utils/style';

const stackVariants = cva(
  'flex',
  {
    variants: {
      direction: {
        row: 'flex-row',
        col: 'flex-col',
        rowReverse: 'flex-row-reverse',
        colReverse: 'flex-col-reverse',
      },
      align: {
        start: 'items-start',
        center: 'items-center',
        end: 'items-end',
        stretch: 'items-stretch',
        baseline: 'items-baseline',
      },
      justify: {
        start: 'justify-start',
        center: 'justify-center',
        end: 'justify-end',
        between: 'justify-between',
        around: 'justify-around',
      },
      gap: {
        0: 'gap-0',
        1: 'gap-1',
        2: 'gap-2',
        3: 'gap-3',
        4: 'gap-4',
        6: 'gap-6',
        8: 'gap-8',
      },
      wrap: {
        nowrap: 'flex-nowrap',
        wrap: 'flex-wrap',
        wrapReverse: 'flex-wrap-reverse',
      }
    },
    defaultVariants: {
      direction: 'col',
      align: 'stretch',
      justify: 'start',
      gap: 4,
      wrap: 'nowrap',
    },
  }
);

export interface StackProps extends React.HTMLAttributes<HTMLDivElement>, VariantProps<typeof stackVariants> {
  as?: React.ElementType;
}

export const Stack = React.forwardRef<HTMLDivElement, StackProps>(
  ({ className, direction, align, justify, gap, wrap, as: Component = 'div', ...props }, ref) => {
    return (
      <Component ref={ref} className={cn(stackVariants({ direction, align, justify, gap, wrap, className }))} {...props} />
    );
  }
);
Stack.displayName = 'Stack';
