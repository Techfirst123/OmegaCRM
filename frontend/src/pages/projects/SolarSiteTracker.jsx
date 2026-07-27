import React, { useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import {
  ArrowLeft, Sun, MapPin, Zap, Building2, CheckCircle2,
  Clock, Circle, Filter, Download,
} from 'lucide-react'

// ── Work structure: Solar → Work Stages (left → right execution sequence) ──
export const WORK_STAGES = [
  { key: 'cleaning',   label: 'Cleaning / Leveling' },
  { key: 'working',    label: 'Start to Working Condition' },
  { key: 'survey',     label: 'Survey & Layout Marking' },
  { key: 'ntp',        label: 'NTP / Drawing' },
  { key: 'fencing',    label: 'Fencing / Boundary' },
  { key: 'piling',     label: 'Piling Marking / Acquiring / Legs Installation' },
  { key: 'icr',        label: 'ICR Marking / Foundation' },
  { key: 'mms',        label: 'MMS (Module Mounting Structure)' },
  { key: 'module',     label: 'Module Installation' },
  { key: 'electrical', label: 'Electrical Work' },
]

// ── Hard-coded vendors (contractors) for the 205 MW Rajasthan EPC rollout ──
export const VENDORS = [
  { name: 'Pathfaund',     color: 'bg-brand-500' },
  { name: 'Tru Power',     color: 'bg-violet-500' },
  { name: 'Neel Krishna',  color: 'bg-amber-500' },
  { name: 'Surya Day',     color: 'bg-rose-500' },
  { name: 'Groww Energy',  color: 'bg-teal-500' },
]

// completed = number of WORK_STAGES finished in order; inProgress = currently active stage index (or null if none)
export const SITES = [
  { circle: 'Bikaner',   substation: 'Lunkaransar',   mw: 15, vendor: 'Pathfaund',    completed: 9,  inProgress: 9,    updatedOn: '2026-06-29' },
  { circle: 'Bikaner',   substation: 'Kolayat',        mw: 12, vendor: 'Pathfaund',    completed: 6,  inProgress: 6,    updatedOn: '2026-06-27' },
  { circle: 'Jaisalmer', substation: 'Pokaran',        mw: 18, vendor: 'Pathfaund',    completed: 10, inProgress: null, updatedOn: '2026-06-25' },
  { circle: 'Jaisalmer', substation: 'Ramgarh',        mw: 10, vendor: 'Pathfaund',    completed: 3,  inProgress: 3,    updatedOn: '2026-06-28' },
  { circle: 'Barmer',    substation: 'Baytu',          mw: 14, vendor: 'Tru Power',    completed: 7,  inProgress: 7,    updatedOn: '2026-06-29' },
  { circle: 'Barmer',    substation: 'Sheo',           mw: 13, vendor: 'Tru Power',    completed: 5,  inProgress: 5,    updatedOn: '2026-06-26' },
  { circle: 'Barmer',    substation: 'Chohtan',        mw: 13, vendor: 'Tru Power',    completed: 2,  inProgress: 2,    updatedOn: '2026-06-28' },
  { circle: 'Jodhpur',   substation: 'Phalodi',        mw: 16, vendor: 'Neel Krishna', completed: 8,  inProgress: 8,    updatedOn: '2026-06-30' },
  { circle: 'Jodhpur',   substation: 'Osian',          mw: 12, vendor: 'Neel Krishna', completed: 4,  inProgress: 4,    updatedOn: '2026-06-27' },
  { circle: 'Jodhpur',   substation: 'Bap',            mw: 10, vendor: 'Neel Krishna', completed: 1,  inProgress: 1,    updatedOn: '2026-06-24' },
  { circle: 'Nagaur',    substation: 'Merta',          mw: 14, vendor: 'Surya Day',    completed: 9,  inProgress: 9,    updatedOn: '2026-06-29' },
  { circle: 'Nagaur',    substation: 'Degana',         mw: 12, vendor: 'Surya Day',    completed: 6,  inProgress: 6,    updatedOn: '2026-06-28' },
  { circle: 'Nagaur',    substation: 'Ladnu',          mw: 10, vendor: 'Surya Day',    completed: 3,  inProgress: 3,    updatedOn: '2026-06-25' },
  { circle: 'Churu',     substation: 'Sardarshahar',   mw: 13, vendor: 'Groww Energy', completed: 7,  inProgress: 7,    updatedOn: '2026-06-30' },
  { circle: 'Churu',     substation: 'Ratangarh',      mw: 12, vendor: 'Groww Energy', completed: 5,  inProgress: 5,    updatedOn: '2026-06-26' },
  { circle: 'Churu',     substation: 'Sujangarh',      mw: 11, vendor: 'Groww Energy', completed: 0,  inProgress: 0,    updatedOn: '2026-06-22' },
]

const TOTAL_MW = SITES.reduce((s, x) => s + x.mw, 0)

export function siteProgressPct(site) {
  const stageCredit = site.inProgress !== null && site.inProgress === site.completed ? 0.5 : 0
  return Math.round(((site.completed + stageCredit) / WORK_STAGES.length) * 100)
}

function StageCell({ stageIdx, site }) {
  let state = 'pending'
  if (stageIdx < site.completed) state = 'done'
  else if (stageIdx === site.inProgress) state = 'progress'

  const styles = {
    done:     'bg-emerald-500',
    progress: 'bg-amber-400',
    pending:  'bg-surface-150',
  }
  const icon = {
    done:     <CheckCircle2 size={11} className="text-white" />,
    progress: <Clock size={11} className="text-white" />,
    pending:  <Circle size={9} className="text-slate-400" />,
  }
  return (
    <td className="p-1 text-center">
      <div className={`w-7 h-7 mx-auto rounded-md flex items-center justify-center ${styles[state]}`}>
        {icon[state]}
      </div>
    </td>
  )
}

export default function SolarSiteTracker() {
  const [vendorFilter, setVendorFilter] = useState('All')

  const vendorStats = useMemo(() => VENDORS.map(v => {
    const vSites = SITES.filter(s => s.vendor === v.name)
    const mw = vSites.reduce((s, x) => s + x.mw, 0)
    const avgPct = vSites.length
      ? Math.round(vSites.reduce((s, x) => s + siteProgressPct(x), 0) / vSites.length)
      : 0
    return { ...v, sites: vSites.length, mw, avgPct }
  }), [])

  const filtered = vendorFilter === 'All' ? SITES : SITES.filter(s => s.vendor === vendorFilter)

  const overallPct = Math.round(SITES.reduce((s, x) => s + siteProgressPct(x), 0) / SITES.length)

  return (
    <div className="space-y-6 pb-8">
      {/* Header */}
      <div>
        <Link to="/projects" className="inline-flex items-center gap-1.5 text-sm text-slate-500 hover:text-slate-700 mb-4 transition-colors">
          <ArrowLeft size={15} />Back to Projects
        </Link>
        <div className="page-header">
          <div>
            <h2 className="page-title flex items-center gap-2">
              <Sun size={20} className="text-amber-500" />
              Solar — 205 MW Rajasthan Site Allotment & Work Progress
            </h2>
            <p className="page-subtitle">{SITES.length} sites · {TOTAL_MW} MW · {VENDORS.length} contractors · {overallPct}% overall progress</p>
          </div>
          <button className="btn-secondary"><Download size={14} />Export</button>
        </div>
      </div>

      {/* Vendor summary cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
        {vendorStats.map(v => (
          <button key={v.name} onClick={() => setVendorFilter(vendorFilter === v.name ? 'All' : v.name)}
            className={`card p-4 text-left transition-all hover:shadow-card-hover ${vendorFilter === v.name ? 'ring-2 ring-brand-400' : ''}`}>
            <div className="flex items-center gap-2 mb-3">
              <span className={`w-2.5 h-2.5 rounded-full ${v.color}`} />
              <span className="font-semibold text-slate-900 text-sm truncate">{v.name}</span>
            </div>
            <div className="flex items-center gap-3 text-xs text-slate-500 mb-3">
              <span className="flex items-center gap-1"><Building2 size={11} />{v.sites} sites</span>
              <span className="flex items-center gap-1"><Zap size={11} />{v.mw} MW</span>
            </div>
            <div className="h-1.5 bg-surface-100 rounded-full overflow-hidden mb-1.5">
              <div className={`h-full rounded-full ${v.avgPct === 100 ? 'bg-emerald-500' : 'bg-brand-500'}`} style={{ width: `${v.avgPct}%` }} />
            </div>
            <p className="text-xs font-bold text-slate-700">{v.avgPct}% complete</p>
          </button>
        ))}
      </div>

      {/* Filter bar */}
      <div className="card p-4 flex items-center gap-3 flex-wrap">
        <div className="flex items-center gap-2 text-xs text-slate-500 font-medium"><Filter size={13} />Contractor:</div>
        <div className="flex gap-1.5 flex-wrap">
          {['All', ...VENDORS.map(v => v.name)].map(name => (
            <button key={name} onClick={() => setVendorFilter(name)}
              className={`px-3 py-1.5 text-xs font-semibold rounded-lg transition-colors ${vendorFilter === name ? 'bg-brand-500 text-white shadow-sm' : 'bg-surface-50 text-slate-600 border border-surface-200 hover:bg-surface-100'}`}>
              {name}
            </button>
          ))}
        </div>
        <div className="flex items-center gap-4 ml-auto text-xs text-slate-500">
          <span className="flex items-center gap-1.5"><span className="w-3 h-3 rounded bg-emerald-500" />Done</span>
          <span className="flex items-center gap-1.5"><span className="w-3 h-3 rounded bg-amber-400" />In Progress</span>
          <span className="flex items-center gap-1.5"><span className="w-3 h-3 rounded bg-surface-150 border border-surface-200" />Pending</span>
        </div>
      </div>

      {/* Site x Work-stage status grid */}
      <div className="card overflow-x-auto p-0">
        <table className="w-full text-xs border-collapse">
          <thead>
            <tr className="bg-surface-50 border-b border-surface-200">
              <th className="text-left p-3 font-semibold text-slate-500 sticky left-0 bg-surface-50 z-10">Circle</th>
              <th className="text-left p-3 font-semibold text-slate-500">Substation</th>
              <th className="text-center p-3 font-semibold text-slate-500">MW</th>
              <th className="text-left p-3 font-semibold text-slate-500">Contractor</th>
              {WORK_STAGES.map(ws => (
                <th key={ws.key} className="p-2 font-semibold text-slate-500" style={{ minWidth: 56 }}>
                  <div className="[writing-mode:vertical-rl] rotate-180 inline-block max-h-[140px] py-1">{ws.label}</div>
                </th>
              ))}
              <th className="text-center p-3 font-semibold text-slate-500">Progress</th>
            </tr>
          </thead>
          <tbody>
            {filtered.map((site, i) => {
              const vendor = VENDORS.find(v => v.name === site.vendor)
              const pct = siteProgressPct(site)
              return (
                <tr key={i} className="border-b border-surface-100 hover:bg-surface-50/60 transition-colors">
                  <td className="p-3 font-medium text-slate-700 sticky left-0 bg-white z-10 flex items-center gap-1.5">
                    <MapPin size={11} className="text-slate-400" />{site.circle}
                  </td>
                  <td className="p-3 text-slate-600">{site.substation}</td>
                  <td className="p-3 text-center font-semibold text-slate-700">{site.mw}</td>
                  <td className="p-3">
                    <span className="inline-flex items-center gap-1.5">
                      <span className={`w-2 h-2 rounded-full ${vendor?.color}`} />
                      {site.vendor}
                    </span>
                  </td>
                  {WORK_STAGES.map((ws, idx) => (
                    <StageCell key={ws.key} stageIdx={idx} site={site} />
                  ))}
                  <td className="p-3 text-center">
                    <span className={`font-bold ${pct === 100 ? 'text-emerald-600' : 'text-slate-700'}`}>{pct}%</span>
                  </td>
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>
    </div>
  )
}
