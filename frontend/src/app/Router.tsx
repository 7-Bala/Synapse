import { createBrowserRouter, Navigate } from 'react-router-dom';
import { AppShell } from '@/app/AppShell';
import { MissionControlPage } from '@/pages/MissionControlPage';
import { ExecutionsPage } from '@/pages/ExecutionsPage';
import { ReplayPage } from '@/pages/ReplayPage';
import { EvidencePage } from '@/pages/EvidencePage';
import { AgentsPage } from '@/pages/AgentsPage';
import { TelemetryPage } from '@/pages/TelemetryPage';
import { SettingsPage } from '@/pages/SettingsPage';
import { DesignSystemShowcase } from '@/pages/DesignSystemShowcase';

export const router = createBrowserRouter([
  {
    path: '/',
    element: <AppShell />,
    children: [
      { index: true, element: <MissionControlPage /> },
      { path: 'executions', element: <ExecutionsPage /> },
      { path: 'replay', element: <ReplayPage /> },
      { path: 'evidence', element: <EvidencePage /> },
      { path: 'agents', element: <AgentsPage /> },
      { path: 'telemetry', element: <TelemetryPage /> },
      { path: 'settings', element: <SettingsPage /> },
      { path: 'design-system', element: <DesignSystemShowcase /> },
      { path: '*', element: <Navigate to="/" replace /> },
    ],
  },
]);
