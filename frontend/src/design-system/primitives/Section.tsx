/**
 * @module Section
 * @description A semantic container for grouped content.
 * @version 1.0.0
 * @category Primitive
 * @maturity Beta
 */
import React from 'react';
import { cva, type VariantProps } from 'class-variance-authority';
import { cn } from '../utils/style';

const sectionVariants = cva(
  'flex flex-col',
  {
    variants: {
      spacing: {
        sm: 'gap-2',
        md: 'gap-4',
        lg: 'gap-6',
        xl: 'gap-8',
      }
    },
    defaultVariants: {
      spacing: 'md',
    },
  }
);

export interface SectionProps extends Omit<React.HTMLAttributes<HTMLElement>, 'title'>, VariantProps<typeof sectionVariants> {
  title?: React.ReactNode;
}

export const Section = React.forwardRef<HTMLElement, SectionProps>(
  ({ className, spacing, title, children, ...props }, ref) => {
    return (
      <section ref={ref} className={cn(sectionVariants({ spacing, className }))} {...props}>
        {title && <h3 className="text-sectionTitle font-medium text-text-primary">{title}</h3>}
        {children}
      </section>
    );
  }
);
Section.displayName = 'Section';
