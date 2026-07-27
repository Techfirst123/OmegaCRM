import React, { useState } from 'react'
import { Search, Package, Upload, Download, Plus, Filter } from 'lucide-react'

const mockMaterials = [
  { id:'MAT-001', name:'Solar PV Module 540W',        cat:'Solar Equipment',  unit:'Nos',  hsnCode:'85414011', gst:'12%', lastRate:'₹8,500',   stock:450  },
  { id:'MAT-002', name:'String Inverter 100kW',       cat:'Solar Equipment',  unit:'Nos',  hsnCode:'85044090', gst:'18%', lastRate:'₹1,85,000', stock:12   },
  { id:'MAT-003', name:'DC Cable 4mm² (Red)',         cat:'Cables',           unit:'Mtrs', hsnCode:'85444290', gst:'18%', lastRate:'₹85',       stock:8200 },
  { id:'MAT-004', name:'AC Cable 10mm² (Black)',      cat:'Cables',           unit:'Mtrs', hsnCode:'85444290', gst:'18%', lastRate:'₹175',      stock:3500 },
  { id:'MAT-005', name:'MC4 Connector Pair',          cat:'Solar Equipment',  unit:'Nos',  hsnCode:'85369090', gst:'18%', lastRate:'₹45',       stock:2000 },
  { id:'MAT-006', name:'Mounting Structure (GI)',     cat:'Structural',       unit:'Set',  hsnCode:'73089090', gst:'18%', lastRate:'₹12,500',   stock:180  },
  { id:'MAT-007', name:'Earthing Strip 25×3mm',       cat:'Electrical',       unit:'Mtrs', hsnCode:'74082100', gst:'18%', lastRate:'₹120',      stock:1200 },
  { id:'MAT-008', name:'AC Distribution Panel',       cat:'Electrical',       unit:'Nos',  hsnCode:'85371090', gst:'18%', lastRate:'₹95,000',   stock:8    },
  { id:'MAT-009', name:'SCADA System',                cat:'Electronics',      unit:'Set',  hsnCode:'85176990', gst:'18%', lastRate:'₹3,50,000', stock:2    },
  { id:'MAT-010', name:'Lightning Arrester',          cat:'Electrical',       unit:'Nos',  hsnCode:'85351000', gst:'18%', lastRate:'₹4,200',    stock:24   },
]

const cats = ['All', ...new Set(mockMaterials.map(m=>m.cat))]

export default function MaterialList() {
  const [search, setSearch] = useState('')
  const [catFilter, setCatFilter] = useState('All')

  const filtered = mockMaterials.filter(m => {
    const q = search.toLowerCase()
    return (m.name.toLowerCase().includes(q) || m.id.toLowerCase().includes(q) || m.hsnCode.includes(q))
      && (catFilter === 'All' || m.cat === catFilter)
  })

  return (
    <div className="space-y-6 pb-4">
      <div className="page-header">
        <div>
          <h2 className="page-title">Material Master</h2>
          <p className="page-subtitle">{mockMaterials.length} materials registered in the system</p>
        </div>
        <div className="flex items-center gap-2">
          <button className="btn-secondary"><Download size={14} />Export</button>
          <button className="btn-secondary"><Upload size={14} />Import Excel</button>
          <button className="btn-primary"><Plus size={14} />Add Material</button>
        </div>
      </div>

      {/* Filter bar */}
      <div className="card p-4 flex items-center gap-3 flex-wrap">
        <div className="flex items-center bg-surface-50 border border-surface-200 rounded-lg px-3 py-2 gap-2 flex-1 max-w-sm">
          <Search size={14} className="text-slate-400" />
          <input type="text" placeholder="Search material name, code, HSN…"
            className="bg-transparent text-sm placeholder-slate-400 outline-none flex-1"
            value={search} onChange={e => setSearch(e.target.value)} />
        </div>
        <div className="flex gap-1.5 flex-wrap">
          {cats.map(c => (
            <button key={c} onClick={() => setCatFilter(c)}
              className={`px-3 py-1.5 text-xs font-semibold rounded-lg transition-colors ${catFilter===c ? 'bg-brand-500 text-white shadow-sm' : 'bg-surface-50 text-slate-600 border border-surface-200 hover:bg-surface-100'}`}
            >
              {c}
            </button>
          ))}
        </div>
        <span className="ml-auto text-xs text-slate-400">{filtered.length} items</span>
      </div>

      {/* Table */}
      <div className="card overflow-hidden">
        <div className="overflow-x-auto">
          <table className="data-table">
            <thead>
              <tr>
                <th>Material Code</th>
                <th>Description</th>
                <th>Category</th>
                <th>Unit</th>
                <th>HSN Code</th>
                <th>GST Rate</th>
                <th className="text-right">Last Rate</th>
                <th className="text-right">Stock Qty</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map(m => (
                <tr key={m.id} className="cursor-pointer">
                  <td className="font-mono text-xs font-bold text-brand-600">{m.id}</td>
                  <td>
                    <div className="flex items-center gap-2">
                      <div className="w-7 h-7 rounded-lg bg-orange-50 border border-orange-100 flex items-center justify-center flex-shrink-0">
                        <Package size={13} className="text-orange-500" />
                      </div>
                      <span className="font-medium text-slate-800">{m.name}</span>
                    </div>
                  </td>
                  <td><span className="badge badge-slate text-xs">{m.cat}</span></td>
                  <td className="text-xs text-slate-500">{m.unit}</td>
                  <td className="font-mono text-xs text-slate-500">{m.hsnCode}</td>
                  <td className="text-xs font-semibold text-slate-600">{m.gst}</td>
                  <td className="text-right font-semibold text-slate-900">{m.lastRate}</td>
                  <td className="text-right font-bold text-slate-900">{m.stock.toLocaleString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
