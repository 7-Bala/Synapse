/**
 * @module InspectorLayout
 * @description An enterprise layout featuring a main content area and a collapsible right-side inspector.
 * @version 1.0.0
 * @category Layout
 * @maturity Beta
 */
import React from 'react';
import { cn } from '../utils/style';
import { Surface } from '../primitives/Surface';
import { Divider } from '../primitives/Divider';

export interface InspectorLayoutProps extends React.HTMLAttributes<HTMLDivElement> {
  inspector: React.ReactNode;
  inspectorOpen?: boolean;
  inspectorWidth?: number;
}

export const InspectorLayout = React.forwardRef<HTMLDivElement, InspectorLayoutProps>(
  ({ className, children, inspector, inspectorOpen = true, inspectorWidth = 320, ...props }, ref) => {
    return (
      <div ref={ref} className={cn('flex w-full h-full overflow-hidden', className)} {...props}>
        <div className="flex-1 min-w-0 h-full relative">
          {children}
        </div>
        {inspectorOpen && (
          <>
            <Divider orientation="vertical" />
            <Surface 
              variant="elevated" 
              className="h-full shrink-0 overflow-y-auto" 
              style={{ width: inspectorWidth }}
            >
              {inspector}
            </Surface>
          </>
        )}
      </div>
    );
  }
);
InspectorLayout.displayName = 'InspectorLayout';
