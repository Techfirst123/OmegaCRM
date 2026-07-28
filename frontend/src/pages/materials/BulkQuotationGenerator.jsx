import React, { useEffect, useMemo, useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  Upload, Plus, Trash2, Loader2, AlertCircle, CheckCircle2, PackageSearch, ShieldCheck,
} from 'lucide-react'

function getCookie(name) {
  const value = `; ${document.cookie}`
  const parts = value.split(`; ${name}=`)
  if (parts.length === 2) return parts.pop().split(';').shift()
  return ''
}

const CHECK_URL = '/procurement/purchase-orders/bulk-generate/check/'
const GENERATE_URL = '/procurement/api/bulk-generate/'
const VENDOR_OPTIONS_URL = '/procurement/api/vendors/'

const DIVISION_CHOICES = [
  { value: 'solar', label: 'Solar' },
  { value: 'biogas', label: 'Biogas' },
  { value: 'infrastructure', label: 'Infrastructure' },
  { value: 'pharma', label: 'Pharma' },
  { value: 'other', label: 'Other' },
]

const emptyRow = () => ({ material_name: '', unit: '', quantity: '' })

const Field = ({ label, required, children }) => (
  <div>
    <label className="block text-xs font-medium text-slate-600 mb-1">
      {label}{required && <span className="text-red-500 ml-0.5">*</span>}
    </label>
    {children}
  </div>
)

const Input = (props) => (
  <input
    {...props}
    className="w-full px-3 py-2 text-sm border border-surface-200 rounded-lg bg-white text-slate-800 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-brand-300 focus:border-brand-400 transition"
  />
)

const Select = ({ children, ...props }) => (
  <select
    {...props}
    className="w-full px-3 py-2 text-sm border border-surface-200 rounded-lg bg-white text-slate-800 focus:outline-none focus:ring-2 focus:ring-brand-300 focus:border-brand-400 transition"
  >
    {children}
  </select>
)

const Textarea = (props) => (
  <textarea
    {...props}
    className="w-full px-3 py-2 text-sm border border-surface-200 rounded-lg bg-white text-slate-800 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-brand-300 focus:border-brand-400 transition resize-none"
  />
)

