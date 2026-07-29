import React, { useEffect, useMemo, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { ArrowLeft, Download, Loader2, AlertCircle, Zap } from 'lucide-react'

const detailUrl = (id) => `/procurement/api/quotations/${id}/`
const pdfUrl = (id) => `/procurement/api/quotations/${id}/pdf/`

const STATUS_LABELS = {
  draft: 'Draft',
  verified: 'Verified',
  converted: 'Converted to PO',
}

export default function QuotationPreview() {
  const { id } = useParams()
  const [quotation, setQuotation] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    setLoading(true)
    setError('')
    fetch(detailUrl(id), { credentials: 'same-origin' })
      .then((res) => res.json().then((data) => ({ ok: res.ok, data })))
      .then(({ ok, data }) => {
        if (!ok) throw new Error(data.error || 'Could not load this quotation.')
        setQuotation(data.quotation)
      })
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false))
  }, [id])

  const total = useMemo(() => {
    if (!quotation) return 0
    return quotation.rows.reduce((sum, row) => sum + (row.amount ? parseFloat(row.amount) : 0), 0)
  }, [quotation])

  if (loading) {
    return <div className="py-16 text-center text-slate-400"><Loader2 size={20} className="animate-spin inline-block mr-2" />Loading preview…</div>
  }
  if (error) {
    return (
      <div className="flex items-center gap-2.5 bg-red-50 text-red-700 border border-red-200 rounded-xl px-4 py-3 text-sm">
        <AlertCircle size={16} />{error}
      </div>
    )
  }

  return (
    <div className="space-y-4 pb-10">
      <div className="flex items-center justify-between print:hidden">
        <Link to={`/materials/quotations/${id}`} className="text-sm text-slate-500 flex items-center gap-1 hover:text-slate-700">
          <ArrowLeft size={14} />Back to Quotation
        </Link>
        <a className="btn-primary" href={pdfUrl(id)} target="_blank" rel="noreferrer">
          <Download size={14} />Download PDF
        </a>
      </div>

      <div className="card p-10 max-w-3xl mx-auto bg-white">
        <div className="flex items-center gap-3 mb-1">
          <div className="w-9 h-9 bg-brand-500 rounded-xl flex items-center justify-center">
            <Zap size={18} className="text-white" />
          </div>
          <span className="text-xl font-bold text-slate-900">OmegaERP</span>
        </div>
        <h2 className="text-lg font-semibold text-slate-700 mb-6">Material Quotation</h2>

        <div className="grid grid-cols-3 gap-4 text-sm text-slate-600 mb-6">
          <div><span className="text-slate-400">Quotation No.</span><div className="font-semibold text-slate-800">{quotation.quotation_number}</div></div>
          <div><span className="text-slate-400">Date</span><div className="font-semibold text-slate-800">{new Date(quotation.created_at).toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' })}</div></div>
          <div><span className="text-slate-400">Status</span><div className="font-semibold text-slate-800">{STATUS_LABELS[quotation.status] || quotation.status}</div></div>
        </div>

        <div className="grid grid-cols-2 gap-8 mb-8">
          <div>
            <div className="text-xs font-bold text-slate-500 uppercase mb-1">From</div>
            <p className="text-sm font-medium text-slate-800">{quotation.sender_name || '—'}</p>
            {quotation.sender_address && <p className="text-sm text-slate-500 whitespace-pre-line">{quotation.sender_address}</p>}
            {quotation.sender_mobile && <p className="text-sm text-slate-500">Mobile: {quotation.sender_mobile}</p>}
          </div>
          <div>
            <div className="text-xs font-bold text-slate-500 uppercase mb-1">To</div>
            <p className="text-sm font-medium text-slate-800">{quotation.client_name || '—'}</p>
            {quotation.client_address && <p className="text-sm text-slate-500 whitespace-pre-line">{quotation.client_address}</p>}
            {quotation.client_mobile && <p className="text-sm text-slate-500">Mobile: {quotation.client_mobile}</p>}
          </div>
        </div>

        <table className="w-full text-sm border-collapse">
          <thead>
            <tr className="bg-slate-800 text-white">
              <th className="text-left px-3 py-2 rounded-l-lg">Material Name</th>
              <th className="text-left px-3 py-2">Unit</th>
              <th className="text-right px-3 py-2">Qty</th>
              <th className="text-right px-3 py-2">Available</th>
              <th className="text-right px-3 py-2">Rate (₹)</th>
              <th className="text-right px-3 py-2 rounded-r-lg">Amount (₹)</th>
            </tr>
          </thead>
          <tbody>
            {quotation.rows.map((row, i) => (
              <tr key={i} className="border-b border-surface-100">
                <td className="px-3 py-2 text-slate-800">{row.material_name || '-'}</td>
                <td className="px-3 py-2 text-slate-500">{row.unit || '-'}</td>
                <td className="px-3 py-2 text-right">{row.requested_qty ?? '-'}</td>
                <td className="px-3 py-2 text-right">{row.available_qty ?? '-'}</td>
                <td className="px-3 py-2 text-right">{row.unit_rate || '-'}</td>
                <td className="px-3 py-2 text-right font-medium">{row.amount || '-'}</td>
              </tr>
            ))}
          </tbody>
          <tfoot>
            <tr>
              <td colSpan={5} className="px-3 py-3 text-right font-semibold text-slate-600">Total</td>
              <td className="px-3 py-3 text-right font-bold text-slate-900">
                ₹{total.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
              </td>
            </tr>
          </tfoot>
        </table>
      </div>
    </div>
  )
}
