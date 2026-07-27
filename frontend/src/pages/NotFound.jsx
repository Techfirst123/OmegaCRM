import React from 'react'
import { Link } from 'react-router-dom'
import { ArrowLeft, Zap } from 'lucide-react'

export default function NotFound() {
  return (
    <div className="flex flex-col items-center justify-center h-full py-24 text-center">
      <div className="w-16 h-16 bg-brand-50 border border-brand-100 rounded-2xl flex items-center justify-center mb-6">
        <Zap size={28} className="text-brand-400" />
      </div>
      <h1 className="text-5xl font-bold text-slate-900 mb-3">404</h1>
      <h2 className="text-xl font-semibold text-slate-700 mb-2">Page not found</h2>
      <p className="text-slate-400 text-sm mb-8 max-w-sm">
        The page you're looking for doesn't exist or has been moved.
      </p>
      <Link to="/" className="btn-primary">
        <ArrowLeft size={15} />Back to Dashboard
      </Link>
    </div>
  )
}
