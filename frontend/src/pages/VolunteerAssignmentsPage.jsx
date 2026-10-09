import { useCallback, useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { MapPinned, PackageCheck, Truck } from 'lucide-react';

import trackingApi from '../api/tracking';
import DashboardLayout from '../components/dashboard/DashboardLayout';

const navItems = [
  { label: 'Overview', to: '/dashboard/volunteer', icon: PackageCheck },
  { label: 'Pickup board', to: '/volunteer/pickups', icon: Truck },
];
const statusTone = {
  SCHEDULED: 'bg-amber-100 text-amber-800', ACCEPTED: 'bg-blue-100 text-blue-800',
  IN_TRANSIT: 'bg-indigo-100 text-indigo-800', PICKED_UP: 'bg-violet-100 text-violet-800',
  DELIVERED: 'bg-emerald-100 text-emerald-800', CANCELLED: 'bg-slate-100 text-slate-600',
};

function PickupCard({ pickup, available = false, onAccept, busy }) {
  return <article className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
    <div className="flex flex-wrap items-start justify-between gap-3">
      <div><h3 className="text-lg font-semibold text-slate-900">{pickup.donation_name}</h3><p className="mt-1 text-sm text-slate-600">{pickup.quantity} {pickup.unit} · {pickup.ngo_name}</p><p className="mt-2 text-sm text-slate-600">Pickup window: {new Date(pickup.pickup_window_start).toLocaleString()} – {new Date(pickup.pickup_window_end).toLocaleString()}</p><p className="mt-2 flex items-center gap-1 text-sm text-slate-600"><MapPinned size={15} />{pickup.pickup_address}</p><p className="mt-1 rounded-lg bg-slate-50 p-2 text-xs text-slate-500">Map unavailable: no map integration is configured. Use the pickup address above.</p></div>
      <div className="flex flex-col items-end gap-2"><span className={`rounded-full px-3 py-1 text-xs font-semibold ${statusTone[pickup.status] || statusTone.SCHEDULED}`}>{pickup.status.replaceAll('_', ' ')}</span>{available ? <button type="button" onClick={() => onAccept(pickup.id)} disabled={busy} className="rounded-xl bg-sky-700 px-4 py-2 text-sm font-semibold text-white disabled:bg-slate-300">{busy ? 'Accepting…' : 'Accept pickup'}</button> : <Link to={`/volunteer/pickups/${pickup.id}`} className="rounded-xl border border-slate-300 px-4 py-2 text-sm font-semibold text-slate-700">Details & timeline</Link>}</div>
    </div>
  </article>;
}

function VolunteerAssignmentsPage() {
  const [assignments, setAssignments] = useState([]);
  const [available, setAvailable] = useState([]);
  const [loading, setLoading] = useState(true);
  const [busyId, setBusyId] = useState(null);
  const [error, setError] = useState('');
  const [notice, setNotice] = useState('');

  const load = useCallback(async () => {
    setError('');
    try {
      const [assignedResponse, availableResponse] = await Promise.all([trackingApi.assignments(), trackingApi.available()]);
      setAssignments(assignedResponse.data.results || assignedResponse.data);
      setAvailable(availableResponse.data.results || availableResponse.data);
    } catch (requestError) {
      setError(requestError.response?.data?.detail || 'Could not load pickup assignments.');
    } finally { setLoading(false); }
  }, []);
  useEffect(() => { load(); }, [load]);

  const accept = async (pickupId) => {
    setBusyId(pickupId);
    try {
      await trackingApi.accept(pickupId);
      setNotice('Pickup assigned to you. Open the details to update its status and timeline.');
      await load();
    } catch (requestError) {
      setError(requestError.response?.data?.detail || 'This pickup may already be assigned.');
    } finally { setBusyId(null); }
  };

  return <DashboardLayout title="Pickup assignments" subtitle="Claim unassigned scheduled pickups or update only the work assigned to you." roleLabel="Volunteer" navItems={navItems}>
    {error && <p role="alert" className="mb-4 rounded-xl bg-rose-50 p-3 text-sm text-rose-700">{error}</p>}{notice && <p role="status" className="mb-4 rounded-xl bg-emerald-50 p-3 text-sm text-emerald-800">{notice}</p>}
    {loading ? <p className="rounded-2xl border bg-white p-6 text-slate-500">Loading pickups…</p> : <div className="space-y-8">
      <section><h2 className="mb-3 text-xl font-semibold text-slate-900">Assigned to me</h2><div className="space-y-3">{assignments.length ? assignments.map((pickup) => <PickupCard key={pickup.id} pickup={pickup} />) : <p className="rounded-xl border border-dashed p-5 text-sm text-slate-500">No assigned pickups yet.</p>}</div></section>
      <section><h2 className="mb-3 text-xl font-semibold text-slate-900">Available to claim</h2><div className="space-y-3">{available.length ? available.map((pickup) => <PickupCard key={pickup.id} pickup={pickup} available onAccept={accept} busy={busyId === pickup.id} />) : <p className="rounded-xl border border-dashed p-5 text-sm text-slate-500">No unassigned pickups are available.</p>}</div></section>
    </div>}
  </DashboardLayout>;
}

export default VolunteerAssignmentsPage;
