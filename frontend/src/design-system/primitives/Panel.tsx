/**
 * @module Panel
 * @description A fundamental container block with built-in padding, surface, and border.
 * @version 1.0.0
 * @category Primitive
 * @maturity Beta
 */
import React from 'react';
import { cva, type VariantProps } from 'class-variance-authority';
import { cn } from '../utils/style';
import { Surface } from './Surface';

const panelVariants = cva(
  'flex flex-col',
  {
    variants: {
      padding: {
        none: 'p-0',
        sm: 'p-2',
        md: 'p-4',
        lg: 'p-6',
      }
    },
    defaultVariants: {
      padding: 'md',
    },
  }
);

export interface PanelProps extends React.HTMLAttributes<HTMLDivElement>, VariantProps<typeof panelVariants> {
  elevated?: boolean;
}

export const Panel = React.forwardRef<HTMLDivElement, PanelProps>(
  ({ className, padding, elevated = false, ...props }, ref) => {
    return (
      <Surface 
        ref={ref} 
        variant={elevated ? 'elevated' : 'panel'} 
        border="subtle" 
        radius="md" 
        elevation={elevated ? 'panel' : 'none'}
        className={cn(panelVariants({ padding, className }))} 
        {...props} 
      />
    );
  }
);
Panel.displayName = 'Panel';