export default function BulkQuotationGenerator() {
  const navigate = useNavigate()
  const fileInputRef = useRef(null)

  const [manualRows, setManualRows] = useState([emptyRow(), emptyRow(), emptyRow()])
  const [verifying, setVerifying] = useState(false)
  const [quotation, setQuotation] = useState(null) // { rows, all_matched }
  const [alert, setAlert] = useState(null)

  const [vendors, setVendors] = useState([])
  const [vendorsLoading, setVendorsLoading] = useState(true)

  const [poForm, setPoForm] = useState({
    po_number: '', po_date: new Date().toISOString().slice(0, 10), vendor: '',
    business_division: 'solar', project_site_name: '', project_location: '',
    delivery_address: '', dispatch_origin: '', department: '',
    payment_terms: '', delivery_terms: '', expected_delivery_date: '',
  })
  const [generating, setGenerating] = useState(false)
  const [generateError, setGenerateError] = useState('')
  const [success, setSuccess] = useState(null) // { po_number, item_count }

  useEffect(() => {
    fetch(VENDOR_OPTIONS_URL, { credentials: 'same-origin' })
      .then((res) => res.json())
      .then((data) => setVendors(data.results || []))
      .catch(() => setVendors([]))
      .finally(() => setVendorsLoading(false))
  }, [])

  const quotationTotal = useMemo(() => {
    if (!quotation) return 0
    return quotation.rows.reduce((sum, row) => sum + (row.amount ? parseFloat(row.amount) : 0), 0)
  }, [quotation])

  const setPoField = (key) => (e) => setPoForm((f) => ({ ...f, [key]: e.target.value }))

  const updateManualRow = (index, key, value) => {
    setManualRows((rows) => rows.map((row, i) => (i === index ? { ...row, [key]: value } : row)))
  }
  const addManualRow = () => setManualRows((rows) => [...rows, emptyRow()])
  const removeManualRow = (index) => setManualRows((rows) => rows.filter((_, i) => i !== index))

  const runVerify = async (body, isFormData) => {
    setVerifying(true)
    setAlert(null)
    try {
      const options = { method: 'POST', headers: { 'X-CSRFToken': getCookie('csrftoken') } }
      if (isFormData) {
        options.body = body
      } else {
        options.headers['Content-Type'] = 'application/json'
        options.body = JSON.stringify(body)
      }
      const res = await fetch(CHECK_URL, options)
      const data = await res.json().catch(() => ({}))
      if (!res.ok) throw new Error(data.error || 'Could not verify the product list against inventory.')
      setQuotation(data)
      const count = data.rows?.length || 0
      setAlert({
        type: data.all_matched ? 'success' : 'warning',
        message: data.all_matched
          ? `Verified ${count} product${count === 1 ? '' : 's'} — everything is available in inventory. You can generate the purchase order below.`
          : `Verified ${count} product${count === 1 ? '' : 's'} — some items don't match inventory. Fix the list and verify again.`,
      })
    } catch (err) {
      setAlert({ type: 'error', message: err.message })
    } finally {
      setVerifying(false)
    }
  }

  const handleVerifyManual = () => {
    const rows = manualRows.filter((r) => r.material_name || r.unit || r.quantity)
    if (!rows.length) {
      setAlert({ type: 'error', message: 'Add at least one product row first.' })
      return
    }
    runVerify({ rows })
  }

  const handleFileChange = (e) => {
    const file = e.target.files?.[0]
    e.target.value = ''
    if (!file) return
    if (!file.name.toLowerCase().endsWith('.xlsx')) {
      setAlert({ type: 'error', message: 'Please upload the product list in .xlsx format.' })
      return
    }
    const formData = new FormData()
    formData.append('materialFile', file)
    runVerify(formData, true)
  }

  const handleGenerate = async (e) => {
    e.preventDefault()
    if (!quotation?.all_matched) return
    setGenerating(true)
    setGenerateError('')
    try {
      const items = quotation.rows.map((r) => ({
        material_name: r.material_name, unit: r.unit, quantity: r.requested_qty,
      }))
      const payload = { ...poForm, status: 'draft', items }
      const res = await fetch(GENERATE_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCookie('csrftoken') },
        body: JSON.stringify(payload),
      })
      const data = await res.json().catch(() => ({}))
      if (!res.ok) {
        const fieldErrors = data.field_errors
          ? Object.entries(data.field_errors).map(([k, v]) => `${k}: ${v.map((e) => e.message || e).join(', ')}`).join(' | ')
          : ''
        throw new Error(data.error || fieldErrors || 'Could not generate the purchase order.')
      }
      setSuccess({ po_number: data.po_number, item_count: quotation.rows.length })
    } catch (err) {
      setGenerateError(err.message)
    } finally {
      setGenerating(false)
    }
  }

  const resetAll = () => {
    setManualRows([emptyRow(), emptyRow(), emptyRow()])
    setQuotation(null)
    setAlert(null)
    setGenerateError('')
    setSuccess(null)
    setPoForm({
      po_number: '', po_date: new Date().toISOString().slice(0, 10), vendor: '',
      business_division: 'solar', project_site_name: '', project_location: '',
      delivery_address: '', dispatch_origin: '', department: '',
      payment_terms: '', delivery_terms: '', expected_delivery_date: '',
    })
  }

  if (success) {
    return (
      <div className="space-y-6 pb-4">
        <div className="page-header">
          <div>
            <h2 className="page-title">Bulk Quotation Generator</h2>
            <p className="page-subtitle">Purchase order generated</p>
          </div>
        </div>
        <div className="card p-10 flex flex-col items-center text-center gap-3 max-w-lg mx-auto">
          <div className="w-14 h-14 rounded-full bg-emerald-50 border border-emerald-200 flex items-center justify-center">
            <CheckCircle2 size={28} className="text-emerald-500" />
          </div>
          <h3 className="text-lg font-bold text-slate-900">Purchase Order {success.po_number} generated</h3>
          <p className="text-sm text-slate-500">
            {success.item_count} verified item{success.item_count === 1 ? '' : 's'} added and deducted from inventory.
          </p>
          <div className="flex gap-2 mt-2">
            <button className="btn-primary" onClick={resetAll}>Build Another Quotation</button>
            <button className="btn-secondary" onClick={() => navigate('/materials')}>Back to Materials</button>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6 pb-4">
      <div className="page-header">
        <div>
          <h2 className="page-title">Bulk Quotation Generator</h2>
          <p className="page-subtitle">
            Build a quotation from your product list, verify it against inventory, then generate the purchase order.
          </p>
        </div>
      </div>

      {alert && (
        <div className={`flex items-center gap-2.5 rounded-xl px-4 py-3 text-sm border ${
          alert.type === 'error' ? 'bg-red-50 text-red-700 border-red-200'
            : alert.type === 'warning' ? 'bg-amber-50 text-amber-700 border-amber-200'
              : 'bg-emerald-50 text-emerald-700 border-emerald-200'
        }`}>
          {alert.type === 'error' ? <AlertCircle size={16} /> : <CheckCircle2 size={16} />}
          {alert.message}
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <div className="card p-4 space-y-3">
          <div className="flex items-center gap-2 font-semibold text-slate-800 text-sm">
            <Upload size={15} className="text-brand-500" /> Upload Excel List
          </div>
          <p className="text-xs text-slate-500">Required columns: Material Name, Unit, Quantity</p>
          <input ref={fileInputRef} type="file" accept=".xlsx" className="hidden" onChange={handleFileChange} />
          <button className="btn-primary w-full justify-center" disabled={verifying} onClick={() => fileInputRef.current?.click()}>
            {verifying ? <Loader2 size={14} className="animate-spin" /> : <ShieldCheck size={14} />}
            Verify File
          </button>
        </div>

        <div className="card p-4 space-y-3">
          <div className="flex items-center gap-2 font-semibold text-slate-800 text-sm">
            <PackageSearch size={15} className="text-brand-500" /> Enter Products Manually
          </div>
          <div className="space-y-2 max-h-48 overflow-y-auto pr-1">
            {manualRows.map((row, i) => (
              <div key={i} className="grid grid-cols-[1fr_90px_80px_28px] gap-1.5">
                <Input placeholder="Material name" value={row.material_name}
                  onChange={(e) => updateManualRow(i, 'material_name', e.target.value)} />
                <Input placeholder="Unit" value={row.unit}
                  onChange={(e) => updateManualRow(i, 'unit', e.target.value)} />
                <Input type="number" min="1" step="1" placeholder="Qty" value={row.quantity}
                  onChange={(e) => updateManualRow(i, 'quantity', e.target.value)} />
                <button type="button" className="text-slate-400 hover:text-red-500" onClick={() => removeManualRow(i)}>
                  <Trash2 size={14} />
                </button>
              </div>
            ))}
          </div>
          <div className="flex gap-2">
            <button type="button" className="btn-secondary text-xs" onClick={addManualRow}><Plus size={13} />Add Row</button>
            <button type="button" className="btn-primary text-xs ml-auto" disabled={verifying} onClick={handleVerifyManual}>
              {verifying ? <Loader2 size={13} className="animate-spin" /> : <ShieldCheck size={13} />}
              Verify List
            </button>
          </div>
        </div>
      </div>

      <div className="card overflow-hidden">
        <div className="p-4 border-b border-surface-100 flex items-center justify-between">
          <h3 className="font-semibold text-slate-800 text-sm">Quotation Details</h3>
          {quotation && (
            <span className={`badge text-xs ${quotation.all_matched ? 'bg-emerald-100 text-emerald-700' : 'bg-amber-100 text-amber-700'}`}>
              {quotation.all_matched ? 'Verified' : 'Needs Attention'}
            </span>
          )}
        </div>
        <div className="overflow-x-auto">
          <table className="data-table">
            <thead>
              <tr>
                <th>Material Name</th><th>Unit</th><th className="text-right">Requested</th>
                <th className="text-right">Available</th><th className="text-right">Rate</th>
                <th className="text-right">Amount</th><th>Status</th>
              </tr>
            </thead>
            <tbody>
              {!quotation || quotation.rows.length === 0 ? (
                <tr><td colSpan={7} className="text-center py-8 text-slate-400">No products verified yet.</td></tr>
              ) : quotation.rows.map((row, i) => (
                <tr key={i}>
                  <td className="font-medium text-slate-800">{row.material_name || '-'}</td>
                  <td className="text-xs text-slate-500">{row.unit || '-'}</td>
                  <td className="text-right">{row.requested_qty ?? '-'}</td>
                  <td className="text-right">{row.available_qty ?? '-'}</td>
                  <td className="text-right">{row.unit_rate ? `₹${row.unit_rate}` : '-'}</td>
                  <td className="text-right font-semibold text-slate-900">{row.amount ? `₹${row.amount}` : '-'}</td>
                  <td>
                    <span className={`badge text-xs ${row.matched ? 'bg-emerald-100 text-emerald-700' : 'bg-red-100 text-red-700'}`}>
                      {row.matched ? 'Matched' : 'Not Matched'}
                    </span>
                    <div className="text-xs text-slate-400 mt-0.5">{row.reason}</div>
                  </td>
                </tr>
              ))}
            </tbody>
            {quotation && quotation.rows.length > 0 && (
              <tfoot>
                <tr className="bg-surface-50">
                  <td colSpan={5} className="text-right font-semibold text-slate-600">Total Quotation Value</td>
                  <td className="text-right font-bold text-slate-900">
                    ₹{quotationTotal.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                  </td>
                  <td></td>
                </tr>
              </tfoot>
            )}
          </table>
        </div>
      </div>

      <div className="card p-5 space-y-4">
        <h3 className="font-semibold text-slate-800 text-sm">Generate Purchase Order</h3>
        <p className="text-xs text-slate-500">
          Fill in the PO header once the quotation above is fully Verified. The button stays disabled until every product matches inventory.
        </p>

        {generateError && (
          <div className="flex items-center gap-2 bg-red-50 text-red-700 border border-red-200 rounded-lg px-3 py-2 text-sm">
            <AlertCircle size={14} className="flex-shrink-0" />{generateError}
          </div>
        )}

        <form onSubmit={handleGenerate} className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <Field label="PO Number" required>
            <Input value={poForm.po_number} onChange={setPoField('po_number')} placeholder="e.g. PO-2026-014" required />
          </Field>
          <Field label="PO Date" required>
            <Input type="date" value={poForm.po_date} onChange={setPoField('po_date')} required />
          </Field>
          <Field label="Vendor" required>
            <Select value={poForm.vendor} onChange={setPoField('vendor')} required disabled={vendorsLoading}>
              <option value="">{vendorsLoading ? 'Loading vendors…' : 'Select vendor'}</option>
              {vendors.map((v) => (
                <option key={v.id} value={v.id}>{v.company_name} ({v.vendor_id})</option>
              ))}
            </Select>
          </Field>
          <Field label="Business Division" required>
            <Select value={poForm.business_division} onChange={setPoField('business_division')} required>
              {DIVISION_CHOICES.map((c) => <option key={c.value} value={c.value}>{c.label}</option>)}
            </Select>
          </Field>
          <Field label="Project / Site Name" required>
            <Input value={poForm.project_site_name} onChange={setPoField('project_site_name')} placeholder="e.g. KUSUM A&C 205 MW" required />
          </Field>
          <Field label="Project Location">
            <Input value={poForm.project_location} onChange={setPoField('project_location')} />
          </Field>
          <Field label="Dispatch Origin">
            <Input value={poForm.dispatch_origin} onChange={setPoField('dispatch_origin')} placeholder="From where material is coming" />
          </Field>
          <Field label="Department">
            <Input value={poForm.department} onChange={setPoField('department')} />
          </Field>
          <Field label="Expected Delivery Date">
            <Input type="date" value={poForm.expected_delivery_date} onChange={setPoField('expected_delivery_date')} />
          </Field>
          <div className="md:col-span-2">
            <Field label="Delivery Address">
              <Textarea rows={2} value={poForm.delivery_address} onChange={setPoField('delivery_address')} />
            </Field>
          </div>
          <Field label="Payment Terms">
            <Textarea rows={2} value={poForm.payment_terms} onChange={setPoField('payment_terms')} />
          </Field>
          <Field label="Delivery Terms">
            <Textarea rows={2} value={poForm.delivery_terms} onChange={setPoField('delivery_terms')} />
          </Field>

          <div className="md:col-span-2 flex justify-end">
            <button type="submit" className="btn-primary disabled:opacity-50" disabled={!quotation?.all_matched || generating}>
              {generating ? <Loader2 size={14} className="animate-spin" /> : <CheckCircle2 size={14} />}
              Generate Purchase Order
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
