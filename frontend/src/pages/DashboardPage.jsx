import { ArrowUpRight, Bell, Boxes, HandHeart, TrendingUp } from 'lucide-react';

import Sidebar from '../components/layout/Sidebar';
import StatusBadge from '../components/ui/StatusBadge';

const cards = [
  { label: 'Inventory alerts', value: '02 pending', icon: Boxes, tone: 'emerald' },
  { label: 'Donations ready', value: '08 requests', icon: HandHeart, tone: 'amber' },
  { label: 'Forecast health', value: 'Stable', icon: TrendingUp, tone: 'slate' },
];

function DashboardPage() {
  return (
    <div className="flex gap-6 py-4">
      <Sidebar />

      <div className="flex-1 space-y-6">
        <section className="rounded-[28px] border border-slate-200 bg-white p-6 shadow-sm">
          <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <p className="text-sm uppercase tracking-[0.2em] text-emerald-700">Overview</p>
              <h1 className="mt-2 text-3xl font-bold text-slate-900">Operations dashboard</h1>
            </div>
            <div className="flex items-center gap-2 rounded-full bg-slate-100 px-3 py-2 text-sm text-slate-700">
              <Bell size={16} />
              3 updates this week
            </div>
          </div>
        </section>

        <section className="grid gap-4 md:grid-cols-3">
          {cards.map(({ label, value, icon: Icon, tone }) => (
            <div key={label} className="rounded-[24px] border border-slate-200 bg-white p-5 shadow-sm">
              <div className="flex items-center justify-between">
                <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-emerald-100 text-emerald-700">
                  <Icon size={18} />
                </div>
                <ArrowUpRight size={18} className="text-slate-400" />
              </div>
              <p className="mt-5 text-sm text-slate-500">{label}</p>
              <p className="mt-2 text-2xl font-bold text-slate-900">{value}</p>
              <div className="mt-4">
                <StatusBadge label="Preview" variant={tone === 'emerald' ? 'success' : tone === 'amber' ? 'warning' : 'neutral'} />
              </div>
            </div>
          ))}
        </section>

        <section className="grid gap-6 xl:grid-cols-[1.1fr_0.9fr]">
          <div className="rounded-[28px] border border-slate-200 bg-white p-6 shadow-sm">
            <h2 className="text-xl font-semibold text-slate-900">Donor activity summary</h2>
            <div className="mt-5 space-y-4">
              {[
                { label: 'Fresh produce', status: 'Ready to dispatch', variant: 'success' },
                { label: 'Bakery surplus', status: 'Needs review', variant: 'warning' },
                { label: 'Prepared meals', status: 'Queued', variant: 'neutral' },
              ].map(({ label, status, variant }) => (
                <div key={label} className="flex items-center justify-between rounded-2xl bg-slate-50 px-4 py-3">
                  <div>
                    <p className="font-medium text-slate-800">{label}</p>
                    <p className="text-sm text-slate-500">Last updated today</p>
                  </div>
                  <StatusBadge label={status} variant={variant} />
                </div>
              ))}
            </div>
          </div>

          <div className="rounded-[28px] border border-slate-200 bg-slate-900 p-6 text-white shadow-sm">
            <p className="text-sm uppercase tracking-[0.2em] text-emerald-300">Summary</p>
            <h2 className="mt-3 text-2xl font-bold">This module is ready for operational detail work</h2>
            <p className="mt-4 text-slate-300">
              Additional features such as charts, donation tables, logistics, and user actions will be added in the next development cycle.
            </p>
          </div>
        </section>
      </div>
    </div>
  );
}

export default DashboardPage;
