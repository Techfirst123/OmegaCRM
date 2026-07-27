import React, { useState } from 'react'
import { Link } from 'react-router-dom'
import { Search, FolderKanban, MapPin, Zap, Plus, Users, ChevronRight, Sun } from 'lucide-react'

const mockProjects = [
  { id:1, code:'PRJ-001', name:'Solar — Pathfaund 205 MW', type:'Solar PV', capacity:'205 MW', location:'Rajasthan',  client:'SECI',    status:'Active',    progress:62, vendors:5,  poValue:'₹48Cr', tracker:true },
  { id:2, code:'PRJ-002', name:'Biogas Plant Beta',     type:'Biogas',     capacity:'5 MW',   location:'Punjab',     client:'MNRE',    status:'Active',    progress:34, vendors:5,  poValue:'₹12Cr'  },
  { id:3, code:'PRJ-003', name:'Wind Farm Gamma',       type:'Wind',       capacity:'100 MW', location:'Tamil Nadu', client:'TANGEDCO',status:'Active',    progress:88, vendors:12, poValue:'₹102Cr' },
  { id:4, code:'PRJ-004', name:'Substation Delta',      type:'Civil',      capacity:'220kV',  location:'Gujarat',    client:'GETCO',   status:'Completed', progress:100,vendors:6,  poValue:'₹28Cr'  },
  { id:5, code:'PRJ-005', name:'Solar Farm Epsilon',    type:'Solar PV',   capacity:'80 MW',  location:'Madhya Pradesh',client:'NTPC', status:'Planning',  progress:8,  vendors:3,  poValue:'₹6Cr'   },
  { id:6, code:'PRJ-006', name:'Pharma Plant Zeta',     type:'Industrial', capacity:'—',      location:'Maharashtra', client:'SunPharma',status:'Active',  progress:55, vendors:9,  poValue:'₹34Cr'  },
]

const statusBadge = { Active:'badge-blue', Completed:'badge-green', Planning:'badge-amber' }

const ProgressBar = ({ pct }) => (
  <div className="h-2 bg-surface-100 rounded-full overflow-hidden w-full">
    <div className={`h-full rounded-full transition-all ${pct === 100 ? 'bg-emerald-500' : pct > 70 ? 'bg-brand-500' : pct > 30 ? 'bg-amber-500' : 'bg-slate-400'}`}
      style={{ width:`${pct}%` }} />
  </div>
)

export default function ProjectList() {
  const [search, setSearch] = useState('')
  const [typeFilter, setTypeFilter] = useState('All')

  const types = ['All', ...new Set(mockProjects.map(p=>p.type))]

  const filtered = mockProjects.filter(p => {
    const q = search.toLowerCase()
    return (p.name.toLowerCase().includes(q) || p.code.toLowerCase().includes(q) || p.location.toLowerCase().includes(q))
      && (typeFilter === 'All' || p.type === typeFilter)
  })

  return (
    <div className="space-y-6 pb-4">
      <div className="page-header">
        <div>
          <h2 className="page-title">Projects</h2>
          <p className="page-subtitle">{mockProjects.length} projects · {mockProjects.filter(p=>p.status==='Active').length} active</p>
        </div>
        <div className="flex items-center gap-2">
          <Link to="/projects/solar-tracker" className="btn-secondary"><Sun size={14} />Solar Site Tracker</Link>
          <Link to="/projects/new" className="btn-primary"><Plus size={14} />New Project</Link>
        </div>
      </div>

      {/* Filter bar */}
      <div className="card p-4 flex items-center gap-3 flex-wrap">
        <div className="flex items-center bg-surface-50 border border-surface-200 rounded-lg px-3 py-2 gap-2 flex-1 max-w-sm">
          <Search size={14} className="text-slate-400" />
          <input type="text" placeholder="Search project name, code, location…"
            className="bg-transparent text-sm placeholder-slate-400 outline-none flex-1"
            value={search} onChange={e => setSearch(e.target.value)} />
        </div>
        <div className="flex gap-1.5 flex-wrap">
          {types.map(t => (
            <button key={t} onClick={() => setTypeFilter(t)}
              className={`px-3 py-1.5 text-xs font-semibold rounded-lg transition-colors ${typeFilter===t ? 'bg-brand-500 text-white shadow-sm' : 'bg-surface-50 text-slate-600 border border-surface-200 hover:bg-surface-100'}`}
            >
              {t}
            </button>
          ))}
        </div>
      </div>

      {/* Project cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
        {filtered.map(p => {
          const Card = p.tracker ? Link : 'div'
          const cardProps = p.tracker ? { to: '/projects/solar-tracker' } : {}
          return (
          <Card key={p.id} {...cardProps} className="card p-5 hover:shadow-card-hover transition-all group cursor-pointer block">
            <div className="flex items-start justify-between mb-4">
              <div className="flex items-center gap-3">
                <div className="w-11 h-11 rounded-xl bg-brand-50 border border-brand-100 flex items-center justify-center flex-shrink-0">
                  <FolderKanban size={19} className="text-brand-600" />
                </div>
                <div>
                  <p className="text-xs font-medium text-slate-400">{p.code}</p>
                  <span className={`badge mt-0.5 ${statusBadge[p.status]}`}>{p.status}</span>
                </div>
              </div>
              <span className="text-xs font-semibold text-slate-400 bg-surface-100 px-2 py-1 rounded-lg">{p.type}</span>
            </div>

            <h3 className="font-semibold text-slate-900 mb-1 group-hover:text-brand-600 transition-colors">{p.name}</h3>

            <div className="flex items-center gap-4 text-xs text-slate-500 mb-4">
              <span className="flex items-center gap-1"><MapPin size={11} />{p.location}</span>
              <span className="flex items-center gap-1"><Zap size={11} />{p.capacity}</span>
            </div>

            {/* Progress */}
            <div className="mb-4">
              <div className="flex items-center justify-between text-xs mb-1.5">
                <span className="text-slate-500 font-medium">Project Progress</span>
                <span className={`font-bold ${p.progress === 100 ? 'text-emerald-600' : 'text-slate-900'}`}>{p.progress}%</span>
              </div>
              <ProgressBar pct={p.progress} />
            </div>

            <div className="flex items-center justify-between pt-3 border-t border-surface-100 text-xs">
              <div className="flex items-center gap-3 text-slate-500">
                <span className="flex items-center gap-1"><Users size={11} />{p.vendors} vendors</span>
                <span className="font-semibold text-slate-700">{p.poValue} PO</span>
              </div>
              <span className="text-slate-400">{p.client}</span>
            </div>
          </Card>
          )
        })}
      </div>
    </div>
  )
}
