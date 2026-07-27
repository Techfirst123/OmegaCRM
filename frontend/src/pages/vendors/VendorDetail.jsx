import React, { useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import {
  ArrowLeft, Building2, MapPin, Phone, Mail, Globe, Edit,
  FileText, CheckCircle, Clock, ShoppingCart, CreditCard, Star,
} from 'lucide-react'

const vendor = {
  id: 1, code: 'VND-001', name: 'Tata Projects Ltd', cat: 'EPC Contractor',
  status: 'Active', msme: false, rating: 4.8,
  gst: '27AAACT2727Q1ZW', pan: 'AAACT2727Q', cin: 'U45209MH1979PLC021258',
  address: 'Mafatlal Centre, 10th Floor, Nariman Point, Mumbai - 400021',
  state: 'Maharashtra', city: 'Mumbai', pincode: '400021',
  contact: '+91 22 6745 9000', email: 'procurement@tataprojects.com', website: 'www.tataprojects.com',
  bank: 'HDFC Bank Ltd', ifsc: 'HDFC0001234', account: '50200012345678', branch: 'Nariman Point, Mumbai',
  registeredDate: '12 Jan 2022',
  recentPOs: [
    { id: 'PO-2024-089', project: 'Solar Farm Alpha',  value: '₹24.5L', status: 'Active',   date: '15 Jun 2024' },
    { id: 'PO-2024-076', project: 'Wind Farm Gamma',   value: '₹18.2L', status: 'Closed',   date: '2 May 2024'  },
    { id: 'PO-2024-061', project: 'Biogas Plant Beta', value: '₹31.4L', status: 'Closed',   date: '14 Mar 2024' },
  ],
  tasks: [
    { id: 1, title: 'Collect GST certificate (renewal)', status: 'Pending', due: '30 Jun 2024' },
    { id: 2, title: 'Quotation follow-up — Solar Phase 2', status: 'In Progress', due: '25 Jun 2024' },
    { id: 3, title: 'Verify bank details update', status: 'Completed', due: '15 Jun 2024' },
  ],
  docs: [
    { name: 'GST Registration Certificate',  date: '12 Jan 2022', type: 'Compliance' },
    { name: 'PAN Card',                       date: '12 Jan 2022', type: 'Identity'   },
    { name: 'Cancelled Cheque',               date: '5 Mar 2023',  type: 'Banking'    },
    { name: 'Incorporation Certificate',      date: '12 Jan 2022', type: 'Legal'      },
  ],
}

const TABS = ['Overview', 'Purchase Orders', 'Tasks', 'Documents']

const statusBadge = { Active:'badge-blue', Closed:'badge-slate', Delivered:'badge-green' }
const taskBadge   = { Pending:'badge-amber', 'In Progress':'badge-blue', Completed:'badge-green' }

export default function VendorDetail() {
  const { id } = useParams()
  const [tab, setTab] = useState('Overview')

  return (
    <div className="space-y-6 pb-4">
      {/* Back + header */}
      <div>
        <Link to="/vendors" className="inline-flex items-center gap-1.5 text-sm text-slate-500 hover:text-slate-700 mb-4 transition-colors">
          <ArrowLeft size={15} />Back to Vendors
        </Link>
        <div className="flex items-start justify-between gap-4">
          <div className="flex items-center gap-4">
            <div className="w-14 h-14 rounded-2xl bg-brand-50 border-2 border-brand-100 flex items-center justify-center flex-shrink-0">
              <Building2 size={26} className="text-brand-600" />
            </div>
            <div>
              <div className="flex items-center gap-2 mb-1">
                <h2 className="text-xl font-bold text-slate-900">{vendor.name}</h2>
                <span className="badge badge-green">{vendor.status}</span>
                {vendor.msme && <span className="badge badge-violet">MSME</span>}
              </div>
              <p className="text-slate-500 text-sm">{vendor.cat} · {vendor.code}</p>
              <p className="text-xs text-slate-400 mt-0.5 flex items-center gap-1">
                <MapPin size={11} />{vendor.city}, {vendor.state}
              </p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <button className="btn-secondary"><Edit size={14} />Edit</button>
            <button className="btn-primary"><ShoppingCart size={14} />Create PO</button>
          </div>
        </div>
      </div>

      {/* KPI strip */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {[
          { label: 'Total POs',          value: '24',     icon: ShoppingCart, cls: 'text-blue-600 bg-blue-50'    },
          { label: 'Total PO Value',     value: '₹4.8Cr', icon: CreditCard,   cls: 'text-emerald-600 bg-emerald-50' },
          { label: 'Active Tasks',       value: '2',      icon: Clock,        cls: 'text-amber-600 bg-amber-50'  },
          { label: 'Vendor Rating',      value: '4.8 ★',  icon: Star,         cls: 'text-violet-600 bg-violet-50'},
        ].map(k => {
          const Icon = k.icon
          return (
            <div key={k.label} className="card p-4 flex items-center gap-3">
              <div className={`w-9 h-9 rounded-xl ${k.cls} flex items-center justify-center flex-shrink-0`}>
                <Icon size={16} />
              </div>
              <div>
                <p className="font-bold text-slate-900 text-lg leading-none">{k.value}</p>
                <p className="text-xs text-slate-400 mt-0.5">{k.label}</p>
              </div>
            </div>
          )
        })}
      </div>

      {/* Tabs */}
      <div className="border-b border-surface-200">
        <div className="flex gap-0">
          {TABS.map(t => (
            <button key={t} onClick={() => setTab(t)}
              className={`px-5 py-3 text-sm font-medium border-b-2 transition-colors ${
                tab === t ? 'border-brand-500 text-brand-600' : 'border-transparent text-slate-500 hover:text-slate-700'
              }`}
            >
              {t}
            </button>
          ))}
        </div>
      </div>

      {/* Tab content */}
      {tab === 'Overview' && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
          {/* Registration */}
          <div className="card p-5">
            <h3 className="font-semibold text-slate-900 text-sm mb-4">Registration Details</h3>
            <dl className="space-y-3">
              {[
                { l:'GST Number',   v: vendor.gst          },
                { l:'PAN Number',   v: vendor.pan          },
                { l:'CIN',          v: vendor.cin          },
                { l:'Registered On',v: vendor.registeredDate},
              ].map(r => (
                <div key={r.l} className="flex items-center justify-between py-1.5 border-b border-surface-50 last:border-0">
                  <dt className="text-xs text-slate-500 font-medium">{r.l}</dt>
                  <dd className="text-sm text-slate-900 font-mono text-xs">{r.v}</dd>
                </div>
              ))}
            </dl>
          </div>

          {/* Contact */}
          <div className="card p-5">
            <h3 className="font-semibold text-slate-900 text-sm mb-4">Contact Information</h3>
            <div className="space-y-3">
              {[
                { icon: MapPin, v: vendor.address   },
                { icon: Phone,  v: vendor.contact   },
                { icon: Mail,   v: vendor.email     },
                { icon: Globe,  v: vendor.website   },
              ].map((c, i) => {
                const Icon = c.icon
                return (
                  <div key={i} className="flex items-start gap-3">
                    <Icon size={15} className="text-slate-400 flex-shrink-0 mt-0.5" />
                    <span className="text-sm text-slate-700">{c.v}</span>
                  </div>
                )
              })}
            </div>
          </div>

          {/* Bank */}
          <div className="card p-5">
            <h3 className="font-semibold text-slate-900 text-sm mb-4">Bank Details</h3>
            <dl className="space-y-3">
              {[
                { l:'Bank Name',     v: vendor.bank    },
                { l:'IFSC Code',     v: vendor.ifsc    },
                { l:'Account No.',   v: '•••••• ' + vendor.account.slice(-4) },
                { l:'Branch',        v: vendor.branch  },
              ].map(r => (
                <div key={r.l} className="flex items-center justify-between py-1.5 border-b border-surface-50 last:border-0">
                  <dt className="text-xs text-slate-500 font-medium">{r.l}</dt>
                  <dd className="text-sm text-slate-900">{r.v}</dd>
                </div>
              ))}
            </dl>
          </div>
        </div>
      )}

      {tab === 'Purchase Orders' && (
        <div className="card overflow-hidden">
          <table className="data-table">
            <thead><tr><th>PO Number</th><th>Project</th><th>Value</th><th>Status</th><th>Date</th></tr></thead>
            <tbody>
              {vendor.recentPOs.map(po => (
                <tr key={po.id}>
                  <td><Link to={`/purchase-orders/${po.id}`} className="font-semibold text-brand-600 hover:text-brand-700">{po.id}</Link></td>
                  <td className="text-slate-600">{po.project}</td>
                  <td className="font-semibold text-slate-900">{po.value}</td>
                  <td><span className={`badge ${statusBadge[po.status] || 'badge-slate'}`}>{po.status}</span></td>
                  <td className="text-xs text-slate-400">{po.date}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {tab === 'Tasks' && (
        <div className="card overflow-hidden">
          <table className="data-table">
            <thead><tr><th>#</th><th>Task</th><th>Status</th><th>Due Date</th></tr></thead>
            <tbody>
              {vendor.tasks.map(t => (
                <tr key={t.id}>
                  <td className="text-slate-400 text-xs">{t.id}</td>
                  <td className="font-medium text-slate-800">{t.title}</td>
                  <td><span className={`badge ${taskBadge[t.status]}`}>{t.status}</span></td>
                  <td className="text-xs text-slate-400">{t.due}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {tab === 'Documents' && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {vendor.docs.map((d, i) => (
            <div key={i} className="card p-4 flex items-center gap-3 hover:shadow-card-hover transition-all cursor-pointer group">
              <div className="w-10 h-10 rounded-xl bg-brand-50 border border-brand-100 flex items-center justify-center flex-shrink-0">
                <FileText size={18} className="text-brand-500" />
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-slate-900 truncate">{d.name}</p>
                <p className="text-xs text-slate-400 mt-0.5">{d.type} · Uploaded {d.date}</p>
              </div>
              <span className="badge badge-slate text-xs group-hover:badge-blue transition-colors">{d.type}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
