import React, { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { Plus, Loader2, AlertCircle, FileText } from 'lucide-react'

const LIST_URL = '/procurement/api/quotations/'

const STATUS_LABELS = {
  draft: { label: 'Draft', className: 'bg-slate-100 text-slate-600' },
  verified: { label: 'Verified', className: 'bg-emerald-100 text-emerald-700' },
  converted: { label: 'Converted to PO', className: 'bg-brand-100 text-brand-700' },
}

export default function QuotationList() {
  const [quotations, setQuotations] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const fetchQuotations = () => {
    setLoading(true)
    setError('')
    fetch(LIST_URL, { credentials: 'same-origin' })
      .then((res) => res.json().then((data) => ({ ok: res.ok, data })))
      .then(({ ok, data }) => {
        if (!ok) throw new Error(data.error || 'Could not load quotations.')
        setQuotations(data.results || [])
      })
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false))
  }

  useEffect(() => { fetchQuotations() }, [])

  return (
    <div className="space-y-6 pb-4">
      <div className="page-header">
        <div>
          <h2 className="page-title">Quotations</h2>
          <p className="page-subtitle">{loading ? 'Loading…' : `${quotations.length} quotation${quotations.length === 1 ? '' : 's'}`}</p>
        </div>
        <Link to="/materials/quotations/new" className="btn-primary"><Plus size={14} />New Quotation</Link>
      </div>

      {error && (
        <div className="flex items-center gap-2.5 bg-red-50 text-red-700 border border-red-200 rounded-xl px-4 py-3 text-sm">
          <AlertCircle size={16} />{error}
          <button className="ml-auto btn-secondary" onClick={fetchQuotations}>Retry</button>
        </div>
      )}

      <div className="card overflow-hidden">
        <div className="overflow-x-auto">
          <table className="data-table">
            <thead>
              <tr>
                <th>Quotation No.</th><th>Status</th><th className="text-right">Items</th>
                <th>Created</th><th>Purchase Order</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr><td colSpan={5} className="text-center py-10 text-slate-400">
                  <Loader2 size={18} className="animate-spin inline-block mr-2" />Loading quotations…
                </td></tr>
              ) : quotations.length === 0 ? (
                <tr><td colSpan={5} className="text-center py-10 text-slate-400">
                  No quotations yet. Create one to get started.
                </td></tr>
              ) : quotations.map((q) => {
                const status = STATUS_LABELS[q.status] || STATUS_LABELS.draft
                return (
                  <tr key={q.id} className="cursor-pointer">
                    <td>
                      <Link to={`/materials/quotations/${q.id}`} className="flex items-center gap-2 font-semibold text-brand-600">
                        <FileText size={14} />{q.quotation_number}
                      </Link>
                    </td>
                    <td><span className={`badge text-xs ${status.className}`}>{status.label}</span></td>
                    <td className="text-right">{q.item_count}</td>
                    <td className="text-xs text-slate-500">{new Date(q.created_at).toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' })}</td>
                    <td className="text-xs text-slate-500">{q.po_number || '-'}</td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
