import React, { useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { ArrowLeft, Download, Edit, CheckCircle, Clock, Circle, Truck, CreditCard, Package, FileText } from 'lucide-react'

const po = {
  id: 'PO-2024-089', date: '15 Jun 2024', status: 'Active',
  vendor: { id:1, name:'Tata Projects Ltd', code:'VND-001', contact:'+91 22 6745 9000', email:'procurement@tataprojects.com' },
  project: 'Solar Farm Alpha', workPackage: 'Electrical Civil Works',
  deliveryDate: '30 Jun 2024', paymentTerms: '30 days net',
  totalValue: 2450000, gst: 441000, grandTotal: 2891000,
  items: [
    { no:1, name:'Solar PV Module 540W',    unit:'Nos',  qty:200, rate:8500,   gst:12, amount:1700000 },
    { no:2, name:'Inverter 100kW',           unit:'Nos',  qty:2,   rate:185000, gst:18, amount:370000  },
    { no:3, name:'DC Cable 4mm² (Red)',      unit:'Mtrs', qty:1500, rate:85,    gst:18, amount:127500  },
    { no:4, name:'AC Distribution Panel',   unit:'Nos',  qty:1,   rate:125000, gst:18, amount:125000  },
    { no:5, name:'Earthing Kit',             unit:'Set',  qty:4,   rate:7000,  gst:18, amount:28000   },
    { no:6, name:'Installation Labour',      unit:'LS',   qty:1,   rate:99500, gst:18, amount:99500   },
  ],
  paymentStages: [
    { stage:'Advance (30%)',       due:'₹8.67L',  paid:'₹8.67L', date:'18 Jun 2024', status:'done'    },
    { stage:'On Delivery (40%)',   due:'₹11.56L', paid:'—',       date:'30 Jun 2024', status:'pending' },
    { stage:'After Inspection (20%)', due:'₹5.78L', paid:'—',    date:'15 Jul 2024', status:'pending' },
    { stage:'Final (10%)',         due:'₹2.89L',  paid:'—',       date:'30 Jul 2024', status:'pending' },
  ],
  deliveries: [
    { ref:'DEL-001', items:'Solar PV Module 540W x 100', date:'22 Jun 2024', status:'In Transit', qc:'Pending' },
  ],
  docs: [
    { name:'PO Document',         type:'PO',      date:'15 Jun 2024' },
    { name:'Advance Payment Proof',type:'Payment', date:'18 Jun 2024' },
  ],
}

const fmt = (n) => '₹' + (n/100000).toFixed(2) + 'L'

const TABS = ['Items', 'Deliveries', 'Payments', 'Documents']

export default function PODetail() {
  const { id } = useParams()
  const [tab, setTab] = useState('Items')

  return (
    <div className="space-y-6 pb-4">
      {/* Back */}
      <Link to="/purchase-orders" className="inline-flex items-center gap-1.5 text-sm text-slate-500 hover:text-slate-700 transition-colors">
        <ArrowLeft size={15} />Back to Purchase Orders
      </Link>

      {/* PO Header card */}
      <div className="card p-6">
        <div className="flex items-start justify-between gap-4 mb-6">
          <div>
            <div className="flex items-center gap-3 mb-2">
              <h2 className="text-xl font-bold text-slate-900">{po.id}</h2>
              <span className="badge badge-blue">{po.status}</span>
            </div>
            <p className="text-slate-500 text-sm">Issued on {po.date} · {po.project}</p>
          </div>
          <div className="flex items-center gap-2">
            <button className="btn-secondary"><Download size={14} />Download PDF</button>
            <button className="btn-secondary"><Edit size={14} />Edit</button>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* Vendor */}
          <div>
            <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">Vendor</p>
            <Link to={`/vendors/${po.vendor.id}`} className="font-semibold text-brand-600 hover:text-brand-700 text-sm">{po.vendor.name}</Link>
            <p className="text-xs text-slate-400 mt-0.5">{po.vendor.code}</p>
            <p className="text-xs text-slate-500 mt-1">{po.vendor.contact}</p>
            <p className="text-xs text-slate-500">{po.vendor.email}</p>
          </div>

          {/* PO details */}
          <div>
            <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">Details</p>
            <dl className="space-y-1.5">
              {[
                { l:'Project',       v: po.project      },
                { l:'Work Package',  v: po.workPackage   },
                { l:'Delivery Date', v: po.deliveryDate  },
                { l:'Payment Terms', v: po.paymentTerms  },
              ].map(r => (
                <div key={r.l} className="flex items-center gap-2 text-xs">
                  <dt className="text-slate-400 w-24 flex-shrink-0">{r.l}</dt>
                  <dd className="text-slate-700 font-medium">{r.v}</dd>
                </div>
              ))}
            </dl>
          </div>

          {/* Value summary */}
          <div className="bg-brand-50 border border-brand-100 rounded-xl p-4">
            <p className="text-xs font-semibold text-brand-700 uppercase tracking-wider mb-3">Value Summary</p>
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span className="text-slate-600">Sub-Total</span>
                <span className="font-semibold text-slate-900">{fmt(po.totalValue)}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-slate-600">GST (blended)</span>
                <span className="font-semibold text-slate-900">{fmt(po.gst)}</span>
              </div>
              <div className="flex justify-between text-sm border-t border-brand-200 pt-2 mt-2">
                <span className="font-bold text-slate-900">Grand Total</span>
                <span className="font-bold text-brand-600 text-base">{fmt(po.grandTotal)}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="border-b border-surface-200">
        <div className="flex">
          {TABS.map(t => (
            <button key={t} onClick={() => setTab(t)}
              className={`px-5 py-3 text-sm font-medium border-b-2 transition-colors ${
                tab === t ? 'border-brand-500 text-brand-600' : 'border-transparent text-slate-500 hover:text-slate-700'
              }`}
            >
              {t}
            </button>
          ))}
        </div>
      </div>

      {tab === 'Items' && (
        <div className="card overflow-hidden">
          <div className="overflow-x-auto">
            <table className="data-table">
              <thead>
                <tr>
                  <th>#</th>
                  <th>Item Description</th>
                  <th>Unit</th>
                  <th className="text-right">Qty</th>
                  <th className="text-right">Rate (₹)</th>
                  <th className="text-center">GST %</th>
                  <th className="text-right">Amount (₹)</th>
                </tr>
              </thead>
              <tbody>
                {po.items.map(item => (
                  <tr key={item.no}>
                    <td className="text-xs text-slate-400">{item.no}</td>
                    <td className="font-medium text-slate-800">{item.name}</td>
                    <td className="text-xs text-slate-500">{item.unit}</td>
                    <td className="text-right text-slate-700">{item.qty.toLocaleString()}</td>
                    <td className="text-right text-slate-700">{item.rate.toLocaleString()}</td>
                    <td className="text-center text-xs text-slate-500">{item.gst}%</td>
                    <td className="text-right font-semibold text-slate-900">{item.amount.toLocaleString()}</td>
                  </tr>
                ))}
              </tbody>
              <tfoot>
                <tr className="bg-surface-50">
                  <td colSpan={6} className="px-4 py-3 text-right text-sm font-bold text-slate-700">Grand Total (incl. GST)</td>
                  <td className="px-4 py-3 text-right text-base font-bold text-brand-600">₹{po.grandTotal.toLocaleString()}</td>
                </tr>
              </tfoot>
            </table>
          </div>
        </div>
      )}

      {tab === 'Deliveries' && (
        <div className="card overflow-hidden">
          <table className="data-table">
            <thead><tr><th>Ref</th><th>Items</th><th>Expected Date</th><th>Status</th><th>QC</th></tr></thead>
            <tbody>
              {po.deliveries.map(d => (
                <tr key={d.ref}>
                  <td className="font-semibold text-brand-600">{d.ref}</td>
                  <td className="text-slate-600 text-xs max-w-[200px] truncate">{d.items}</td>
                  <td className="text-xs text-slate-400">{d.date}</td>
                  <td><span className="badge badge-amber">{d.status}</span></td>
                  <td><span className="badge badge-slate">{d.qc}</span></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {tab === 'Payments' && (
        <div className="space-y-3">
          {po.paymentStages.map((s, i) => (
            <div key={i} className="card p-4 flex items-center gap-4">
              <div className={`w-9 h-9 rounded-xl flex items-center justify-center flex-shrink-0 ${s.status === 'done' ? 'bg-emerald-50 text-emerald-600' : 'bg-surface-100 text-slate-400'}`}>
                {s.status === 'done' ? <CheckCircle size={18} /> : <Clock size={18} />}
              </div>
              <div className="flex-1">
                <p className="text-sm font-semibold text-slate-900">{s.stage}</p>
                <p className="text-xs text-slate-400 mt-0.5">Due {s.date}</p>
              </div>
              <div className="text-right">
                <p className="text-sm font-bold text-slate-900">{s.due}</p>
                <p className={`text-xs mt-0.5 ${s.status === 'done' ? 'text-emerald-600 font-semibold' : 'text-slate-400'}`}>
                  Paid: {s.paid}
                </p>
              </div>
            </div>
          ))}
        </div>
      )}

      {tab === 'Documents' && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {po.docs.map((d, i) => (
            <div key={i} className="card p-4 flex items-center gap-3 cursor-pointer hover:shadow-card-hover transition-all">
              <div className="w-10 h-10 rounded-xl bg-brand-50 border border-brand-100 flex items-center justify-center flex-shrink-0">
                <FileText size={18} className="text-brand-500" />
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-slate-900 truncate">{d.name}</p>
                <p className="text-xs text-slate-400 mt-0.5">{d.type} · {d.date}</p>
              </div>
              <Download size={15} className="text-slate-400 flex-shrink-0" />
            </div>
          ))}
          <button className="card p-4 flex items-center justify-center gap-2 text-sm text-brand-500 hover:text-brand-600 hover:shadow-card-hover transition-all border-dashed">
            <FileText size={16} />Upload Document
          </button>
        </div>
      )}
    </div>
  )
}
