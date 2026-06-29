import { 
  Activity, 
  TerminalSquare, 
  RotateCcw, 
  Search, 
  Users, 
  BarChart2, 
  Settings 
} from 'lucide-react';
import type { LucideIcon } from 'lucide-react';

export type WorkspaceGroup = 'Mission Control' | 'Runtime' | 'Analysis' | 'System';

export interface WorkspaceConfig {
  id: string;
  title: string;
  description: string;
  route: string;
  icon: LucideIcon;
  group: WorkspaceGroup;
  order: number;
  shortcut: string;
  breadcrumb: string;
  hidden: boolean;
  beta: boolean;
  enabled: boolean;
}

export const navigation: WorkspaceConfig[] = [
  {
    id: 'mission-control',
    title: 'Mission Control',
    description: 'What is happening right now?',
    route: '/',
    icon: Activity,
    group: 'Mission Control',
    order: 1,
    shortcut: 'G M',
    breadcrumb: 'Mission Control',
    hidden: false,
    beta: false,
    enabled: true,
  },
  {
    id: 'executions',
    title: 'Executions',
    description: 'Inspect and control active orchestrations.',
    route: '/executions',
    icon: TerminalSquare,
    group: 'Runtime',
    order: 2,
    shortcut: 'G E',
    breadcrumb: 'Executions',
    hidden: false,
    beta: false,
    enabled: true,
  },
  {
    id: 'replay',
    title: 'Replay',
    description: 'Time-travel debugging and execution playback.',
    route: '/replay',
    icon: RotateCcw,
    group: 'Runtime',
    order: 3,
    shortcut: 'G R',
    breadcrumb: 'Replay',
    hidden: false,
    beta: true,
    enabled: true,
  },
  {
    id: 'evidence',
    title: 'Evidence',
    description: 'Inspect artifacts, files, and generated outputs.',
    route: '/evidence',
    icon: Search,
    group: 'Analysis',
    order: 4,
    shortcut: 'G V',
    breadcrumb: 'Evidence',
    hidden: false,
    beta: true,
    enabled: true,
  },
  {
    id: 'agents',
    title: 'Agents',
    description: 'Agent configuration, swarms, and capabilities.',
    route: '/agents',
    icon: Users,
    group: 'Analysis',
    order: 5,
    shortcut: 'G A',
    breadcrumb: 'Agents',
    hidden: false,
    beta: true,
    enabled: true,
  },
  {
    id: 'telemetry',
    title: 'Telemetry',
    description: 'System health, metrics, and token usage.',
    route: '/telemetry',
    icon: BarChart2,
    group: 'Analysis',
    order: 6,
    shortcut: 'G T',
    breadcrumb: 'Telemetry',
    hidden: false,
    beta: true,
    enabled: true,
  },
  {
    id: 'settings',
    title: 'Settings',
    description: 'System configuration and preferences.',
    route: '/settings',
    icon: Settings,
    group: 'System',
    order: 7,
    shortcut: 'G S',
    breadcrumb: 'Settings',
    hidden: false,
    beta: false,
    enabled: true,
  },
];

export type NavigationId = typeof navigation[number]['id'];

export const navigationById = Object.fromEntries(
  navigation.map((item) => [item.id, item]),
) as Record<NavigationId, WorkspaceConfig>;

export function getPageTitle(pathname: string): string {
  const item = navigation.find((n) =>
    n.route === '/' ? pathname === '/' : pathname.startsWith(n.route),
  );
  return item?.title ?? 'Synapse';
}

export function getNavigationGroups(): Record<WorkspaceGroup, WorkspaceConfig[]> {
  const groups: Record<WorkspaceGroup, WorkspaceConfig[]> = {
    'Mission Control': [],
    'Runtime': [],
    'Analysis': [],
    'System': []
  };
  
  navigation
    .filter(nav => !nav.hidden && nav.enabled)
    .sort((a, b) => a.order - b.order)
    .forEach(nav => {
      groups[nav.group].push(nav);
    });
    
  return groups;
}
