/**
 * @module PanelGroup
 * @description A layout primitive that hosts multiple panels with a shared gap.
 * @version 1.0.0
 * @category Layout
 * @maturity Beta
 */
import React from 'react';
import { cn } from '../utils/style';
import { Stack, type StackProps } from '../primitives/Stack';

export interface PanelGroupProps extends StackProps {}

export const PanelGroup = React.forwardRef<HTMLDivElement, PanelGroupProps>(
  ({ className, ...props }, ref) => {
    return (
      <Stack ref={ref} gap={4} className={cn('w-full', className)} {...props} />
    );
  }
);
PanelGroup.displayName = 'PanelGroup';
