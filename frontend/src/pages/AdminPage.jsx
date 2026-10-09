import { ShieldCheck } from 'lucide-react';

import StatusBadge from '../components/ui/StatusBadge';

const rows = [
  { name: 'Warehouse check-in', owner: 'Operations', status: 'Healthy' },
  { name: 'Donation priority list', owner: 'Programs', status: 'Review' },
  { name: 'Partner access review', owner: 'Admin', status: 'Approved' },
];

function AdminPage() {
  return (
    <div className="mx-auto max-w-5xl py-6">
      <div className="rounded-[30px] border border-slate-200 bg-white p-6 shadow-sm">
        <div className="flex items-center gap-3">
          <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-emerald-100 text-emerald-700">
            <ShieldCheck size={22} />
          </div>
          <div>
            <p className="text-sm uppercase tracking-[0.2em] text-emerald-700">Admin</p>
            <h1 className="text-3xl font-bold text-slate-900">Role-based access preview</h1>
          </div>
        </div>

        <div className="mt-8 overflow-hidden rounded-2xl border border-slate-200">
          <table className="min-w-full divide-y divide-slate-200 text-left">
            <thead className="bg-slate-50">
              <tr>
                <th className="px-4 py-3 text-sm font-semibold text-slate-700">Process</th>
                <th className="px-4 py-3 text-sm font-semibold text-slate-700">Owner</th>
                <th className="px-4 py-3 text-sm font-semibold text-slate-700">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-200 bg-white">
              {rows.map(({ name, owner, status }) => (
                <tr key={name}>
                  <td className="px-4 py-3 text-sm text-slate-800">{name}</td>
                  <td className="px-4 py-3 text-sm text-slate-600">{owner}</td>
                  <td className="px-4 py-3">
                    <StatusBadge
                      label={status}
                      variant={status === 'Healthy' ? 'success' : status === 'Review' ? 'warning' : 'neutral'}
                    />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

export default AdminPage;
