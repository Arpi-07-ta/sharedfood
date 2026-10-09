import { useCallback, useEffect, useState } from 'react';
import { ArrowLeft, CheckCircle2, MapPinned, PackageCheck } from 'lucide-react';
import { Link, useParams } from 'react-router-dom';

import trackingApi from '../api/tracking';
import DashboardLayout from '../components/dashboard/DashboardLayout';

const navItems = [
  { label: 'Overview', to: '/dashboard/volunteer', icon: Truck },
  { label: 'Pickup board', to: '/volunteer/pickups', icon: PackageCheck },
];
const nextActions = {
  ACCEPTED: ['IN_TRANSIT', 'CANCELLED'],
  IN_TRANSIT: ['PICKED_UP', 'CANCELLED'],
  PICKED_UP: ['DELIVERED'],
};
const titles = { ACCEPTED: 'Start route', IN_TRANSIT: 'Confirm collection', PICKED_UP: 'Confirm delivery' };

function PickupDetailsPage() {
  const { id } = useParams();
  const [pickup, setPickup] = useState(null);
  const [note, setNote] = useState('');
  const [proof, setProof] = useState(null);
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const [notice, setNotice] = useState('');

  const load = useCallback(async () => {
    setError('');
    try { const { data } = await trackingApi.detail(id); setPickup(data); }
    catch (requestError) { setError(requestError.response?.data?.detail || 'Could not load pickup details.'); }
    finally { setLoading(false); }
  }, [id]);
  useEffect(() => { load(); }, [load]);

  const updateStatus = async (nextStatus) => {
    setBusy(true);
    setError('');
    setNotice('');
    try {
      let payload = { status: nextStatus, note };
      if (nextStatus === 'DELIVERED' && proof) {
        payload = new FormData();
        payload.append('status', nextStatus);
        payload.append('note', note);
        payload.append('proof_file', proof);
      }
      const { data } = await trackingApi.updateStatus(id, payload);
      setPickup(data);
      setNote('');
      setProof(null);
      setNotice(`${nextStatus.replaceAll('_', ' ')} recorded and added to the tracking timeline.`);
    } catch (requestError) {
      setError(requestError.response?.data?.detail || requestError.response?.data?.proof_file?.[0] || 'Could not update pickup status.');
    } finally { setBusy(false); }
  };

  const downloadProof = async () => {
    try {
      const { data } = await trackingApi.proof(id);
      const objectUrl = URL.createObjectURL(data);
      const link = document.createElement('a');
      link.href = objectUrl;
      link.download = `delivery-proof-${id}`;
      link.click();
      URL.revokeObjectURL(objectUrl);
    } catch {
      setError('Could not download delivery proof.');
    }
  };

  const actions = pickup ? nextActions[pickup.status] || [] : [];
  return <DashboardLayout title="Pickup details" subtitle="Pickup status changes are permission-checked and recorded in a permanent timeline." roleLabel="Volunteer" navItems={navItems}>
    <Link to="/volunteer/pickups" className="mb-4 inline-flex items-center gap-2 text-sm font-semibold text-sky-700"><ArrowLeft size={16} />Back to pickup board</Link>
    {error && <p role="alert" className="mb-4 rounded-xl bg-rose-50 p-3 text-sm text-rose-700">{error}</p>}{notice && <p role="status" className="mb-4 rounded-xl bg-emerald-50 p-3 text-sm text-emerald-800">{notice}</p>}
    {loading || !pickup ? <p className="rounded-2xl border bg-white p-6 text-slate-500">Loading pickup…</p> : <div className="space-y-5">
      <section className="rounded-[28px] border border-slate-200 bg-white p-6 shadow-sm">
        <div className="flex flex-wrap items-start justify-between gap-4"><div><p className="text-xs font-semibold uppercase tracking-[0.18em] text-sky-700">{pickup.ngo_name}</p><h2 className="mt-2 text-2xl font-bold text-slate-900">{pickup.donation_name}</h2><p className="mt-1 text-slate-600">{pickup.quantity} {pickup.unit}</p></div><span className="rounded-full bg-sky-100 px-3 py-1 text-sm font-semibold text-sky-800">{pickup.status.replaceAll('_', ' ')}</span></div>
        <div className="mt-5 grid gap-4 md:grid-cols-2"><div className="rounded-xl bg-slate-50 p-4"><p className="text-xs font-semibold uppercase text-slate-500">Pickup address</p><p className="mt-2 flex gap-2 text-sm text-slate-800"><MapPinned size={16} className="shrink-0" />{pickup.pickup_address}</p><p className="mt-2 text-xs text-slate-500">Map unavailable: no map integration is configured. Use the address and confirm route details with the NGO.</p></div><div className="rounded-xl bg-slate-50 p-4"><p className="text-xs font-semibold uppercase text-slate-500">Pickup window</p><p className="mt-2 text-sm text-slate-800">{new Date(pickup.pickup_window_start).toLocaleString()} – {new Date(pickup.pickup_window_end).toLocaleString()}</p><p className="mt-2 text-xs text-slate-500">Assigned volunteer updates are limited to this pickup's assignee.</p></div></div>
      </section>

      <section className="rounded-[28px] border border-slate-200 bg-white p-6 shadow-sm"><h2 className="text-xl font-semibold text-slate-900">Pickup status update</h2>{actions.length === 0 ? <p className="mt-2 text-sm text-slate-500">This pickup has no remaining volunteer status actions.</p> : <div className="mt-4 space-y-4"><label className="block text-sm font-medium text-slate-700">Field note<textarea value={note} onChange={(event) => setNote(event.target.value)} rows={3} className="mt-1 w-full rounded-xl border border-slate-300 px-3 py-2" placeholder="Optional collection or delivery notes" /></label>{pickup.status === 'PICKED_UP' && <label className="block text-sm font-medium text-slate-700">Delivery proof (optional PDF/JPEG/PNG, max 10 MB)<input type="file" accept="application/pdf,image/jpeg,image/png" onChange={(event) => setProof(event.target.files?.[0] || null)} className="mt-1 block w-full text-sm" /></label>}<div className="flex flex-wrap gap-2">{actions.map((action) => <button key={action} type="button" disabled={busy} onClick={() => updateStatus(action)} className={`rounded-xl px-4 py-2 text-sm font-semibold text-white disabled:opacity-50 ${action === 'CANCELLED' ? 'bg-rose-700' : 'bg-sky-700'}`}><CheckCircle2 size={15} className="mr-1 inline" />{busy ? 'Saving…' : titles[pickup.status] && action !== 'CANCELLED' ? titles[pickup.status] : action.replaceAll('_', ' ')}</button>)}</div></div>}</section>

      <section className="rounded-[28px] border border-slate-200 bg-white p-6 shadow-sm"><h2 className="text-xl font-semibold text-slate-900">Tracking timeline</h2><div className="mt-5 space-y-4">{(pickup.status_history || []).map((entry) => <div key={entry.id} className="relative border-l-2 border-sky-200 pb-2 pl-5"><span className="absolute -left-[7px] top-1 h-3 w-3 rounded-full bg-sky-600" /><p className="font-semibold text-slate-900">{entry.new_status.replaceAll('_', ' ')}</p><p className="text-xs text-slate-500">{new Date(entry.created_at).toLocaleString()} · {entry.changed_by_name}</p>{entry.note && <p className="mt-1 text-sm text-slate-600">{entry.note}</p>}</div>)}{pickup.received_at && <div className="relative border-l-2 border-emerald-200 pb-2 pl-5"><span className="absolute -left-[7px] top-1 h-3 w-3 rounded-full bg-emerald-600" /><p className="font-semibold text-emerald-800">NGO confirmed receipt</p><p className="text-xs text-slate-500">{new Date(pickup.received_at).toLocaleString()}</p></div>}</div>{pickup.delivery_log?.proof_available && <button type="button" onClick={downloadProof} className="mt-4 text-sm font-semibold text-sky-700">Download protected delivery proof</button>}</section>
    </div>}
  </DashboardLayout>;
}

export default PickupDetailsPage;
