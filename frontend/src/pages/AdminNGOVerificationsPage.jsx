import { useCallback, useEffect, useState } from 'react';
import { CheckCircle2, ExternalLink, ShieldCheck, XCircle } from 'lucide-react';

import ngoAdminApi from '../api/ngoAdmin';
import DashboardLayout from '../components/dashboard/DashboardLayout';

const navItems = [
  { label: 'Admin overview', to: '/dashboard/admin', icon: ShieldCheck },
  { label: 'NGO verification', to: '/admin/ngo-verifications', icon: CheckCircle2 },
];

function AdminNGOVerificationsPage() {
  const [items, setItems] = useState([]);
  const [statusFilter, setStatusFilter] = useState('PENDING');
  const [notes, setNotes] = useState({});
  const [loading, setLoading] = useState(true);
  const [workingId, setWorkingId] = useState(null);
  const [error, setError] = useState('');
  const [notice, setNotice] = useState('');

  const load = useCallback(async () => {
    setLoading(true);
    setError('');
    try {
      const { data } = await ngoAdminApi.verifications({ status: statusFilter });
      setItems(data.results || []);
    } catch (requestError) {
      setError(requestError.response?.status === 403 ? 'Administrator permission is required.' : 'Could not load NGO verification requests.');
    } finally {
      setLoading(false);
    }
  }, [statusFilter]);

  useEffect(() => { load(); }, [load]);

  const review = async (item, decision) => {
    setWorkingId(item.id);
    setError('');
    setNotice('');
    try {
      await ngoAdminApi.reviewVerification(item.id, { status: decision, note: notes[item.id] || '' });
      setNotice(`${item.organization_name}: ${decision.toLowerCase()}.`);
      await load();
    } catch (requestError) {
      setError(requestError.response?.data?.note?.[0] || requestError.response?.data?.detail || 'Could not save the verification decision.');
    } finally {
      setWorkingId(null);
    }
  };

  const openDocument = async (id) => {
    try {
      const { data } = await ngoAdminApi.verificationDocument(id);
      const documentUrl = URL.createObjectURL(data);
      window.open(documentUrl, '_blank', 'noopener,noreferrer');
      window.setTimeout(() => URL.revokeObjectURL(documentUrl), 60_000);
    } catch {
      setError('Could not open the protected verification document.');
    }
  };

  return (
    <DashboardLayout title="NGO verification" subtitle="Review organization registrations and record a decision before matching eligibility is enabled." roleLabel="Admin" navItems={navItems}>
      <section className="rounded-[28px] border border-slate-200 bg-white p-6 shadow-sm">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div><p className="text-sm font-semibold uppercase tracking-[0.2em] text-emerald-700">Verification queue</p><h2 className="mt-2 text-2xl font-semibold text-slate-900">Organization applications</h2></div>
          <select value={statusFilter} onChange={(event) => setStatusFilter(event.target.value)} className="rounded-xl border border-slate-300 px-3 py-2 text-sm">
            {['PENDING', 'APPROVED', 'REJECTED', 'SUSPENDED'].map((status) => <option key={status}>{status}</option>)}
          </select>
        </div>
        {error && <p role="alert" className="mt-4 rounded-xl bg-rose-50 px-4 py-3 text-sm text-rose-700">{error}</p>}
        {notice && <p role="status" className="mt-4 rounded-xl bg-emerald-50 px-4 py-3 text-sm text-emerald-800">{notice}</p>}
        {loading ? <p className="mt-6 text-sm text-slate-500">Loading verification requests…</p> : items.length === 0 ? <div className="mt-6 rounded-2xl border border-dashed border-slate-300 p-8 text-center text-sm text-slate-500">No {statusFilter.toLowerCase()} NGO requests.</div> : (
          <div className="mt-5 space-y-4">
            {items.map((item) => <article key={item.id} className="rounded-2xl border border-slate-200 p-5">
              <div className="flex flex-wrap items-start justify-between gap-4">
                <div className="min-w-[250px] flex-1">
                  <h3 className="text-lg font-semibold text-slate-900">{item.organization_name}</h3>
                  <p className="mt-1 text-sm text-slate-600">Registration {item.registration_number} · {item.ngo_email} · {item.phone_number || 'No phone provided'}</p>
                  <p className="mt-2 text-xs text-slate-500">Submitted {new Date(item.created_at).toLocaleString()} · Status {item.status}</p>
                  {item.review_note && <p className="mt-2 text-sm text-slate-700">Review note: {item.review_note}</p>}
                  {item.document_name && <button type="button" onClick={() => openDocument(item.id)} className="mt-3 inline-flex items-center gap-2 text-sm font-semibold text-emerald-700 hover:text-emerald-900"><ExternalLink size={15} />View protected verification document</button>}
                  <label className="mt-4 block text-sm font-medium text-slate-700">Decision note
                    <textarea value={notes[item.id] || ''} onChange={(event) => setNotes((current) => ({ ...current, [item.id]: event.target.value }))} rows={2} className="mt-1 w-full rounded-xl border border-slate-300 px-3 py-2" placeholder="Required when rejecting or suspending." />
                  </label>
                </div>
                {statusFilter !== 'APPROVED' && <div className="flex gap-2">
                  <button type="button" disabled={workingId === item.id} onClick={() => review(item, 'APPROVED')} className="inline-flex items-center gap-2 rounded-xl bg-emerald-700 px-3 py-2 text-sm font-semibold text-white disabled:opacity-50"><CheckCircle2 size={15} />Approve</button>
                  <button type="button" disabled={workingId === item.id || !(notes[item.id] || '').trim()} onClick={() => review(item, 'REJECTED')} className="inline-flex items-center gap-2 rounded-xl border border-rose-200 px-3 py-2 text-sm font-semibold text-rose-700 disabled:opacity-50"><XCircle size={15} />Reject</button>
                </div>}
              </div>
            </article>)}
          </div>
        )}
      </section>
    </DashboardLayout>
  );
}

export default AdminNGOVerificationsPage;
