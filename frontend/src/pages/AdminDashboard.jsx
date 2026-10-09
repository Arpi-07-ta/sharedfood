import { useState } from 'react';
import { Activity, BarChart3, BellRing, ShieldCheck, Users } from 'lucide-react';
import { Link } from 'react-router-dom';
import {
  Bar,
  BarChart,
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
  { label: 'Overview', to: '/dashboard/admin', icon: Activity },
  { label: 'Platform', to: '/dashboard/admin', icon: ShieldCheck },
  { label: 'Users', to: '/dashboard/admin', icon: Users },
  { label: 'Fraud alerts', to: '/admin/fraud-alerts', icon: BellRing },
  { label: 'NGO verification', to: '/admin/ngo-verifications', icon: ShieldCheck },
  { label: 'Notifications', to: '/dashboard/admin', icon: BellRing },
  { label: 'Analytics', to: '/dashboard/admin', icon: BarChart3 },
];

const healthSeries = [
  { label: 'Mon', value: 68 },
  { label: 'Tue', value: 71 },
  { label: 'Wed', value: 67 },
  { label: 'Thu', value: 74 },
  { label: 'Fri', value: 79 },
  { label: 'Sat', value: 72 },
];

const rows = [
  { id: 1, entity: 'Donation moderation', owner: 'Operations team', status: 'Monitoring', severity: 'Medium' },
  { id: 2, entity: 'Volunteer access', owner: 'Admin review', status: 'Needs review', severity: 'High' },
  { id: 3, entity: 'Partner onboarding', owner: 'Community team', status: 'Stable', severity: 'Low' },
];

const filterItems = ['All', 'Monitoring', 'Needs review', 'Stable'];

function AdminDashboard() {
  const [filter, setFilter] = useState('All');
  const backendAvailable = false;

  const visibleRows = filter === 'All' ? rows : rows.filter((row) => row.status === filter);

  return (
    <DashboardLayout title="Admin dashboard" subtitle="Operate platform health, security review, partner governance and system insights." roleLabel="Admin" navItems={navItems}>
      {backendAvailable ? null : (
        <ErrorMessage
          title="Connection state: admin analytics unavailable"
          message="This admin dashboard is intentionally in a safe placeholder state until the backend metrics and audit APIs are available."
        />
      )}

      <section className="grid gap-4 md:grid-cols-3">
        <SummaryCard label="Platform health" value="Waiting for telemetry" detail="Offline" tone="emerald" icon={Activity} />
        <SummaryCard label="Flagged reviews" value="Review risk queue" detail="Admin-only" tone="amber" icon={BellRing} />
        <SummaryCard label="User access" value="Pending sync" detail="Not yet verified" tone="slate" icon={Users} />
      </section>
      <div className="-mt-2">
        <Link to="/admin/fraud-alerts" className="inline-flex items-center gap-2 rounded-xl bg-rose-700 px-4 py-2 text-sm font-semibold text-white hover:bg-rose-800">
          <BellRing size={16} /> Open fraud-alert review queue
        </Link>
        <Link to="/admin/ngo-verifications" className="ml-2 inline-flex items-center gap-2 rounded-xl bg-emerald-700 px-4 py-2 text-sm font-semibold text-white hover:bg-emerald-800">
          <ShieldCheck size={16} /> Review NGO applications
        </Link>
      </div>

      <section className="grid gap-6 xl:grid-cols-[1.2fr_0.8fr]">
        <ChartCard title="Operational health" description="Placeholder analytics for system monitoring, audit events and governance checks." action={<StatusBadge label="Preview" variant="neutral" />}>
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={healthSeries}>
              <CartesianGrid stroke="#e2e8f0" strokeDasharray="4 4" vertical={false} />
              <XAxis dataKey="label" axisLine={false} tickLine={false} tick={{ fill: '#475569', fontSize: 12 }} />
              <YAxis axisLine={false} tickLine={false} tick={{ fill: '#475569', fontSize: 12 }} />
              <Tooltip />
              <Bar dataKey="value" radius={[8, 8, 0, 0]} fill="#8b5cf6" />
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>

        <div className="rounded-[28px] border border-violet-100 bg-violet-50 p-6 shadow-sm">
          <p className="text-sm uppercase tracking-[0.2em] text-violet-700">Admin ops</p>
          <h3 className="mt-3 text-xl font-semibold text-slate-900">Governance checklist</h3>
          <ul className="mt-4 space-y-3 text-sm text-slate-700">
            <li>• Review partner and user access controls</li>
            <li>• Manage incident queues and platform alerts</li>
            <li>• Monitor platform health throughout the service lifecycle</li>
          </ul>
        </div>
      </section>

      <section className="space-y-4 rounded-[28px] border border-slate-200 bg-white p-6 shadow-sm">
        <div className="flex flex-col gap-3 lg:flex-row lg:items-center lg:justify-between">
          <div>
            <h2 className="text-xl font-semibold text-slate-900">Monitoring board</h2>
            <p className="text-sm text-slate-500">Placeholder governance table for recurring reviews and system checks.</p>
          </div>
          <FilterBar items={filterItems} activeItem={filter} onChange={setFilter} />
        </div>

        <DataTable
          columns={[
            { key: 'entity', label: 'Review item' },
            { key: 'owner', label: 'Owner' },
            { key: 'severity', label: 'Severity' },
            {
              key: 'status',
              label: 'Status',
              render: (row) => <StatusBadge label={row.status} variant={row.status === 'Monitoring' ? 'success' : row.status === 'Needs review' ? 'warning' : 'neutral'} />,
            },
          ]}
          rows={visibleRows}
          emptyTitle="No admin review items available"
          emptyDescription="Live audit events and user governance data will populate this list once the API is connected."
        />
      </section>
    </DashboardLayout>
  );
}

export default AdminDashboard;
