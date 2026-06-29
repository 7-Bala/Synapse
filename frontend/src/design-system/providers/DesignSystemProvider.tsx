/**
 * @module DesignSystemProvider
 * @description Composes all underlying Design System providers (Theme, Motion, Localization, Density, Accessibility, Feature Flags).
 */
import React from 'react';
import { ThemeProvider } from './ThemeProvider';

// Stubs for future providers
function MotionProvider({ children }: { children: React.ReactNode }) { return <>{children}</>; }
function LocalizationProvider({ children }: { children: React.ReactNode }) { return <>{children}</>; }
function DensityProvider({ children }: { children: React.ReactNode }) { return <>{children}</>; }
function AccessibilityProvider({ children }: { children: React.ReactNode }) { return <>{children}</>; }
function FeatureFlagProvider({ children }: { children: React.ReactNode }) { return <>{children}</>; }

export function DesignSystemProvider({ children }: { children: React.ReactNode }) {
  return (
    <FeatureFlagProvider>
      <AccessibilityProvider>
        <LocalizationProvider>
          <ThemeProvider>
            <DensityProvider>
              <MotionProvider>
                {children}
              </MotionProvider>
            </DensityProvider>
          </ThemeProvider>
        </LocalizationProvider>
      </AccessibilityProvider>
    </FeatureFlagProvider>
  );
}
