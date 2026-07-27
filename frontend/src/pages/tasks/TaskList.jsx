import React, { useState } from 'react'
import { ClipboardList, CheckCircle, Clock, AlertCircle, Plus, Search } from 'lucide-react'

const mockTasks = [
  { id:1, title:'Collect GST renewal certificate from Tata Projects',     type:'Document Collection', vendor:'Tata Projects Ltd', assignee:'Anjali Mehta', due:'30 Jun 2024', status:'Pending',     priority:'High'   },
  { id:2, title:'Follow up on Solar Phase 2 quotation with L&T',          type:'Quotation Follow-up', vendor:'L&T Ltd',          assignee:'Rajesh Kumar', due:'25 Jun 2024', status:'In Progress', priority:'High'   },
  { id:3, title:'Verify updated bank details for Siemens',                type:'Compliance Check',   vendor:'Siemens India',    assignee:'Priya Sharma', due:'20 Jun 2024', status:'Completed',   priority:'Medium' },
  { id:4, title:'Onboard Greentech Solar as new vendor',                  type:'Onboarding',         vendor:'Greentech Solar',  assignee:'Kiran Patel',  due:'15 Jul 2024', status:'In Progress', priority:'Low'    },
  { id:5, title:'Collect MSME registration certificate — Havells Infra',  type:'Document Collection',vendor:'Havells Infra',    assignee:'Anjali Mehta', due:'10 Jul 2024', status:'Pending',     priority:'Medium' },
]

const statusBadge = { Pending:'badge-amber', 'In Progress':'badge-blue', Completed:'badge-green' }
const priorityBadge = { High:'badge-red', Medium:'badge-amber', Low:'badge-slate' }

export default function TaskList() {
  const [search, setSearch] = useState('')
  const [statusFilter, setStatusFilter] = useState('All')
  const filtered = mockTasks.filter(t => {
    const q = search.toLowerCase()
    return (t.title.toLowerCase().includes(q) || t.vendor.toLowerCase().includes(q))
      && (statusFilter === 'All' || t.status === statusFilter)
  })
  return (
    <div className="space-y-6 pb-4">
      <div className="page-header">
        <div>
          <h2 className="page-title">Vendor Tasks</h2>
          <p className="page-subtitle">{mockTasks.filter(t=>t.status!=='Completed').length} open tasks</p>
        </div>
        <button className="btn-primary"><Plus size={14} />New Task</button>
      </div>
      <div className="card p-4 flex items-center gap-3 flex-wrap">
        <div className="flex items-center bg-surface-50 border border-surface-200 rounded-lg px-3 py-2 gap-2 flex-1 max-w-sm">
          <Search size={14} className="text-slate-400" />
          <input type="text" placeholder="Search tasks…"
            className="bg-transparent text-sm placeholder-slate-400 outline-none flex-1"
            value={search} onChange={e => setSearch(e.target.value)} />
        </div>
        <div className="flex gap-1.5">
          {['All','Pending','In Progress','Completed'].map(s => (
            <button key={s} onClick={() => setStatusFilter(s)}
              className={`px-3 py-1.5 text-xs font-semibold rounded-lg transition-colors ${statusFilter===s ? 'bg-brand-500 text-white shadow-sm' : 'bg-surface-50 text-slate-600 border border-surface-200 hover:bg-surface-100'}`}
            >
              {s}
            </button>
          ))}
        </div>
      </div>
      <div className="card overflow-hidden">
        <table className="data-table">
          <thead><tr><th>#</th><th>Task</th><th>Type</th><th>Vendor</th><th>Assignee</th><th>Due</th><th>Priority</th><th>Status</th></tr></thead>
          <tbody>
            {filtered.map(t => (
              <tr key={t.id}>
                <td className="text-slate-400 text-xs">{t.id}</td>
                <td className="font-medium text-slate-800 max-w-[240px] truncate">{t.title}</td>
                <td className="text-xs text-slate-500">{t.type}</td>
                <td className="text-slate-600 text-xs">{t.vendor}</td>
                <td className="text-xs text-slate-500">{t.assignee}</td>
                <td className="text-xs text-slate-400 whitespace-nowrap">{t.due}</td>
                <td><span className={`badge ${priorityBadge[t.priority]}`}>{t.priority}</span></td>
                <td><span className={`badge ${statusBadge[t.status]}`}>{t.status}</span></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
