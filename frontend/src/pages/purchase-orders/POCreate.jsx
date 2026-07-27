import React, { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { ArrowLeft, Plus, Trash2, ShoppingCart, Building2, Package, CreditCard, Loader2, CheckCircle } from 'lucide-react'

const SECTIONS = ['Vendor & Project', 'Line Items', 'Payment & Terms', 'Review']

const vendors = [
  'Tata Projects Ltd', 'Larsen & Toubro Ltd', 'Siemens India Ltd',
  'ABB India Ltd', 'Havells Infra Pvt Ltd', 'BHEL Heavy Equipment',
  'Sterling & Wilson', 'Greentech Solar Pvt',
]

const Field = ({ label, required, children, className = '' }) => (
  <div className={className}>
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

const emptyItem = () => ({ description: '', unit: 'Nos', qty: '', rate: '', gst: '18' })

const fmt = (n) => isNaN(n) || n === 0 ? '—' : `₹${Number(n).toLocaleString('en-IN')}`

export default function POCreate() {
  const navigate = useNavigate()
  const [step, setStep] = useState(0)
  const [submitting, setSubmitting] = useState(false)
  const [success, setSuccess] = useState(false)
  const [error, setError] = useState('')

  const [form, setForm] = useState({
    vendor: '',
    project: '',
    workPackage: '',
    deliveryDate: '',
    paymentTerms: '30 days net',
    notes: '',
    advancePercent: '30',
  })

  const [items, setItems] = useState([emptyItem()])

  const setF = (k) => (e) => setForm(f => ({ ...f, [k]: e.target.value }))

  const setItem = (i, k) => (e) => {
    setItems(prev => {
      const next = [...prev]
      next[i] = { ...next[i], [k]: e.target.value }
      return next
    })
  }

  const addItem = () => setItems(prev => [...prev, emptyItem()])
  const removeItem = (i) => setItems(prev => prev.filter((_, idx) => idx !== i))

  const itemAmount = (item) => {
    const base = parseFloat(item.qty || 0) * parseFloat(item.rate || 0)
    return base
  }
  const itemGstAmt = (item) => itemAmount(item) * parseFloat(item.gst || 0) / 100
  const subTotal = items.reduce((s, it) => s + itemAmount(it), 0)
  const totalGst = items.reduce((s, it) => s + itemGstAmt(it), 0)
  const grandTotal = subTotal + totalGst

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!form.vendor || !form.project || !form.deliveryDate) {
      setError('Please fill all required fields.')
      setStep(0)
      return
    }
    if (items.some(it => !it.description || !it.qty || !it.rate)) {
      setError('Each line item needs description, quantity, and rate.')
      setStep(1)
      return
    }
    setError('')
    setSubmitting(true)
    // Simulate API call (replace with real endpoint when backend PO API is ready)
    await new Promise(r => setTimeout(r, 1200))
    setSubmitting(false)
    setSuccess(true)
    setTimeout(() => navigate('/purchase-orders'), 2000)
  }

  const sectionIcons = [Building2, Package, CreditCard, ShoppingCart]

  if (success) {
    return (
      <div className="max-w-xl mx-auto mt-20 text-center space-y-4">
        <div className="w-16 h-16 bg-emerald-50 rounded-2xl flex items-center justify-center mx-auto">
          <CheckCircle size={32} className="text-emerald-500" />
        </div>
        <h2 className="text-xl font-bold text-slate-900">Purchase Order Created</h2>
        <p className="text-slate-500 text-sm">Redirecting to Purchase Orders…</p>
      </div>
    )
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6 pb-8">
      {/* Header */}
      <div>
        <Link to="/purchase-orders" className="inline-flex items-center gap-1.5 text-sm text-slate-500 hover:text-slate-700 mb-4 transition-colors">
          <ArrowLeft size={15} />Back to Purchase Orders
        </Link>
        <h2 className="text-xl font-bold text-slate-900">Create Purchase Order</h2>
        <p className="text-slate-500 text-sm mt-0.5">Fill all sections, then review before submitting</p>
      </div>

      {/* Step tabs */}
      <div className="flex gap-2 flex-wrap">
        {SECTIONS.map((s, i) => {
          const Icon = sectionIcons[i]
          return (
            <button key={s} onClick={() => setStep(i)}
              className={`flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-medium border transition-all ${
                step === i
                  ? 'bg-brand-500 text-white border-brand-500 shadow-sm'
                  : 'bg-white text-slate-600 border-surface-200 hover:border-brand-300'
              }`}
            >
              <Icon size={14} />{s}
            </button>
          )
        })}
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 text-sm rounded-xl px-4 py-3">{error}</div>
      )}

      <form onSubmit={handleSubmit}>
        {/* Step 0 — Vendor & Project */}
        {step === 0 && (
          <div className="card p-6 space-y-4">
            <h3 className="font-semibold text-slate-900 text-sm border-b border-surface-100 pb-3">Vendor & Project Details</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <Field label="Vendor" required>
                <Select value={form.vendor} onChange={setF('vendor')} required>
                  <option value="">Select vendor</option>
                  {vendors.map(v => <option key={v} value={v}>{v}</option>)}
                </Select>
              </Field>
              <Field label="Project / Site" required>
                <Input placeholder="e.g. Solar Farm Alpha" value={form.project} onChange={setF('project')} required />
              </Field>
              <Field label="Work Package">
                <Input placeholder="e.g. Electrical Civil Works" value={form.workPackage} onChange={setF('workPackage')} />
              </Field>
              <Field label="Expected Delivery Date" required>
                <Input type="date" value={form.deliveryDate} onChange={setF('deliveryDate')} required />
              </Field>
              <Field label="Notes / Scope" className="md:col-span-2">
                <Textarea rows={3} placeholder="Any special instructions or scope notes…" value={form.notes} onChange={setF('notes')} />
              </Field>
            </div>
            <div className="flex justify-end pt-2">
              <button type="button" onClick={() => setStep(1)} className="btn-primary">Next: Line Items →</button>
            </div>
          </div>
        )}

        {/* Step 1 — Line Items */}
        {step === 1 && (
          <div className="card p-6 space-y-4">
            <h3 className="font-semibold text-slate-900 text-sm border-b border-surface-100 pb-3">Line Items</h3>

            <div className="space-y-3">
              {items.map((item, i) => (
                <div key={i} className="bg-surface-50 border border-surface-200 rounded-xl p-4">
                  <div className="flex items-center justify-between mb-3">
                    <span className="text-xs font-semibold text-slate-500">Item {i + 1}</span>
                    {items.length > 1 && (
                      <button type="button" onClick={() => removeItem(i)}
                        className="text-red-400 hover:text-red-600 transition-colors">
                        <Trash2 size={14} />
                      </button>
                    )}
                  </div>
                  <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
                    <div className="col-span-2">
                      <Field label="Description" required>
                        <Input placeholder="Item / service description" value={item.description} onChange={setItem(i, 'description')} required />
                      </Field>
                    </div>
                    <Field label="Unit">
                      <Select value={item.unit} onChange={setItem(i, 'unit')}>
                        <option value="Nos">Nos</option>
                        <option value="Mtrs">Mtrs</option>
                        <option value="Kgs">Kgs</option>
                        <option value="LS">LS</option>
                        <option value="Set">Set</option>
                        <option value="Sqft">Sqft</option>
                      </Select>
                    </Field>
                    <Field label="Qty" required>
                      <Input type="number" min="0" step="any" placeholder="0" value={item.qty} onChange={setItem(i, 'qty')} required />
                    </Field>
                    <Field label="Rate (₹)" required>
                      <Input type="number" min="0" step="any" placeholder="0.00" value={item.rate} onChange={setItem(i, 'rate')} required />
                    </Field>
                    <Field label="GST %">
                      <Select value={item.gst} onChange={setItem(i, 'gst')}>
                        <option value="0">0%</option>
                        <option value="5">5%</option>
                        <option value="12">12%</option>
                        <option value="18">18%</option>
                        <option value="28">28%</option>
                      </Select>
                    </Field>
                    <div className="col-span-2 md:col-span-4 flex items-end">
                      <p className="text-xs text-slate-500">
                        Amount: <span className="font-semibold text-slate-800">{fmt(itemAmount(item))}</span>
                        {' '}+ GST: <span className="font-semibold text-slate-800">{fmt(itemGstAmt(item))}</span>
                        {' '}= <span className="font-bold text-brand-600">{fmt(itemAmount(item) + itemGstAmt(item))}</span>
                      </p>
                    </div>
                  </div>
                </div>
              ))}
            </div>

            <button type="button" onClick={addItem}
              className="w-full py-3 border-2 border-dashed border-surface-300 rounded-xl text-sm text-slate-500 hover:border-brand-300 hover:text-brand-500 transition-colors flex items-center justify-center gap-2">
              <Plus size={14} />Add Line Item
            </button>

            {/* Totals */}
            <div className="bg-brand-50 border border-brand-100 rounded-xl p-4 ml-auto max-w-xs">
              <div className="space-y-2 text-sm">
                <div className="flex justify-between"><span className="text-slate-600">Sub-Total</span><span className="font-semibold">{fmt(subTotal)}</span></div>
                <div className="flex justify-between"><span className="text-slate-600">GST</span><span className="font-semibold">{fmt(totalGst)}</span></div>
                <div className="flex justify-between border-t border-brand-200 pt-2 mt-2">
                  <span className="font-bold text-slate-900">Grand Total</span>
                  <span className="font-bold text-brand-600 text-base">{fmt(grandTotal)}</span>
                </div>
              </div>
            </div>

            <div className="flex justify-between pt-2">
              <button type="button" onClick={() => setStep(0)} className="btn-secondary">← Back</button>
              <button type="button" onClick={() => setStep(2)} className="btn-primary">Next: Payment →</button>
            </div>
          </div>
        )}

        {/* Step 2 — Payment & Terms */}
        {step === 2 && (
          <div className="card p-6 space-y-4">
            <h3 className="font-semibold text-slate-900 text-sm border-b border-surface-100 pb-3">Payment & Terms</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <Field label="Payment Terms">
                <Select value={form.paymentTerms} onChange={setF('paymentTerms')}>
                  <option value="Immediate">Immediate</option>
                  <option value="15 days net">15 days net</option>
                  <option value="30 days net">30 days net</option>
                  <option value="45 days net">45 days net</option>
                  <option value="60 days net">60 days net</option>
                  <option value="Against delivery">Against delivery</option>
                  <option value="Milestone-based">Milestone-based</option>
                </Select>
              </Field>
              <Field label="Advance Payment (%)">
                <Select value={form.advancePercent} onChange={setF('advancePercent')}>
                  <option value="0">No Advance</option>
                  <option value="10">10%</option>
                  <option value="20">20%</option>
                  <option value="25">25%</option>
                  <option value="30">30%</option>
                  <option value="40">40%</option>
                  <option value="50">50%</option>
                </Select>
              </Field>
            </div>
            {grandTotal > 0 && (
              <div className="bg-surface-50 border border-surface-200 rounded-xl p-4">
                <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-3">Estimated Payment Schedule</p>
                <div className="space-y-2 text-sm">
                  {[
                    { label: `Advance (${form.advancePercent}%)`, pct: parseFloat(form.advancePercent) },
                    { label: 'On Delivery (remaining)', pct: 100 - parseFloat(form.advancePercent) },
                  ].map((s, i) => (
                    <div key={i} className="flex justify-between">
                      <span className="text-slate-600">{s.label}</span>
                      <span className="font-semibold text-slate-900">{fmt(grandTotal * s.pct / 100)}</span>
                    </div>
                  ))}
                  <div className="flex justify-between border-t border-surface-200 pt-2 font-bold">
                    <span>Total</span>
                    <span className="text-brand-600">{fmt(grandTotal)}</span>
                  </div>
                </div>
              </div>
            )}
            <div className="flex justify-between pt-2">
              <button type="button" onClick={() => setStep(1)} className="btn-secondary">← Back</button>
              <button type="button" onClick={() => setStep(3)} className="btn-primary">Review →</button>
            </div>
          </div>
        )}

        {/* Step 3 — Review */}
        {step === 3 && (
          <div className="space-y-4">
            <div className="card p-5">
              <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-3">Vendor & Project</p>
              <div className="grid grid-cols-2 gap-3 text-sm">
                {[
                  { l: 'Vendor', v: form.vendor || '—' },
                  { l: 'Project', v: form.project || '—' },
                  { l: 'Work Package', v: form.workPackage || '—' },
                  { l: 'Delivery Date', v: form.deliveryDate || '—' },
                  { l: 'Payment Terms', v: form.paymentTerms },
                  { l: 'Advance', v: `${form.advancePercent}%` },
                ].map(r => (
                  <div key={r.l} className="flex flex-col">
                    <span className="text-xs text-slate-400">{r.l}</span>
                    <span className="font-medium text-slate-800">{r.v}</span>
                  </div>
                ))}
              </div>
            </div>

            <div className="card overflow-hidden">
              <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider px-5 py-3 border-b border-surface-100">Line Items</p>
              <table className="data-table">
                <thead><tr><th>#</th><th>Description</th><th>Unit</th><th className="text-right">Qty</th><th className="text-right">Rate</th><th className="text-center">GST</th><th className="text-right">Amount</th></tr></thead>
                <tbody>
                  {items.map((it, i) => (
                    <tr key={i}>
                      <td className="text-slate-400">{i + 1}</td>
                      <td className="font-medium text-slate-800">{it.description || '—'}</td>
                      <td className="text-slate-500">{it.unit}</td>
                      <td className="text-right text-slate-700">{it.qty || 0}</td>
                      <td className="text-right text-slate-700">{it.rate ? `₹${Number(it.rate).toLocaleString()}` : '—'}</td>
                      <td className="text-center text-slate-500">{it.gst}%</td>
                      <td className="text-right font-semibold text-slate-900">{fmt(itemAmount(it) + itemGstAmt(it))}</td>
                    </tr>
                  ))}
                </tbody>
                <tfoot>
                  <tr className="bg-brand-50">
                    <td colSpan={6} className="px-4 py-3 text-right text-sm font-bold text-slate-700">Grand Total (incl. GST)</td>
                    <td className="px-4 py-3 text-right font-bold text-brand-600">{fmt(grandTotal)}</td>
                  </tr>
                </tfoot>
              </table>
            </div>

            <div className="flex justify-between pt-2">
              <button type="button" onClick={() => setStep(2)} className="btn-secondary">← Back</button>
              <button type="submit" disabled={submitting}
                className="btn-primary min-w-[180px] flex items-center justify-center gap-2">
                {submitting
                  ? <><Loader2 size={15} className="animate-spin" />Creating PO…</>
                  : <><ShoppingCart size={15} />Create Purchase Order</>
                }
              </button>
            </div>
          </div>
        )}
      </form>
    </div>
  )
}
