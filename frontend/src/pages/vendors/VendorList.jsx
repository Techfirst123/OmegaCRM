import React, { useState } from 'react'
import { Link } from 'react-router-dom'
import { Search, Plus, Building2, MapPin, Phone, ChevronRight, Download, SlidersHorizontal } from 'lucide-react'

const mockVendors = [
  { id:1, code:'VND-001', name:'Tata Projects Ltd',     cat:'EPC Contractor',      gst:'27AAACT2727Q1ZW', state:'Maharashtra', city:'Mumbai',    phone:'+91 22 6745 9000', status:'Active',   msme:false, rating:4.8, pos:24 },
  { id:2, code:'VND-002', name:'Larsen & Toubro Ltd',   cat:'EPC Contractor',      gst:'29AAACL0624G1ZB', state:'Karnataka',   city:'Bangalore', phone:'+91 80 2222 8000', status:'Active',   msme:false, rating:4.9, pos:31 },
  { id:3, code:'VND-003', name:'Siemens India Ltd',     cat:'Equipment Supplier',  gst:'27AAACS1891G1ZR', state:'Maharashtra', city:'Pune',      phone:'+91 20 6666 5000', status:'Active',   msme:false, rating:4.7, pos:18 },
  { id:4, code:'VND-004', name:'ABB India Ltd',         cat:'Equipment Supplier',  gst:'29AAACA7815L1ZP', state:'Karnataka',   city:'Bangalore', phone:'+91 80 2294 9000', status:'Active',   msme:false, rating:4.6, pos:12 },
  { id:5, code:'VND-005', name:'Havells Infra Pvt Ltd', cat:'Material Supplier',   gst:'07AABCH0698E1ZF', state:'Delhi',       city:'New Delhi', phone:'+91 11 4966 2222', status:'Inactive', msme:true,  rating:4.2, pos:9  },
  { id:6, code:'VND-006', name:'BHEL Heavy Equipment',  cat:'Equipment Supplier',  gst:'07AAACB4174D1ZS', state:'Delhi',       city:'Noida',     phone:'+91 120 2525 000', status:'Active',   msme:false, rating:4.4, pos:7  },
  { id:7, code:'VND-007', name:'Sterling & Wilson',     cat:'EPC Contractor',      gst:'27AADFS1234K1Z0', state:'Maharashtra', city:'Mumbai',    phone:'+91 22 6158 9000', status:'Active',   msme:false, rating:4.5, pos:15 },
  { id:8, code:'VND-008', name:'Greentech Solar Pvt',   cat:'Material Supplier',   gst:'33AAGFG2345B1ZP', state:'Tamil Nadu',  city:'Chennai',   phone:'+91 44 4567 8900', status:'Active',   msme:true,  rating:4.1, pos:6  },
  // Solar EPC site contractors — 205 MW Rajasthan rollout (see /projects/solar-tracker)
  { id:9,  code:'VND-009', name:'Pathfaund',     cat:'Solar EPC Contractor', gst:'08AAFCP4521R1ZH', state:'Rajasthan', city:'Bikaner',   phone:'+91 151 220 4400', status:'Active', msme:true, rating:4.3, pos:4 },
  { id:10, code:'VND-010', name:'Tru Power',     cat:'Solar EPC Contractor', gst:'08AAGCT8834M1ZK', state:'Rajasthan', city:'Barmer',    phone:'+91 2982 22 1100', status:'Active', msme:true, rating:4.1, pos:3 },
  { id:11, code:'VND-011', name:'Neel Krishna',  cat:'Solar EPC Contractor', gst:'08AAHCN1192P1ZD', state:'Rajasthan', city:'Jodhpur',   phone:'+91 291 251 6600', status:'Active', msme:true, rating:4.0, pos:3 },
  { id:12, code:'VND-012', name:'Surya Day',     cat:'Solar EPC Contractor', gst:'08AAICS5567Q1ZB', state:'Rajasthan', city:'Nagaur',    phone:'+91 1582 24 3300', status:'Active', msme:true, rating:4.2, pos:3 },
  { id:13, code:'VND-013', name:'Groww Energy',  cat:'Solar EPC Contractor', gst:'08AAJCG3309K1ZF', state:'Rajasthan', city:'Churu',     phone:'+91 1562 25 7700', status:'Active', msme:true, rating:4.0, pos:3 },
]

