import { useState } from 'react';
import { BellRing, HeartHandshake, MapPinned, Sparkles, Truck } from 'lucide-react';
import {
  Area,
  AreaChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';

import ChartCard from '../components/dashboard/ChartCard';
import DashboardLayout from '../components/dashboard/DashboardLayout';
import DataTable from '../components/dashboard/DataTable';
import FilterBar from '../components/dashboard/FilterBar';
import SummaryCard from '../components/dashboard/SummaryCard';
import ErrorMessage from '../components/ui/ErrorMessage';
import StatusBadge from '../components/ui/StatusBadge';

const navItems = [
  { label: 'Overview', to: '/dashboard/user', icon: Sparkles },
  { label: 'My donations', to: '/dashboard/user', icon: HeartHandshake },
  { label: 'Pickups', to: '/dashboard/user', icon: Truck },
  { label: 'Alerts', to: '/dashboard/user', icon: BellRing },
  { label: 'Tracking', to: '/dashboard/user', icon: MapPinned },
];

const activitySeries = [
  { day: 'Mon', value: 12 },
  { day: 'Tue', value: 14 },
  { day: 'Wed', value: 8 },
  { day: 'Thu', value: 18 },
  { day: 'Fri', value: 15 },
  { day: 'Sat', value: 10 },
];

const rows = [
  { id: 1, request: 'Fresh fruit donation', window: 'Today, 4:30 PM', status: 'Awaiting pickup', owner: 'Local grocer' },
  { id: 2, request: 'Bakery surplus', window: 'Tomorrow, 9:00 AM', status: 'Ready', owner: 'Bakery partners' },
  { id: 3, request: 'Meal prep kits', window: 'Pending review', status: 'Needs confirmation', owner: 'Volunteer network' },
];

const filterItems = ['All', 'Ready', 'Awaiting pickup', 'Needs confirmation'];

function UserDashboard() {
  const [filter, setFilter] = useState('All');
  const backendAvailable = false;

  const visibleRows = filter === 'All' ? rows : rows.filter((row) => row.status === filter);

  return (
    <DashboardLayout title="User dashboard" subtitle="Track donations, pickups and service updates from a single workspace." roleLabel="User" navItems={navItems}>
      {backendAvailable ? null : (
        <ErrorMessage
          title="Connection state: backend unavailable"
          message="This dashboard is intentionally rendering a placeholder state until the API is live. No real donation data is being claimed at this stage."
        />
      )}

      <section className="grid gap-4 md:grid-cols-3">
        <SummaryCard label="My donation requests" value="Waiting for sync" detail="Pending" tone="emerald" icon={HeartHandshake} />
        <SummaryCard label="Upcoming pickups" value="Not available yet" detail="Unscheduled" tone="amber" icon={Truck} />
        <SummaryCard label="Feedback queue" value="No live events" detail="No backend" tone="slate" icon={BellRing} />
      </section>

      <section className="grid gap-6 xl:grid-cols-[1.2fr_0.8fr]">
        <ChartCard title="Participation trend" description="Placeholder trend view while the backend is still being connected." action={<StatusBadge label="Preview only" variant="neutral" />}>
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={activitySeries}>
              <defs>
                <linearGradient id="userTrendFill" x1="0" x2="0" y1="0" y2="1">
                  <stop offset="5%" stopColor="#10b981" stopOpacity={0.4} />
                  <stop offset="95%" stopColor="#10b981" stopOpacity={0.05} />
                </linearGradient>
              </defs>
              <CartesianGrid stroke="#e2e8f0" strokeDasharray="4 4" vertical={false} />
              <XAxis dataKey="day" axisLine={false} tickLine={false} tick={{ fill: '#475569', fontSize: 12 }} />
              <YAxis axisLine={false} tickLine={false} tick={{ fill: '#475569', fontSize: 12 }} />
              <Tooltip />
              <Area type="monotone" dataKey="value" stroke="#10b981" fill="url(#userTrendFill)" strokeWidth={3} />
            </AreaChart>
          </ResponsiveContainer>
        </ChartCard>

        <div className="rounded-[28px] border border-slate-200 bg-slate-900 p-6 text-white shadow-sm">
          <p className="text-sm uppercase tracking-[0.2em] text-emerald-300">User workflow</p>
          <h3 className="mt-3 text-2xl font-bold">Prepared for donation, pickup and tracking modules</h3>
          <ul className="mt-5 space-y-3 text-sm text-slate-200">
            <li>• Capture donation intent and pickup preferences</li>
            <li>• Monitor cargo status and fulfillment notes</li>
            <li>• Review feedback and volunteer coordination updates</li>
          </ul>
        </div>
      </section>

      <section className="space-y-4 rounded-[28px] border border-slate-200 bg-white p-6 shadow-sm">
        <div className="flex flex-col gap-3 lg:flex-row lg:items-center lg:justify-between">
          <div>
            <h2 className="text-xl font-semibold text-slate-900">Donation activity</h2>
            <p className="text-sm text-slate-500">This list is a placeholder for future user-request operations.</p>
          </div>
          <FilterBar items={filterItems} activeItem={filter} onChange={setFilter} />
        </div>

        <DataTable
          columns={[
            { key: 'request', label: 'Request' },
            { key: 'window', label: 'Pickup window' },
            { key: 'owner', label: 'Partner' },
            {
              key: 'status',
              label: 'Status',
              render: (row) => <StatusBadge label={row.status} variant={row.status === 'Ready' ? 'success' : row.status === 'Awaiting pickup' ? 'warning' : 'neutral'} />,
            },
          ]}
          rows={visibleRows}
          emptyTitle="No user actions queued yet"
          emptyDescription="When the API is connected, donation and pickup records will appear here."
        />
      </section>
    </DashboardLayout>
  );
}

export default UserDashboard;
