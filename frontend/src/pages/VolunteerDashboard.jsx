import { useCallback, useEffect, useState } from 'react';
import { Clock3, MapPinned, Save, Sparkles, Truck } from 'lucide-react';
import { Link } from 'react-router-dom';

import trackingApi from '../api/tracking';
import DashboardLayout from '../components/dashboard/DashboardLayout';

const navItems = [
  { label: 'Overview', to: '/dashboard/volunteer', icon: Sparkles },
  { label: 'Assigned pickups', to: '/volunteer/pickups', icon: Truck },
];
const statusTone = {
  SCHEDULED: 'bg-amber-100 text-amber-800',
  ACCEPTED: 'bg-blue-100 text-blue-800',
  IN_TRANSIT: 'bg-indigo-100 text-indigo-800',
  PICKED_UP: 'bg-violet-100 text-violet-800',
  DELIVERED: 'bg-emerald-100 text-emerald-800',
  CANCELLED: 'bg-slate-100 text-slate-600',
};

function VolunteerDashboard() {
  const [profile, setProfile] = useState(null);
  const [assignments, setAssignments] = useState([]);
  const [available, setAvailable] = useState([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [notice, setNotice] = useState('');

  const load = useCallback(async () => {
    setError('');
    try {
      const [profileResponse, assignmentsResponse, availableResponse] = await Promise.all([
        trackingApi.volunteerProfile(), trackingApi.assignments(), trackingApi.available(),
      ]);
      setProfile(profileResponse.data);
      setAssignments(assignmentsResponse.data.results || assignmentsResponse.data);
      setAvailable(availableResponse.data.results || availableResponse.data);
    } catch (requestError) {
      setError(requestError.response?.status === 403 ? 'Your volunteer profile is inactive. Contact an administrator.' : 'Could not load volunteer assignments.');
    } finally { setLoading(false); }
  }, []);

  useEffect(() => { load(); }, [load]);

  const saveProfile = async (event) => {
    event.preventDefault();
    setSaving(true);
    setError('');
    try {
      const { data } = await trackingApi.updateVolunteerProfile(profile);
      setProfile(data);
      setNotice('Availability profile saved.');
    } catch (requestError) {
      setError(requestError.response?.data?.detail || 'Could not update volunteer availability.');
    } finally { setSaving(false); }
  };

  if (loading || !profile) return <DashboardLayout title="Volunteer dashboard" subtitle="Pickup assignment and delivery workspace." roleLabel="Volunteer" navItems={navItems}><p className="rounded-2xl border bg-white p-6 text-slate-500">Loading volunteer workspace…</p></DashboardLayout>;

  return (
    <DashboardLayout title="Volunteer dashboard" subtitle="Manage availability and safely track assigned pickups from collection to delivery." roleLabel="Volunteer" navItems={navItems}>
      {error && <p role="alert" className="mb-4 rounded-xl bg-rose-50 p-3 text-sm text-rose-700">{error}</p>}
      {notice && <p role="status" className="mb-4 rounded-xl bg-emerald-50 p-3 text-sm text-emerald-800">{notice}</p>}
      <section className="grid gap-3 sm:grid-cols-3">
        {[['Assigned', assignments.length], ['Unassigned nearby', available.length], ['Delivered', assignments.filter((item) => item.status === 'DELIVERED').length]].map(([label, count]) => <div key={label} className="rounded-2xl border border-slate-200 bg-white p-4"><p className="text-xs font-semibold uppercase tracking-wide text-slate-500">{label}</p><p className="mt-2 text-2xl font-bold text-slate-900">{count}</p></div>)}
      </section>

      <section className="mt-6 rounded-[28px] border border-slate-200 bg-white p-6 shadow-sm">
        <div className="mb-4"><p className="text-sm font-semibold uppercase tracking-[0.2em] text-sky-700">Volunteer profile</p><h2 className="mt-2 text-xl font-semibold text-slate-900">Availability and service area</h2></div>
        <form onSubmit={saveProfile} className="grid gap-4 md:grid-cols-2">
          <label className="text-sm font-medium text-slate-700">Availability<textarea rows={3} value={profile.availability || ''} onChange={(event) => setProfile({ ...profile, availability: event.target.value })} placeholder="Weekdays after 3pm, weekends…" className="mt-1 w-full rounded-xl border border-slate-300 px-3 py-2" /></label>
          <label className="text-sm font-medium text-slate-700">Skills<textarea rows={3} value={profile.skills || ''} onChange={(event) => setProfile({ ...profile, skills: event.target.value })} placeholder="Driving, food handling, cold-chain…" className="mt-1 w-full rounded-xl border border-slate-300 px-3 py-2" /></label>
          <label className="text-sm font-medium text-slate-700">City<input value={profile.city || ''} onChange={(event) => setProfile({ ...profile, city: event.target.value })} className="mt-1 w-full rounded-xl border border-slate-300 px-3 py-2" /></label>
          <label className="text-sm font-medium text-slate-700">State / region<input value={profile.state || ''} onChange={(event) => setProfile({ ...profile, state: event.target.value })} className="mt-1 w-full rounded-xl border border-slate-300 px-3 py-2" /></label>
          <p className="text-xs text-slate-500">Volunteer activation is administrator-managed.</p>
          <button type="submit" disabled={saving} className="inline-flex justify-center gap-2 rounded-xl bg-sky-700 px-4 py-2 text-sm font-semibold text-white disabled:bg-slate-300"><Save size={16} />{saving ? 'Saving…' : 'Save availability'}</button>
        </form>
      </section>

      <section className="mt-6 rounded-[28px] border border-slate-200 bg-white p-6 shadow-sm">
        <div className="flex flex-wrap items-center justify-between gap-3"><div><h2 className="text-xl font-semibold text-slate-900">Next assigned pickups</h2><p className="mt-1 text-sm text-slate-600">Only pickups assigned to your account can be updated.</p></div><Link to="/volunteer/pickups" className="rounded-xl bg-sky-700 px-4 py-2 text-sm font-semibold text-white">Open pickup board</Link></div>
        <div className="mt-4 space-y-3">{assignments.slice(0, 4).map((pickup) => <Link key={pickup.id} to={`/volunteer/pickups/${pickup.id}`} className="flex flex-wrap items-center justify-between gap-3 rounded-xl border border-slate-200 p-4 hover:border-sky-300"><div><p className="font-semibold text-slate-900">{pickup.donation_name} · {pickup.ngo_name}</p><p className="mt-1 flex items-center gap-1 text-sm text-slate-600"><Clock3 size={14} />{new Date(pickup.pickup_window_start).toLocaleString()}</p><p className="mt-1 flex items-center gap-1 text-xs text-slate-500"><MapPinned size={13} />{pickup.pickup_address}</p></div><span className={`rounded-full px-3 py-1 text-xs font-semibold ${statusTone[pickup.status] || statusTone.SCHEDULED}`}>{pickup.status.replaceAll('_', ' ')}</span></Link>)}{assignments.length === 0 && <p className="rounded-xl border border-dashed border-slate-300 p-5 text-center text-sm text-slate-500">No assigned pickups yet. Browse unassigned pickups on the pickup board.</p>}</div>
      </section>
    </DashboardLayout>
  );
}

export default VolunteerDashboard;
