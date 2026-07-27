import React from 'react'
import { BarChart3, Download, FileText, TrendingUp, Clock, Building2, ShoppingCart, Truck, CreditCard } from 'lucide-react'

const reportGroups = [
  {
    group: 'Procurement Reports',
    icon: ShoppingCart,
    color: 'text-blue-600 bg-blue-50',
    reports: [
      { name:'Purchase Order Summary',    desc:'PO-wise status, value, and vendor breakdown',      updated:'Today' },
      { name:'Vendor Performance Report', desc:'On-time delivery, quality score, PO value per vendor', updated:'Yesterday' },
      { name:'PO Age Analysis',           desc:'Ageing of open purchase orders beyond due date',   updated:'2 days ago' },
      { name:'Category-wise Spend',       desc:'Material category-wise purchase spend analysis',   updated:'1 week ago' },
    ],
  },
  {
    group: 'Delivery Reports',
    icon: Truck,
    color: 'text-amber-600 bg-amber-50',
    reports: [
      { name:'Delivery Status Report',    desc:'All deliveries with status, QC, and site details', updated:'Today'      },
      { name:'Overdue Deliveries',        desc:'Deliveries delayed beyond expected delivery date',  updated:'Today'      },
      { name:'Quality Rejection Summary', desc:'QC failures, rejection reasons, and vendor action', updated:'3 days ago' },
    ],
  },
  {
    group: 'Payment Reports',
    icon: CreditCard,
    color: 'text-emerald-600 bg-emerald-50',
    reports: [
      { name:'Payment Ledger',            desc:'All payments with TDS, GST, and bank reference',   updated:'Yesterday'  },
      { name:'Outstanding Payables',      desc:'Pending payment amounts by vendor and stage',       updated:'Today'      },
      { name:'TDS Deduction Summary',     desc:'TDS deducted per vendor for IT compliance',         updated:'1 week ago' },
    ],
  },
  {
    group: 'Vendor Reports',
    icon: Building2,
    color: 'text-violet-600 bg-violet-50',
    reports: [
      { name:'Vendor Master List',        desc:'All registered vendors with compliance and status', updated:'2 days ago' },
      { name:'MSME Vendor Report',        desc:'MSME vendors, spend, and statutory compliance',     updated:'1 week ago' },
      { name:'Vendor Task Status',        desc:'Open tasks across vendors and staff assignees',     updated:'Yesterday'  },
    ],
  },
]

export default function ReportsList() {
  return (
    <div className="space-y-6 pb-4">
      <div className="page-header">
        <div>
          <h2 className="page-title">Reports &amp; Analytics</h2>
          <p className="page-subtitle">Generate and download business reports across all modules</p>
        </div>
      </div>

      {/* Quick stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {[
          { label:'Reports Generated',  value:'1,248', icon: BarChart3,  cls:'text-brand-600 bg-brand-50'    },
          { label:'Last Export',        value:'2h ago', icon: Download,   cls:'text-emerald-600 bg-emerald-50' },
          { label:'Saved Reports',      value:'14',     icon: FileText,   cls:'text-amber-600 bg-amber-50'    },
          { label:'Scheduled Reports',  value:'5',      icon: Clock,      cls:'text-violet-600 bg-violet-50'  },
        ].map(s => {
          const Icon = s.icon
          return (
            <div key={s.label} className="card p-4 flex items-center gap-3">
              <div className={`w-9 h-9 rounded-xl ${s.cls} flex items-center justify-center flex-shrink-0`}>
                <Icon size={16} />
              </div>
              <div>
                <p className="font-bold text-slate-900 text-lg leading-none">{s.value}</p>
                <p className="text-xs text-slate-400 mt-0.5">{s.label}</p>
              </div>
            </div>
          )
        })}
      </div>

      {/* Report groups */}
      <div className="space-y-6">
        {reportGroups.map(group => {
          const GroupIcon = group.icon
          return (
            <div key={group.group}>
              <div className="flex items-center gap-2 mb-3">
                <div className={`w-7 h-7 rounded-lg ${group.color} flex items-center justify-center flex-shrink-0`}>
                  <GroupIcon size={14} />
                </div>
                <h3 className="font-semibold text-slate-900 text-sm">{group.group}</h3>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-3">
                {group.reports.map(r => (
                  <div key={r.name} className="card p-4 hover:shadow-card-hover transition-all cursor-pointer group flex items-center gap-3">
                    <div className="w-9 h-9 rounded-xl bg-surface-100 flex items-center justify-center flex-shrink-0 group-hover:bg-brand-50 group-hover:border group-hover:border-brand-100 transition-all">
                      <FileText size={16} className="text-slate-400 group-hover:text-brand-500 transition-colors" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-semibold text-slate-900 truncate group-hover:text-brand-600 transition-colors">{r.name}</p>
                      <p className="text-xs text-slate-400 mt-0.5 truncate">{r.desc}</p>
                      <p className="text-xs text-slate-300 mt-1">Updated {r.updated}</p>
                    </div>
                    <Download size={14} className="text-slate-300 flex-shrink-0 group-hover:text-brand-500 transition-colors" />
                  </div>
                ))}
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}
