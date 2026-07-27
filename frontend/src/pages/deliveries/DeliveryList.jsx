import React, { useState } from 'react'
import { Link } from 'react-router-dom'
import { Search, Truck, CheckCircle, Clock, AlertTriangle, MapPin, Filter } from 'lucide-react'

const mockDeliveries = [
  { id:'DEL-2024-045', po:'PO-2024-089', vendor:'Tata Projects Ltd',   items:'Solar PV Module x 100',         date:'22 Jun 2024', status:'In Transit',     qc:'Pending',  driver:'Ramesh K.', vehicle:'MH-12-AB-3456' },
  { id:'DEL-2024-044', po:'PO-2024-088', vendor:'Larsen & Toubro',     items:'Inverter 100kW x 2',            date:'20 Jun 2024', status:'Dispatched',     qc:'—',        driver:'Suresh M.', vehicle:'KA-09-CD-7890' },
  { id:'DEL-2024-043', po:'PO-2024-087', vendor:'Siemens India',       items:'HV Switchgear x 1',             date:'18 Jun 2024', status:'Delivered',      qc:'Passed',   driver:'Arun P.',   vehicle:'MH-14-EF-1234' },
  { id:'DEL-2024-042', po:'PO-2024-086', vendor:'ABB India Ltd',       items:'Control Panel x 2',             date:'16 Jun 2024', status:'Quality Check',  qc:'In Review', driver:'Vijay S.', vehicle:'DL-01-GH-5678' },
  { id:'DEL-2024-041', po:'PO-2024-085', vendor:'Havells Infra',       items:'Cable Tray 200m',               date:'12 Jun 2024', status:'Delivered',      qc:'Passed',   driver:'Ravi T.',   vehicle:'MH-04-IJ-9012' },
  { id:'DEL-2024-040', po:'PO-2024-084', vendor:'BHEL Heavy Equipment',items:'Transformer 2MVA x 1',          date:'8 Jun 2024',  status:'Overdue',        qc:'—',        driver:'—',         vehicle:'—'             },
]

const statusIcon = {
  Dispatched:    { icon: Truck,         cls: 'text-blue-600 bg-blue-50'    },
  'In Transit':  { icon: Truck,         cls: 'text-amber-600 bg-amber-50'  },
  'Quality Check':{ icon: Clock,        cls: 'text-violet-600 bg-violet-50'},
  Delivered:     { icon: CheckCircle,   cls: 'text-emerald-600 bg-emerald-50'},
  Overdue:       { icon: AlertTriangle, cls: 'text-red-600 bg-red-50'      },
}

const statusBadge = {
  Dispatched:    'badge-blue',
  'In Transit':  'badge-amber',
  'Quality Check':'badge-violet',
  Delivered:     'badge-green',
  Overdue:       'badge-red',
}

const qcBadge = { Passed:'badge-green', 'In Review':'badge-amber', Pending:'badge-slate', '—':'badge-slate' }

export default function DeliveryList() {
  const [search, setSearch] = useState('')
  const [statusFilter, setStatusFilter] = useState('All')

  const filtered = mockDeliveries.filter(d => {
    const q = search.toLowerCase()
    return (d.id.toLowerCase().includes(q) || d.vendor.toLowerCase().includes(q) || d.po.toLowerCase().includes(q))
      && (statusFilter === 'All' || d.status === statusFilter)
  })

  return (
    <div className="space-y-6 pb-4">
      <div className="page-header">
        <div>
          <h2 className="page-title">Deliveries</h2>
          <p className="page-subtitle">{mockDeliveries.length} total · {mockDeliveries.filter(d=>d.status==='Overdue').length} overdue</p>
        </div>
      </div>

      {/* Status strip */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
        {[
          { k:'All',           count: mockDeliveries.length,                                               bg:'bg-slate-100',   text:'text-slate-700'   },
          { k:'Dispatched',    count: mockDeliveries.filter(d=>d.status==='Dispatched').length,            bg:'bg-blue-100',    text:'text-blue-700'    },
          { k:'In Transit',    count: mockDeliveries.filter(d=>d.status==='In Transit').length,            bg:'bg-amber-100',   text:'text-amber-700'   },
          { k:'Quality Check', count: mockDeliveries.filter(d=>d.status==='Quality Check').length,         bg:'bg-violet-100',  text:'text-violet-700'  },
          { k:'Overdue',       count: mockDeliveries.filter(d=>d.status==='Overdue').length,               bg:'bg-red-100',     text:'text-red-700'     },
        ].map(s => (
          <button key={s.k} onClick={() => setStatusFilter(s.k)}
            className={`${s.bg} ${s.text} rounded-xl p-4 text-left transition-all ${statusFilter===s.k?'ring-2 ring-offset-1 ring-slate-400/40 shadow-sm':''}`}
          >
            <p className="text-2xl font-bold">{s.count}</p>
            <p className="text-xs font-semibold mt-0.5">{s.k}</p>
          </button>
        ))}
      </div>

      {/* Filter bar */}
      <div className="card p-4 flex items-center gap-3">
        <div className="flex items-center bg-surface-50 border border-surface-200 rounded-lg px-3 py-2 gap-2 flex-1 max-w-sm">
          <Search size={14} className="text-slate-400" />
          <input type="text" placeholder="Search delivery ID, PO, vendor…"
            className="bg-transparent text-sm placeholder-slate-400 outline-none flex-1"
            value={search} onChange={e => setSearch(e.target.value)} />
        </div>
        <button className="btn-secondary ml-auto"><Filter size={14} />Filters</button>
        <span className="text-xs text-slate-400">{filtered.length} records</span>
      </div>

      {/* Table */}
      <div className="card overflow-hidden">
        <div className="overflow-x-auto">
          <table className="data-table">
            <thead>
              <tr>
                <th>Status</th>
                <th>Delivery ID</th>
                <th>PO Reference</th>
                <th>Vendor</th>
                <th>Items</th>
                <th>Expected Date</th>
                <th>Driver / Vehicle</th>
                <th>QC Status</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map(d => {
                const si = statusIcon[d.status] || statusIcon['Dispatched']
                const Icon = si.icon
                return (
                  <tr key={d.id}>
                    <td>
                      <div className={`w-8 h-8 rounded-lg ${si.cls} flex items-center justify-center`}>
                        <Icon size={15} />
                      </div>
                    </td>
                    <td className="font-bold text-brand-600 text-xs">{d.id}</td>
                    <td>
                      <Link to={`/purchase-orders/${d.po}`} className="text-xs text-brand-500 hover:underline font-medium">{d.po}</Link>
                    </td>
                    <td className="text-slate-700 max-w-[140px] truncate">{d.vendor}</td>
                    <td className="text-xs text-slate-500 max-w-[160px] truncate">{d.items}</td>
                    <td className="text-xs text-slate-400 whitespace-nowrap">{d.date}</td>
                    <td className="text-xs text-slate-500">
                      {d.driver !== '—' ? <><span className="font-medium text-slate-700">{d.driver}</span><br /><span className="text-slate-400">{d.vehicle}</span></> : <span className="text-slate-300">—</span>}
                    </td>
                    <td><span className={`badge ${qcBadge[d.qc]}`}>{d.qc}</span></td>
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
