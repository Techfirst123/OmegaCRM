import React from 'react'
import { Outlet } from 'react-router-dom'
import Sidebar from './Sidebar'
import Header from './Header'
import AIAssistant from '../assistant/AIAssistant'

export default function Layout() {
  return (
    <div className="flex h-screen overflow-hidden bg-surface-50">
      <Sidebar />
      <div className="flex-1 flex flex-col ml-64 min-w-0 overflow-hidden">
        <Header />
        <main className="flex-1 overflow-y-auto p-6">
          <Outlet />
        </main>
      </div>
      {/* Floating AI assistant — visible across all pages */}
      <AIAssistant />
    </div>
  )
}
