import React, { useState } from 'react'
import { Link } from 'react-router-dom'
import { Search, CreditCard, CheckCircle, Clock, AlertTriangle, Download, Plus, Filter } from 'lucide-react'

const mockPayments = [
  { id:'PAY-2024-089-1', po:'PO-2024-089', vendor:'Tata Projects Ltd',   stage:'Advance (30%)',        amount:867000,  tds:8670,  net:858330, mode:'RTGS', status:'Paid',    date:'18 Jun 2024', ref:'RTGS20240618001' },
  { id:'PAY-2024-087-3', po:'PO-2024-087', vendor:'Siemens India',       stage:'Final (10%)',          amount:428000,  tds:4280,  net:423720, mode:'NEFT', status:'Pending', date:'30 Jun 2024', ref:'—'              },
  { id:'PAY-2024-086-2', po:'PO-2024-086', vendor:'ABB India Ltd',       stage:'On Delivery (40%)',    amount:384000,  tds:3840,  net:380160, mode:'NEFT', status:'Overdue', date:'18 Jun 2024', ref:'—'              },
  { id:'PAY-2024-085-4', po:'PO-2024-085', vendor:'Havells Infra',       stage:'Milestone (20%)',      amount:628000,  tds:6280,  net:621720, mode:'RTGS', status:'Paid',    date:'10 Jun 2024', ref:'RTGS20240610004' },
  { id:'PAY-2024-084-1', po:'PO-2024-084', vendor:'BHEL Heavy Equipment',stage:'Advance (30%)',        amount:2670000, tds:26700, net:2643300,mode:'RTGS', status:'Paid',    date:'5 Jun 2024',  ref:'RTGS20240605003' },
  { id:'PAY-2024-083-5', po:'PO-2024-083', vendor:'Sterling & Wilson',   stage:'Final (10%)',          amount:560000,  tds:5600,  net:554400, mode:'NEFT', status:'Pending', date:'1 Jul 2024',  ref:'—'              },
]

const statusBadge = { Paid:'badge-green', Pending:'badge-amber', Overdue:'badge-red' }

const fmt = (n) => '₹' + (n >= 1000000 ? (n/100000).toFixed(1)+'L' : (n/1000).toFixed(0)+'K')

export default function PaymentList() {
  const [search, setSearch] = useState('')
  const [statusFilter, setStatusFilter] = useState('All')

  const filtered = mockPayments.filter(p => {
    const q = search.toLowerCase()
    return (p.id.toLowerCase().includes(q) || p.vendor.toLowerCase().includes(q) || p.po.toLowerCase().includes(q))
      && (statusFilter === 'All' || p.status === statusFilter)
  })

  const totalPaid    = mockPayments.filter(p=>p.status==='Paid').reduce((s,p)=>s+p.net,0)
  const totalPending = mockPayments.filter(p=>p.status!=='Paid').reduce((s,p)=>s+p.net,0)

  return (
    <div className="space-y-6 pb-4">
      <div className="page-header">
        <div>
          <h2 className="page-title">Payments</h2>
          <p className="page-subtitle">Track all vendor payment stages and TDS deductions</p>
        </div>
        <div className="flex items-center gap-2">
          <button className="btn-secondary"><Download size={14} />Export</button>
          <button className="btn-primary"><Plus size={14} />Record Payment</button>
        </div>
      </div>

      {/* KPIs */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {[
          { label:'Total Paid (this month)',     value: fmt(totalPaid),    icon: CheckCircle,   cls:'text-emerald-600 bg-emerald-50 border-emerald-100' },
          { label:'Pending Payments',            value: fmt(totalPending), icon: Clock,         cls:'text-amber-600 bg-amber-50 border-amber-100'       },
          { label:'Overdue Payments',            value: '₹3.8L',           icon: AlertTriangle, cls:'text-red-600 bg-red-50 border-red-100'             },
        ].map(k => {
          const Icon = k.icon
          return (
            <div key={k.label} className={`card p-5 flex items-center gap-4 border ${k.cls}`}>
              <Icon size={24} />
              <div>
                <p className="text-xl font-bold text-slate-900">{k.value}</p>
                <p className="text-xs font-medium mt-0.5 opacity-80">{k.label}</p>
              </div>
            </div>
          )
        })}
      </div>

      {/* Filter bar */}
      <div className="card p-4 flex items-center gap-3 flex-wrap">
        <div className="flex items-center bg-surface-50 border border-surface-200 rounded-lg px-3 py-2 gap-2 flex-1 max-w-sm">
          <Search size={14} className="text-slate-400" />
          <input type="text" placeholder="Search payment ID, PO, vendor…"
            className="bg-transparent text-sm placeholder-slate-400 outline-none flex-1"
            value={search} onChange={e => setSearch(e.target.value)} />
        </div>
        <div className="flex gap-1.5">
          {['All', 'Paid', 'Pending', 'Overdue'].map(s => (
            <button key={s} onClick={() => setStatusFilter(s)}
              className={`px-3 py-1.5 text-xs font-semibold rounded-lg transition-colors ${statusFilter===s ? 'bg-brand-500 text-white shadow-sm' : 'bg-surface-50 text-slate-600 border border-surface-200 hover:bg-surface-100'}`}
            >
              {s}
            </button>
          ))}
        </div>
        <span className="ml-auto text-xs text-slate-400">{filtered.length} records</span>
      </div>

      {/* Table */}
      <div className="card overflow-hidden">
        <div className="overflow-x-auto">
          <table className="data-table">
            <thead>
              <tr>
                <th>Payment ID</th>
                <th>PO Reference</th>
                <th>Vendor</th>
                <th>Stage</th>
                <th className="text-right">Gross Amount</th>
                <th className="text-right">TDS</th>
                <th className="text-right">Net Payable</th>
                <th>Mode</th>
                <th>Status</th>
                <th>Due / Paid Date</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map(p => (
                <tr key={p.id}>
                  <td className="font-bold text-brand-600 text-xs whitespace-nowrap">{p.id}</td>
                  <td><Link to={`/purchase-orders/${p.po}`} className="text-xs text-brand-500 hover:underline font-medium">{p.po}</Link></td>
                  <td className="text-slate-700 max-w-[150px] truncate">{p.vendor}</td>
                  <td className="text-xs text-slate-500">{p.stage}</td>
                  <td className="text-right font-semibold text-slate-900">{fmt(p.amount)}</td>
                  <td className="text-right text-xs text-red-600">-{fmt(p.tds)}</td>
                  <td className="text-right font-bold text-slate-900">{fmt(p.net)}</td>
                  <td className="text-xs text-slate-500">{p.mode}</td>
                  <td><span className={`badge ${statusBadge[p.status]}`}>{p.status}</span></td>
                  <td className="text-xs text-slate-400 whitespace-nowrap">{p.date}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
