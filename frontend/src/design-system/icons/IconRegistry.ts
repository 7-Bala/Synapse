// Layered Icon Architecture
export type IconLayer = 'System' | 'Domain' | 'Illustration';

export interface IconDefinition {
  id: string;
  layer: IconLayer;
  component: React.ComponentType<any>;
}

export const IconRegistry: Record<string, IconDefinition> = {};
