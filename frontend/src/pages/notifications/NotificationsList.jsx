import React, { useState } from 'react'
import { Bell, CheckCircle, AlertTriangle, Info, Trash2 } from 'lucide-react'

const mockNotifs = [
  { id:1, title:'PO-2024-089 approved by Finance',          body:'Purchase order for Tata Projects has been approved. Value: ₹28.9L', type:'success', time:'15 Jun 2024, 10:42 AM', read:false },
  { id:2, title:'Delivery overdue: DEL-2024-040',           body:'BHEL Heavy Equipment delivery is 7 days overdue. Immediate action required.', type:'error', time:'15 Jun 2024, 9:00 AM', read:false },
  { id:3, title:'Vendor Siemens submitted documents',        body:'New compliance documents uploaded for review under VND-003.', type:'info', time:'14 Jun 2024, 4:30 PM', read:false },
  { id:4, title:'Payment PAY-2024-084-1 processed',         body:'Advance payment of ₹26.4L to BHEL has been transferred via RTGS.', type:'success', time:'14 Jun 2024, 2:15 PM', read:true },
  { id:5, title:'GST registration expiring soon — VND-005', body:'Havells Infra Pvt Ltd GST certificate expires in 15 days.', type:'warning', time:'13 Jun 2024, 11:00 AM', read:true },
]

const typeIcon = {
  success: { Icon: CheckCircle, cls: 'text-emerald-600 bg-emerald-50' },
  error:   { Icon: AlertTriangle, cls: 'text-red-600 bg-red-50'       },
  warning: { Icon: AlertTriangle, cls: 'text-amber-600 bg-amber-50'   },
  info:    { Icon: Info,          cls: 'text-blue-600 bg-blue-50'      },
}

export default function NotificationsList() {
  const [notifs, setNotifs] = useState(mockNotifs)
  const markAllRead = () => setNotifs(n => n.map(x => ({ ...x, read:true })))
  const deleteOne = (id) => setNotifs(n => n.filter(x => x.id !== id))

  return (
    <div className="space-y-6 pb-4">
      <div className="page-header">
        <div>
          <h2 className="page-title">Notifications</h2>
          <p className="page-subtitle">{notifs.filter(n=>!n.read).length} unread</p>
        </div>
        <button onClick={markAllRead} className="btn-secondary text-xs">Mark all as read</button>
      </div>
      <div className="space-y-2 max-w-2xl">
        {notifs.map(n => {
          const { Icon, cls } = typeIcon[n.type]
          return (
            <div key={n.id} className={`card p-4 flex items-start gap-4 transition-all ${!n.read ? 'border-brand-200 bg-brand-50/20' : ''}`}>
              <div className={`w-9 h-9 rounded-xl ${cls} flex items-center justify-center flex-shrink-0 mt-0.5`}>
                <Icon size={16} />
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-start justify-between gap-2">
                  <p className={`text-sm ${!n.read ? 'font-bold text-slate-900' : 'font-medium text-slate-700'}`}>{n.title}</p>
                  {!n.read && <div className="w-2 h-2 rounded-full bg-brand-500 flex-shrink-0 mt-1.5" />}
                </div>
                <p className="text-xs text-slate-500 mt-1">{n.body}</p>
                <p className="text-xs text-slate-300 mt-1.5">{n.time}</p>
              </div>
              <button onClick={() => deleteOne(n.id)} className="p-1.5 rounded-lg text-slate-300 hover:text-red-400 hover:bg-red-50 transition-colors flex-shrink-0">
                <Trash2 size={14} />
              </button>
            </div>
          )
        })}
        {notifs.length === 0 && (
          <div className="card p-12 text-center text-slate-400">
            <Bell size={32} className="mx-auto mb-3 opacity-30" />
            <p className="text-sm">You're all caught up!</p>
          </div>
        )}
      </div>
    </div>
  )
}
