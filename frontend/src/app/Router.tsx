import { createBrowserRouter, Navigate } from 'react-router-dom'
import { AppShell } from '@/app/AppShell'
import { DashboardPage } from '@/pages/DashboardPage'
import { DesignSystemShowcase } from '@/pages/DesignSystemShowcase'

export const router = createBrowserRouter([
  {
    path: '/',
    element: <AppShell />,
    children: [
      { index: true, element: <DashboardPage /> },
      { path: 'design-system', element: <DesignSystemShowcase /> },
      { path: '*', element: <Navigate to="/" replace /> },
    ],
  },
])
