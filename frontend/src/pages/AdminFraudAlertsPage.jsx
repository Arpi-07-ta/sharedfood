import { useCallback, useEffect, useState } from 'react';
import { AlertTriangle, CheckCircle2, RefreshCw, ShieldCheck } from 'lucide-react';

import fraudApi from '../api/fraud';
import DashboardLayout from '../components/dashboard/DashboardLayout';

const navItems = [
  { label: 'Admin overview', to: '/dashboard/admin', icon: ShieldCheck },
  { label: 'Fraud alerts', to: '/admin/fraud-alerts', icon: AlertTriangle },
];
const statusFilters = ['OPEN', 'REVIEWING', 'RESOLVED'];
const outcomes = [
  ['NO_ACTION', 'No action required'],
  ['FALSE_POSITIVE', 'False positive'],
  ['POLICY_VIOLATION', 'Policy violation'],
  ['ESCALATED', 'Escalated for further review'],
];
const levelStyles = {
  LOW: 'bg-slate-100 text-slate-700',
  MEDIUM: 'bg-amber-100 text-amber-800',
  HIGH: 'bg-orange-100 text-orange-800',
  CRITICAL: 'bg-rose-100 text-rose-800',
};

function AdminFraudAlertsPage() {
  const [statusFilter, setStatusFilter] = useState('OPEN');
  const [page, setPage] = useState(1);
  const [hasNextPage, setHasNextPage] = useState(false);
  const [hasPreviousPage, setHasPreviousPage] = useState(false);
  const [alerts, setAlerts] = useState([]);
  const [selectedAlert, setSelectedAlert] = useState(null);
  const [outcome, setOutcome] = useState('NO_ACTION');
  const [note, setNote] = useState('');
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [notice, setNotice] = useState('');

  const loadAlerts = useCallback(async () => {
    setLoading(true);
    setError('');
    try {
      const { data } = await fraudApi.listAlerts({ status: statusFilter, page });
      setAlerts(data.results || []);
      setHasNextPage(Boolean(data.next));
      setHasPreviousPage(Boolean(data.previous));
    } catch (requestError) {
      setError(requestError.response?.status === 403
        ? 'Administrator permission is required to view fraud alerts.'
        : 'Could not load fraud alerts.');
    } finally {
      setLoading(false);
    }
  }, [statusFilter, page]);

  useEffect(() => { loadAlerts(); }, [loadAlerts]);

  const openReview = async (alert) => {
    setError('');
    setNotice('');
    setOutcome('NO_ACTION');
    setNote('');
    try {
      const { data } = await fraudApi.getAlert(alert.id);
      setSelectedAlert(data);
    } catch {
      setError('Could not load alert details.');
    }
  };

  const submitReview = async (event) => {
    event.preventDefault();
    if (!selectedAlert) return;
    setSaving(true);
    setError('');
    setNotice('');
    try {
      await fraudApi.reviewAlert(selectedAlert.id, { outcome, note });
      setSelectedAlert(null);
      setNotice(outcome === 'ESCALATED'
        ? 'Review saved and the alert was escalated for continued human review. No account action was taken automatically.'
        : 'Review saved and the alert was marked resolved. No account action was taken automatically.');
      await loadAlerts();
    } catch (requestError) {
      setError(requestError.response?.data?.detail || 'Could not save the review.');
    } finally {
      setSaving(false);
    }
  };

  return (
    <DashboardLayout title="Fraud alert review" subtitle="Rule-based signals are triage aids for human review, not proof of misconduct." roleLabel="Admin" navItems={navItems}>
      <section className="rounded-[28px] border border-slate-200 bg-white p-6 shadow-sm">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div>
            <p className="text-sm font-semibold uppercase tracking-[0.2em] text-rose-700">Admin-only queue</p>
            <h2 className="mt-2 text-2xl font-semibold text-slate-900">Fraud and risk alerts</h2>
            <p className="mt-1 max-w-3xl text-sm text-slate-600">Alerts use explainable rules. A flag never bans, suspends, or restricts an account by itself.</p>
          </div>
          <button type="button" onClick={loadAlerts} className="inline-flex items-center gap-2 rounded-xl border border-slate-200 px-3 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50"><RefreshCw size={16} />Refresh</button>
        </div>

        {error && <p role="alert" className="mt-4 rounded-xl bg-rose-50 px-4 py-3 text-sm text-rose-700">{error}</p>}
        {notice && <p role="status" className="mt-4 rounded-xl bg-emerald-50 px-4 py-3 text-sm text-emerald-800">{notice}</p>}

        <div className="mt-6 flex flex-wrap gap-2" role="tablist" aria-label="Filter alerts by review status">
          {statusFilters.map((filter) => <button key={filter} type="button" role="tab" aria-selected={statusFilter === filter} onClick={() => { setStatusFilter(filter); setPage(1); }} className={`rounded-full px-4 py-2 text-sm font-medium ${statusFilter === filter ? 'bg-slate-900 text-white' : 'bg-slate-100 text-slate-700 hover:bg-slate-200'}`}>{filter}</button>)}
        </div>

        {loading ? <p className="mt-6 text-sm text-slate-500">Loading alerts…</p> : alerts.length === 0 ? (
          <div className="mt-6 rounded-2xl border border-dashed border-slate-300 p-8 text-center">
            <CheckCircle2 className="mx-auto text-emerald-600" size={28} />
            <p className="mt-3 font-medium text-slate-800">No {statusFilter.toLowerCase()} alerts</p>
            <p className="mt-1 text-sm text-slate-500">New alerts appear here when rule-based signals require human review.</p>
          </div>
        ) : (
          <div className="mt-5 space-y-4">
            {alerts.map((alert) => <article key={alert.id} className="rounded-2xl border border-slate-200 p-5">
              <div className="flex flex-wrap items-start justify-between gap-4">
                <div className="min-w-0 flex-1">
                  <div className="flex flex-wrap items-center gap-2">
                    <h3 className="font-semibold text-slate-900">{alert.alert_type.replaceAll('_', ' ')}</h3>
                    <span className={`rounded-full px-2.5 py-1 text-xs font-semibold ${levelStyles[alert.risk_level] || levelStyles.LOW}`}>{alert.risk_level}</span>
                    <span className="rounded-full bg-slate-100 px-2.5 py-1 text-xs font-medium text-slate-700">Score {alert.risk_score}/100</span>
                    <span className="text-xs text-slate-500">{alert.status}</span>
                  </div>
                  <p className="mt-2 text-sm text-slate-600">Account: {alert.actor_username} · Donation: {alert.donation_name || 'Account activity'} · Seen {new Date(alert.last_seen_at).toLocaleString()}</p>
                  <p className="mt-2 text-sm text-slate-700">{alert.reason}</p>
                  <ul className="mt-3 space-y-1 text-xs text-slate-600">{(alert.reasons || []).map((item, index) => <li key={`${alert.id}-${index}`}><span className="font-semibold">{item.code.replaceAll('_', ' ')}:</span> {item.detail}</li>)}</ul>
                  <p className="mt-3 text-xs text-slate-500">{alert.detection_method} · {alert.rule_version} · {alert.occurrence_count} occurrence(s)</p>
                  {alert.review_outcome && <p className="mt-2 text-sm text-slate-700">Outcome: {alert.review_outcome.replaceAll('_', ' ')}{alert.review_note ? ` — ${alert.review_note}` : ''}</p>}
                </div>
                {alert.status !== 'RESOLVED' && <button type="button" onClick={() => openReview(alert)} className="rounded-xl bg-slate-900 px-4 py-2 text-sm font-semibold text-white hover:bg-slate-700">Review</button>}
              </div>
            </article>)}
          </div>
        )}
        {!loading && alerts.length > 0 && <div className="mt-5 flex items-center justify-between border-t border-slate-100 pt-4">
          <span className="text-sm text-slate-500">Page {page}</span>
          <div className="flex gap-2">
            <button type="button" disabled={!hasPreviousPage} onClick={() => setPage((current) => Math.max(1, current - 1))} className="rounded-lg border border-slate-300 px-3 py-2 text-sm disabled:cursor-not-allowed disabled:opacity-40">Previous</button>
            <button type="button" disabled={!hasNextPage} onClick={() => setPage((current) => current + 1)} className="rounded-lg border border-slate-300 px-3 py-2 text-sm disabled:cursor-not-allowed disabled:opacity-40">Next</button>
          </div>
        </div>}
      </section>

      {selectedAlert && <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/50 p-4" role="presentation" onMouseDown={(event) => { if (event.target === event.currentTarget) setSelectedAlert(null); }}>
        <section role="dialog" aria-modal="true" aria-labelledby="fraud-review-title" className="max-h-[90vh] w-full max-w-xl overflow-y-auto rounded-3xl bg-white p-6 shadow-2xl">
          <p className="text-sm font-semibold uppercase tracking-[0.18em] text-rose-700">Human review</p>
          <h2 id="fraud-review-title" className="mt-2 text-xl font-semibold text-slate-900">Review alert #{selectedAlert.id}</h2>
          <p className="mt-2 text-sm text-slate-600">Risk score {selectedAlert.risk_score}/100 · {selectedAlert.risk_level}. Choose an outcome; this does not automatically change user access.</p>
          <form onSubmit={submitReview} className="mt-5 space-y-4">
            <label className="block text-sm font-medium text-slate-700">Review outcome
              <select value={outcome} onChange={(event) => setOutcome(event.target.value)} className="mt-1 w-full rounded-xl border border-slate-300 px-3 py-2">{outcomes.map(([value, label]) => <option key={value} value={value}>{label}</option>)}</select>
            </label>
            <label className="block text-sm font-medium text-slate-700">Review note (optional)
              <textarea value={note} onChange={(event) => setNote(event.target.value)} rows={4} maxLength={5000} className="mt-1 w-full rounded-xl border border-slate-300 px-3 py-2" placeholder="Record the evidence and decision rationale." />
            </label>
            <div className="flex justify-end gap-2">
              <button type="button" onClick={() => setSelectedAlert(null)} className="rounded-xl border border-slate-300 px-4 py-2 text-sm font-medium text-slate-700">Cancel</button>
              <button type="submit" disabled={saving} className="rounded-xl bg-emerald-700 px-4 py-2 text-sm font-semibold text-white hover:bg-emerald-800 disabled:bg-slate-300">{saving ? 'Saving…' : 'Save review'}</button>
            </div>
          </form>
        </section>
      </div>}
    </DashboardLayout>
  );
}

export default AdminFraudAlertsPage;