const Stars = ({ n }) => (
  <div className="flex items-center gap-0.5">
    {[...Array(5)].map((_, i) => (
      <div key={i} className={`w-1.5 h-1.5 rounded-full ${i < Math.floor(n) ? 'bg-amber-400' : 'bg-surface-200'}`} />
    ))}
    <span className="text-xs text-slate-400 ml-1">{n}</span>
  </div>
)

export default function VendorList() {
  const [search, setSearch] = useState('')
  const [statusFilter, setStatusFilter] = useState('All')

  const filtered = mockVendors.filter(v => {
    const q = search.toLowerCase()
    const matchQ = v.name.toLowerCase().includes(q) || v.code.toLowerCase().includes(q) || v.city.toLowerCase().includes(q)
    const matchS = statusFilter === 'All' || v.status === statusFilter
    return matchQ && matchS
  })

  return (
    <div className="space-y-6 pb-4">
      {/* Header */}
      <div className="page-header">
        <div>
          <h2 className="page-title">Vendor Management</h2>
          <p className="page-subtitle">{mockVendors.length} vendors registered · {mockVendors.filter(v=>v.status==='Active').length} active</p>
        </div>
        <div className="flex items-center gap-2">
          <button className="btn-secondary"><Download size={15} />Export</button>
          <Link to="/vendors/new" className="btn-primary"><Plus size={15} />Add Vendor</Link>
        </div>
      </div>

      {/* Filter bar */}
      <div className="card p-4 flex items-center gap-3 flex-wrap">
        <div className="flex items-center bg-surface-50 border border-surface-200 rounded-lg px-3 py-2 gap-2 flex-1 min-w-[200px] max-w-sm">
          <Search size={14} className="text-slate-400 flex-shrink-0" />
          <input
            type="text"
            placeholder="Search by name, code, city…"
            className="bg-transparent text-sm text-slate-700 placeholder-slate-400 outline-none flex-1"
            value={search}
            onChange={e => setSearch(e.target.value)}
          />
        </div>
        <div className="flex items-center gap-1.5">
          {['All', 'Active', 'Inactive'].map(s => (
            <button key={s} onClick={() => setStatusFilter(s)}
              className={`px-3 py-1.5 text-xs font-semibold rounded-lg transition-colors ${
                statusFilter === s ? 'bg-brand-500 text-white shadow-sm' : 'bg-surface-50 text-slate-600 border border-surface-200 hover:bg-surface-100'
              }`}
            >
              {s}
            </button>
          ))}
        </div>
        <button className="btn-secondary ml-auto"><SlidersHorizontal size={14} />Filters</button>
        <span className="text-xs text-slate-400 font-medium">{filtered.length} results</span>
      </div>

      {/* Cards grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 2xl:grid-cols-4 gap-4">
        {filtered.map(v => (
          <Link key={v.id} to={`/vendors/${v.id}`}
            className="card p-5 hover:shadow-card-hover hover:border-brand-200 transition-all duration-150 group block"
          >
            {/* Card top */}
            <div className="flex items-start justify-between mb-4">
              <div className="flex items-center gap-3">
                <div className="w-11 h-11 rounded-xl bg-brand-50 border border-brand-100 flex items-center justify-center flex-shrink-0">
                  <Building2 size={20} className="text-brand-600" />
                </div>
                <div>
                  <p className="text-xs font-medium text-slate-400">{v.code}</p>
                  <span className={`badge text-xs mt-0.5 ${v.status === 'Active' ? 'badge-green' : 'badge-slate'}`}>
                    {v.status}
                  </span>
                </div>
              </div>
              {v.msme && <span className="badge badge-violet text-xs">MSME</span>}
            </div>

            <h3 className="font-semibold text-slate-900 text-sm mb-0.5 group-hover:text-brand-600 transition-colors truncate">{v.name}</h3>
            <p className="text-xs text-slate-400 mb-4">{v.cat}</p>

            <div className="space-y-1.5 mb-4">
              <div className="flex items-center gap-2 text-xs text-slate-500">
                <MapPin size={11} className="flex-shrink-0 text-slate-400" />{v.city}, {v.state}
              </div>
              <div className="flex items-center gap-2 text-xs text-slate-500">
                <Phone size={11} className="flex-shrink-0 text-slate-400" />{v.phone}
              </div>
            </div>

            <div className="flex items-center justify-between pt-4 border-t border-surface-100">
              <div className="flex items-center gap-3">
                <Stars n={v.rating} />
                <span className="text-xs text-slate-400">{v.pos} POs</span>
              </div>
              <ChevronRight size={15} className="text-slate-300 group-hover:text-brand-500 transition-colors" />
            </div>
          </Link>
        ))}
      </div>
    </div>
  )
}
