import React, { useState } from 'react'
import { Link } from 'react-router-dom'
import { Search, Plus, Download, Filter, Calendar, TrendingUp } from 'lucide-react'

const mockPOs = [
  { id:'PO-2024-089', vendor:'Tata Projects Ltd',   project:'Solar Farm Alpha',   items:12, value:2450000, status:'Active',           delivery:'30 Jun 2024', payment:'Advance Paid',    created:'15 Jun 2024' },
  { id:'PO-2024-088', vendor:'Larsen & Toubro',     project:'Biogas Plant Beta',  items:8,  value:1820000, status:'Pending Delivery', delivery:'25 Jun 2024', payment:'Not Started',     created:'12 Jun 2024' },
  { id:'PO-2024-087', vendor:'Siemens India',       project:'Wind Farm Gamma',    items:5,  value:4280000, status:'Delivered',        delivery:'22 Jun 2024', payment:'Final Pending',   created:'10 Jun 2024' },
  { id:'PO-2024-086', vendor:'ABB India Ltd',       project:'Solar Farm Alpha',   items:3,  value:960000,  status:'Payment Due',      delivery:'18 Jun 2024', payment:'Payment Overdue', created:'8 Jun 2024'  },
  { id:'PO-2024-085', vendor:'Havells Infra',       project:'Substation Delta',   items:20, value:3140000, status:'Closed',           delivery:'15 Jun 2024', payment:'Paid',            created:'5 Jun 2024'  },
  { id:'PO-2024-084', vendor:'BHEL Heavy Equipment',project:'Wind Farm Gamma',    items:6,  value:8900000, status:'Active',           delivery:'2 Jul 2024',  payment:'Advance Paid',    created:'2 Jun 2024'  },
  { id:'PO-2024-083', vendor:'Sterling & Wilson',   project:'Solar Farm Alpha',   items:15, value:5600000, status:'Delivered',        delivery:'10 Jun 2024', payment:'Paid',            created:'28 May 2024' },
  { id:'PO-2024-082', vendor:'Greentech Solar',     project:'Biogas Plant Beta',  items:4,  value:780000,  status:'Closed',           delivery:'5 Jun 2024',  payment:'Paid',            created:'20 May 2024' },
]

const statusBadge  = { Active:'badge-blue', 'Pending Delivery':'badge-amber', Delivered:'badge-green', 'Payment Due':'badge-red', Closed:'badge-slate' }
const paymentColor = { 'Not Started':'text-slate-400', 'Advance Paid':'text-blue-600', 'Final Pending':'text-amber-600', 'Payment Overdue':'text-red-600', Paid:'text-emerald-600' }

const fmt = (n) => n >= 10000000 ? `₹${(n/10000000).toFixed(1)}Cr` : `₹${(n/100000).toFixed(1)}L`

export default function POList() {
  const [search, setSearch] = useState('')
  const [statusFilter, setStatusFilter] = useState('All')

  const filtered = mockPOs.filter(p => {
    const q = search.toLowerCase()
    return (p.id.toLowerCase().includes(q) || p.vendor.toLowerCase().includes(q) || p.project.toLowerCase().includes(q))
      && (statusFilter === 'All' || p.status === statusFilter)
  })

  const totalValue = filtered.reduce((s, p) => s + p.value, 0)

  const counts = {
    All: mockPOs.length,
    Active: mockPOs.filter(p=>p.status==='Active').length,
    'Pending Delivery': mockPOs.filter(p=>p.status==='Pending Delivery').length,
    Delivered: mockPOs.filter(p=>p.status==='Delivered').length,
    'Payment Due': mockPOs.filter(p=>p.status==='Payment Due').length,
    Closed: mockPOs.filter(p=>p.status==='Closed').length,
  }

  return (
    <div className="space-y-6 pb-4">
      {/* Header */}
      <div className="page-header">
        <div>
          <h2 className="page-title">Purchase Orders</h2>
          <p className="page-subtitle">Total filtered value: <span className="font-semibold text-slate-700">{fmt(totalValue)}</span></p>
        </div>
        <div className="flex items-center gap-2">
          <button className="btn-secondary"><Download size={14} />Export</button>
          <Link to="/purchase-orders/new" className="btn-primary"><Plus size={14} />New PO</Link>
        </div>
      </div>

      {/* Summary chips */}
      <div className="flex gap-2 flex-wrap">
        {[
          { k:'All',              bg:'bg-slate-100', text:'text-slate-700'  },
          { k:'Active',           bg:'bg-blue-100',  text:'text-blue-700'   },
          { k:'Pending Delivery', bg:'bg-amber-100', text:'text-amber-700'  },
          { k:'Delivered',        bg:'bg-green-100', text:'text-green-700'  },
          { k:'Payment Due',      bg:'bg-red-100',   text:'text-red-700'    },
          { k:'Closed',           bg:'bg-slate-100', text:'text-slate-500'  },
        ].map(s => (
          <button key={s.k} onClick={() => setStatusFilter(s.k)}
            className={`flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-medium transition-all ${s.bg} ${s.text} ${statusFilter === s.k ? 'ring-2 ring-offset-1 ring-slate-400/40 shadow-sm' : 'opacity-80 hover:opacity-100'}`}
          >
            <span>{s.k}</span>
            <span className="font-bold">{counts[s.k]}</span>
          </button>
        ))}
      </div>

      {/* Search + filter */}
      <div className="card p-4 flex items-center gap-3 flex-wrap">
        <div className="flex items-center bg-surface-50 border border-surface-200 rounded-lg px-3 py-2 gap-2 flex-1 min-w-[200px] max-w-sm">
          <Search size={14} className="text-slate-400" />
          <input type="text" placeholder="Search PO, vendor, project…"
            className="bg-transparent text-sm placeholder-slate-400 outline-none flex-1"
            value={search} onChange={e => setSearch(e.target.value)}
          />
        </div>
        <button className="btn-secondary"><Calendar size={14} />Date Range</button>
        <button className="btn-secondary"><Filter size={14} />More Filters</button>
        <span className="ml-auto text-xs text-slate-400">{filtered.length} records</span>
      </div>

      {/* Table */}
      <div className="card overflow-hidden">
        <div className="overflow-x-auto">
          <table className="data-table">
            <thead>
              <tr>
                <th>PO Number</th>
                <th>Vendor</th>
                <th>Project</th>
                <th className="text-center">Items</th>
                <th>Value</th>
                <th>Status</th>
                <th>Payment Stage</th>
                <th>Delivery Date</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map(po => (
                <tr key={po.id}>
                  <td>
                    <Link to={`/purchase-orders/${po.id}`} className="font-bold text-brand-600 hover:text-brand-700 text-xs">
                      {po.id}
                    </Link>
                  </td>
                  <td className="font-medium text-slate-800 max-w-[160px] truncate">{po.vendor}</td>
                  <td className="text-xs text-slate-500 max-w-[140px] truncate">{po.project}</td>
                  <td className="text-center text-xs text-slate-600">{po.items}</td>
                  <td className="font-bold text-slate-900">{fmt(po.value)}</td>
                  <td><span className={`badge ${statusBadge[po.status]}`}>{po.status}</span></td>
                  <td className={`text-xs font-semibold ${paymentColor[po.payment]}`}>{po.payment}</td>
                  <td className="text-xs text-slate-400 whitespace-nowrap">{po.delivery}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        {filtered.length === 0 && (
          <div className="py-16 text-center text-slate-400 text-sm">No purchase orders match your search.</div>
        )}
      </div>
    </div>
  )
}
