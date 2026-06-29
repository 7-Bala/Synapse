import React from 'react'
import { createRoot } from 'react-dom/client'
import { RouterProvider } from 'react-router-dom'
import { router } from './app/Router'
import { DesignSystemProvider } from '@/design-system/providers/DesignSystemProvider'
import './index.css'

const root = document.getElementById('root')
if (root) {
  createRoot(root).render(
    <React.StrictMode>
      <DesignSystemProvider>
        <RouterProvider router={router} />
      </DesignSystemProvider>
    </React.StrictMode>,
  )
}
