import React, { useState } from 'react'
import { ArrowLeftRight, MapPin, Truck, Search, Plus } from 'lucide-react'

const mockTransport = [
  { id:'TRP-001', vehicle:'MH-12-AB-3456', driver:'Ramesh Kumar',  from:'Mumbai',    to:'Rajasthan Site',  delivery:'DEL-2024-045', status:'In Transit',  eta:'22 Jun 2024', freight:'₹18,500' },
  { id:'TRP-002', vehicle:'KA-09-CD-7890', driver:'Suresh Mehta',  from:'Bangalore', to:'Pune Site',       delivery:'DEL-2024-044', status:'Dispatched',  eta:'20 Jun 2024', freight:'₹12,000' },
  { id:'TRP-003', vehicle:'MH-14-EF-1234', driver:'Arun Patil',    from:'Pune',      to:'Gujarat Site',    delivery:'DEL-2024-043', status:'Delivered',   eta:'18 Jun 2024', freight:'₹24,000' },
  { id:'TRP-004', vehicle:'DL-01-GH-5678', driver:'Vijay Singh',   from:'Noida',     to:'Punjab Site',     delivery:'DEL-2024-042', status:'Unloaded',    eta:'16 Jun 2024', freight:'₹31,500' },
]

const statusBadge = { Dispatched:'badge-blue', 'In Transit':'badge-amber', Delivered:'badge-green', Unloaded:'badge-slate' }

export default function TransportList() {
  const [search, setSearch] = useState('')
  const filtered = mockTransport.filter(t => {
    const q = search.toLowerCase()
    return t.vehicle.toLowerCase().includes(q) || t.driver.toLowerCase().includes(q) || t.delivery.toLowerCase().includes(q)
  })
  return (
    <div className="space-y-6 pb-4">
      <div className="page-header">
        <div>
          <h2 className="page-title">Transport Tracking</h2>
          <p className="page-subtitle">{mockTransport.length} active shipments</p>
        </div>
        <button className="btn-primary"><Plus size={14} />Add Movement</button>
      </div>
      <div className="card p-4 flex items-center gap-3">
        <div className="flex items-center bg-surface-50 border border-surface-200 rounded-lg px-3 py-2 gap-2 flex-1 max-w-sm">
          <Search size={14} className="text-slate-400" />
          <input type="text" placeholder="Search vehicle, driver, delivery…"
            className="bg-transparent text-sm placeholder-slate-400 outline-none flex-1"
            value={search} onChange={e => setSearch(e.target.value)} />
        </div>
      </div>
      <div className="card overflow-hidden">
        <table className="data-table">
          <thead><tr><th>ID</th><th>Vehicle</th><th>Driver</th><th>Route</th><th>Delivery Ref</th><th>ETA</th><th>Freight</th><th>Status</th></tr></thead>
          <tbody>
            {filtered.map(t => (
              <tr key={t.id}>
                <td className="font-bold text-brand-600 text-xs">{t.id}</td>
                <td className="font-mono text-xs font-semibold text-slate-800">{t.vehicle}</td>
                <td className="text-slate-700">{t.driver}</td>
                <td className="text-xs text-slate-500">
                  <div className="flex items-center gap-1">
                    <MapPin size={10} className="text-slate-400" />{t.from}
                    <ArrowLeftRight size={10} className="text-slate-300" />
                    <MapPin size={10} className="text-emerald-500" />{t.to}
                  </div>
                </td>
                <td className="text-xs text-brand-500 font-semibold">{t.delivery}</td>
                <td className="text-xs text-slate-400">{t.eta}</td>
                <td className="font-semibold text-slate-900 text-xs">{t.freight}</td>
                <td><span className={`badge ${statusBadge[t.status]}`}>{t.status}</span></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
