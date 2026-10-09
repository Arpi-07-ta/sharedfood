import { useCallback, useEffect, useState } from 'react';
import { Boxes, CheckCircle2, MapPinned, Save, ShieldCheck, Sparkles, Truck } from 'lucide-react';

import { authApi } from '../api/client';
import donationApi from '../api/donations';
import matchingApi from '../api/matching';
import ngoOperationsApi from '../api/ngoOperations';
import trackingApi from '../api/tracking';
import DashboardLayout from '../components/dashboard/DashboardLayout';

const navItems = [
  { label: 'Overview', to: '/dashboard/ngo', icon: Sparkles },
  { label: 'Matching profile', to: '/dashboard/ngo', icon: Boxes },
  { label: 'Pickup coordination', to: '/dashboard/ngo', icon: Truck },
];
const unwrapList = (data) => data?.results || data || [];
const inputValue = (value) => value == null ? '' : String(value);
const blankTimeWindow = () => ({ start: '', end: '' });

function NGODashboard() {
  const [organization, setOrganization] = useState(null);
  const [verification, setVerification] = useState(null);
  const [matchProfile, setMatchProfile] = useState(null);
  const [categories, setCategories] = useState([]);
  const [matches, setMatches] = useState([]);
  const [available, setAvailable] = useState([]);
  const [requests, setRequests] = useState([]);
  const [accepted, setAccepted] = useState([]);
  const [pickups, setPickups] = useState([]);
  const [analytics, setAnalytics] = useState(null);
  const [feedback, setFeedback] = useState({});
  const [windows, setWindows] = useState({});
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [workingId, setWorkingId] = useState(null);
  const [documentFile, setDocumentFile] = useState(null);
  const [documentUrl, setDocumentUrl] = useState('');
  const [error, setError] = useState('');
  const [notice, setNotice] = useState('');

  const loadDashboard = useCallback(async () => {
    setError('');
    const safeLoad = async (promise, fallback, setter) => {
      try { const result = await promise; setter(result.data); } catch { setter(fallback); }
    };
    const jobs = [
      safeLoad(authApi.ngoProfile(), null, (data) => data && setOrganization(data)),
      safeLoad(authApi.ngoVerification(), null, (data) => data && setVerification(data)),
      safeLoad(matchingApi.profile(), null, (data) => data && setMatchProfile({
        ...data,
        latitude: inputValue(data.latitude),
        longitude: inputValue(data.longitude),
        capacity_kg: inputValue(data.capacity_kg),
        current_demand_score: inputValue(data.current_demand_score),
        accepted_categories: (data.accepted_categories || []).map(Number),
      })),
      safeLoad(donationApi.categories(), [], (data) => setCategories(unwrapList(data))),
      safeLoad(matchingApi.myMatches(), [], (data) => setMatches(unwrapList(data))),
      safeLoad(donationApi.list(), [], (data) => setAvailable(unwrapList(data))),
      safeLoad(donationApi.myRequests(), [], (data) => setRequests(unwrapList(data))),
      safeLoad(donationApi.acceptedDonations(), [], (data) => setAccepted(unwrapList(data))),
      safeLoad(trackingApi.ngoPickups(), [], (data) => setPickups(unwrapList(data))),
      safeLoad(ngoOperationsApi.analytics(), null, (data) => setAnalytics(data)),
      safeLoad(ngoOperationsApi.feedback(), [], (data) => setFeedback(Object.fromEntries(unwrapList(data).map((entry) => [entry.donation, entry])))),
    ];
    await Promise.all(jobs);
    setLoading(false);
  }, []);

  useEffect(() => { loadDashboard(); }, [loadDashboard]);

  const updateOrg = (key, value) => setOrganization((current) => ({ ...current, [key]: value }));
  const updateMatch = (key, value) => setMatchProfile((current) => ({ ...current, [key]: value }));
  const toggleCategory = (categoryId) => setMatchProfile((current) => {
    const selected = new Set(current.accepted_categories || []);
    const id = Number(categoryId);
    if (selected.has(id)) selected.delete(id);
    else selected.add(id);
    return { ...current, accepted_categories: [...selected] };
  });

  const saveProfiles = async (event) => {
    event.preventDefault();
    setSaving(true);
    setError('');
    setNotice('');
    const asNumberOrNull = (value) => value === '' ? null : Number(value);
    try {
      const orgPayload = {
        organization_name: organization.organization_name,
        mission: organization.mission,
        address: organization.address,
        city: organization.city,
        state: organization.state,
        country: organization.country,
        contact_email: organization.contact_email,
        latitude: asNumberOrNull(organization.latitude),
        longitude: asNumberOrNull(organization.longitude),
      };
      const matchPayload = {
        capacity_kg: Number(matchProfile.capacity_kg || 0),
        current_demand_score: Number(matchProfile.current_demand_score || 0),
        accepted_categories: matchProfile.accepted_categories,
        latitude: asNumberOrNull(organization.latitude),
        longitude: asNumberOrNull(organization.longitude),
      };
      await Promise.all([authApi.updateNGOProfile(orgPayload), matchingApi.updateProfile(matchPayload)]);
      setNotice('Organization and matching profile saved.');
      await loadDashboard();
    } catch (saveError) {
      setError(saveError.response?.data?.detail || JSON.stringify(saveError.response?.data || {}) || 'Could not save profiles.');
    } finally { setSaving(false); }
  };

  const submitVerification = async (event) => {
    event.preventDefault();
    if (!documentFile && !documentUrl.trim()) {
      setError('Add a verification document file or a document URL.');
      return;
    }
    const payload = new FormData();
    if (documentFile) payload.append('document', documentFile);
    if (documentUrl.trim()) payload.append('documents_url', documentUrl.trim());
    try {
      const { data } = await authApi.submitNGOVerification(payload);
      setVerification(data);
      setNotice('Verification submission sent. Matching acceptance is available after admin approval.');
      setError('');
    } catch (submitError) {
      setError(submitError.response?.data?.document?.[0] || submitError.response?.data?.detail || 'Could not submit verification documents.');
    }
  };

  const requestDonation = async (donation) => {
    setWorkingId(`request-${donation.id}`);
    try {
      await donationApi.requestDonation(donation.id, { requested_quantity: donation.quantity, message: '' });
      setNotice(`Request sent for ${donation.food_name}. The donor will review it.`);
      await loadDashboard();
    } catch (requestError) {
      setError(requestError.response?.data?.detail || requestError.response?.data?.requested_quantity?.[0] || 'Could not request this donation.');
    } finally { setWorkingId(null); }
  };

  const acceptRecommendation = async (matchId) => {
    setWorkingId(matchId);
    try {
      await matchingApi.accept(matchId);
      setNotice('Donation accepted and assigned to your organization.');
      await loadDashboard();
    } catch (requestError) {
      setError(requestError.response?.data?.detail || 'Could not accept this recommendation.');
    } finally { setWorkingId(null); }
  };

  const declineRecommendation = async (matchId) => {
    setWorkingId(matchId);
    try {
      await matchingApi.decline(matchId);
      setNotice('Recommendation declined.');
      await loadDashboard();
    } catch { setError('Could not decline this recommendation.'); }
    finally { setWorkingId(null); }
  };

  const schedulePickup = async (donationId) => {
    const window = windows[donationId] || blankTimeWindow();
    if (!window.start || !window.end) {
      setError('Choose both pickup window times.');
      return;
    }
    setWorkingId(`pickup-${donationId}`);
    try {
      await trackingApi.schedule(donationId, {
        pickup_window_start: new Date(window.start).toISOString(),
        pickup_window_end: new Date(window.end).toISOString(),
      });
      setNotice('Pickup scheduled. Volunteers can now claim the assignment.');
      await loadDashboard();
    } catch (requestError) {
      setError(requestError.response?.data?.detail || 'Could not schedule pickup.');
    } finally { setWorkingId(null); }
  };

  const confirmReceived = async (pickupId) => {
    setWorkingId(`receive-${pickupId}`);
    try {
      await trackingApi.confirmReceived(pickupId);
      setNotice('Receipt confirmed and the donation marked complete. Please leave feedback below.');
      await loadDashboard();
    } catch (requestError) {
      setError(requestError.response?.data?.detail || 'A volunteer must confirm delivery before receipt can be confirmed.');
    } finally { setWorkingId(null); }
  };

  const submitFeedback = async (event, donationId) => {
    event.preventDefault();
    const value = feedback[donationId] || { rating: 5, comment: '' };
    try {
      await ngoOperationsApi.submitFeedback({ donation: donationId, rating: Number(value.rating), comment: value.comment });
      setNotice('Thank you. Your delivery feedback was saved.');
      await loadDashboard();
    } catch (requestError) {
      setError(requestError.response?.data?.detail || requestError.response?.data?.donation?.[0] || 'Could not save feedback.');
    }
  };

  if (loading || !organization || !matchProfile) {
    return <DashboardLayout title="NGO dashboard" subtitle="Organization, donation, and fulfillment workspace." roleLabel="NGO" navItems={navItems}><div className="rounded-2xl border border-slate-200 bg-white p-6 text-slate-500">Loading NGO workspace…</div></DashboardLayout>;
  }

  const approved = verification?.status === 'APPROVED';
  const pending = verification?.status === 'PENDING';
  return (
    <DashboardLayout title="NGO dashboard" subtitle="Manage your organization, request food, coordinate pickups, and record received donations." roleLabel="NGO" navItems={navItems}>
      {error && <p role="alert" className="mb-4 rounded-xl bg-rose-50 px-4 py-3 text-sm text-rose-700">{error}</p>}
      {notice && <p role="status" className="mb-4 rounded-xl bg-emerald-50 px-4 py-3 text-sm text-emerald-800">{notice}</p>}

      {!approved && <section className="mb-6 rounded-2xl border border-amber-200 bg-amber-50 p-5">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div><p className="font-semibold text-amber-900">Verification {verification?.status || 'PENDING'}</p><p className="mt-1 text-sm text-amber-800">Only active, verified NGOs can request or accept donations. Submit organization documents for admin review.</p>{verification?.review_note && <p className="mt-2 text-sm text-slate-700">Admin note: {verification.review_note}</p>}</div>
          {verification?.document_name && <span className="text-xs text-amber-900">File submitted: {verification.document_name}</span>}
        </div>
        {!pending && <form onSubmit={submitVerification} className="mt-4 grid gap-3 sm:grid-cols-[1fr_1fr_auto]">
          <label className="text-sm font-medium text-slate-700">Verification document (PDF/JPG/PNG, up to 5 MB)<input type="file" accept="application/pdf,image/jpeg,image/png" onChange={(event) => setDocumentFile(event.target.files?.[0] || null)} className="mt-1 block w-full text-sm" /></label>
          <label className="text-sm font-medium text-slate-700">Or document URL<input type="url" value={documentUrl} onChange={(event) => setDocumentUrl(event.target.value)} className="mt-1 w-full rounded-xl border border-slate-300 px-3 py-2" /></label>
          <button type="submit" className="self-end rounded-xl bg-amber-700 px-4 py-2 text-sm font-semibold text-white">Submit for review</button>
        </form>}
      </section>}

      <section className="mb-6 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
        {[
          ['Accepted donations', analytics?.accepted_donations ?? '—'],
          ['Completed donations', analytics?.completed_donations ?? '—'],
          ['Received (kg)', analytics?.received_quantity_kg ?? '—'],
          ['Average feedback', analytics?.average_feedback_rating ?? '—'],
        ].map(([label, value]) => <div key={label} className="rounded-2xl border border-slate-200 bg-white p-4"><p className="text-xs font-semibold uppercase tracking-wide text-slate-500">{label}</p><p className="mt-2 text-2xl font-bold text-slate-900">{value}</p></div>)}
      </section>

      <div className="space-y-6">
        <section className="rounded-[28px] border border-slate-200 bg-white p-6 shadow-sm">
          <div className="mb-5"><p className="text-sm font-semibold uppercase tracking-[0.2em] text-emerald-700">Organization profile</p><h2 className="mt-2 text-2xl font-semibold text-slate-900">Contact and location</h2></div>
          <form onSubmit={saveProfiles} className="space-y-5">
            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
              <label className="text-sm font-medium text-slate-700">Organization name<input required value={organization.organization_name || ''} onChange={(event) => updateOrg('organization_name', event.target.value)} className="mt-1 w-full rounded-xl border border-slate-300 px-3 py-2" /></label>
              <label className="text-sm font-medium text-slate-700">Contact email<input type="email" value={organization.contact_email || ''} onChange={(event) => updateOrg('contact_email', event.target.value)} className="mt-1 w-full rounded-xl border border-slate-300 px-3 py-2" /></label>
              <label className="text-sm font-medium text-slate-700">Address<input value={organization.address || ''} onChange={(event) => updateOrg('address', event.target.value)} className="mt-1 w-full rounded-xl border border-slate-300 px-3 py-2" /></label>
              <label className="text-sm font-medium text-slate-700">City<input value={organization.city || ''} onChange={(event) => updateOrg('city', event.target.value)} className="mt-1 w-full rounded-xl border border-slate-300 px-3 py-2" /></label>
              <label className="text-sm font-medium text-slate-700">State / region<input value={organization.state || ''} onChange={(event) => updateOrg('state', event.target.value)} className="mt-1 w-full rounded-xl border border-slate-300 px-3 py-2" /></label>
              <label className="text-sm font-medium text-slate-700">Country<input value={organization.country || ''} onChange={(event) => updateOrg('country', event.target.value)} className="mt-1 w-full rounded-xl border border-slate-300 px-3 py-2" /></label>
              <label className="text-sm font-medium text-slate-700">Latitude<input type="number" min="-90" max="90" step="any" value={inputValue(organization.latitude)} onChange={(event) => updateOrg('latitude', event.target.value)} className="mt-1 w-full rounded-xl border border-slate-300 px-3 py-2" /></label>
              <label className="text-sm font-medium text-slate-700">Longitude<input type="number" min="-180" max="180" step="any" value={inputValue(organization.longitude)} onChange={(event) => updateOrg('longitude', event.target.value)} className="mt-1 w-full rounded-xl border border-slate-300 px-3 py-2" /></label>
              <label className="text-sm font-medium text-slate-700 sm:col-span-2 lg:col-span-1">Mission<input value={organization.mission || ''} onChange={(event) => updateOrg('mission', event.target.value)} className="mt-1 w-full rounded-xl border border-slate-300 px-3 py-2" /></label>
            </div>

            <div className="border-t border-slate-100 pt-5">
              <h3 className="font-semibold text-slate-900">Food needs and capacity</h3>
              <p className="mt-1 text-sm text-slate-600">Requests and recommendations are available after verification approval.</p>
              <div className="mt-3 grid gap-4 sm:grid-cols-2">
                <label className="text-sm font-medium text-slate-700">Capacity (kg)<input type="number" min="0" step="0.01" value={matchProfile.capacity_kg} onChange={(event) => updateMatch('capacity_kg', event.target.value)} className="mt-1 w-full rounded-xl border border-slate-300 px-3 py-2" /></label>
                <label className="text-sm font-medium text-slate-700">Current demand score (0–100)<input type="number" min="0" max="100" value={matchProfile.current_demand_score} onChange={(event) => updateMatch('current_demand_score', event.target.value)} className="mt-1 w-full rounded-xl border border-slate-300 px-3 py-2" /></label>
              </div>
              <p className="mb-2 mt-4 text-sm font-semibold text-slate-800">Accepted categories</p>
              <div className="grid gap-2 sm:grid-cols-2 lg:grid-cols-3">{categories.map((category) => <label key={category.id} className="flex items-center gap-2 rounded-xl border border-slate-200 px-3 py-2 text-sm"><input type="checkbox" checked={(matchProfile.accepted_categories || []).includes(Number(category.id))} onChange={() => toggleCategory(category.id)} />{category.name}</label>)}</div>
            </div>
            <div className="flex flex-wrap items-center justify-between gap-3"><p className="text-xs text-slate-500">Reliability and active status are administrator-managed.</p><button type="submit" disabled={saving} className="inline-flex items-center gap-2 rounded-xl bg-emerald-700 px-4 py-2 text-sm font-semibold text-white disabled:bg-slate-300"><Save size={16} />{saving ? 'Saving…' : 'Save profile and needs'}</button></div>
          </form>
        </section>

        <section className="rounded-[28px] border border-slate-200 bg-white p-6 shadow-sm">
          <h2 className="text-xl font-semibold text-slate-900">Available donations</h2><p className="mt-1 text-sm text-slate-600">Review available listings or submit one request for the full donation. Donors make the final assignment decision.</p>
          {!approved && <p className="mt-3 rounded-xl bg-amber-50 p-3 text-sm text-amber-800">Verification approval is required before you can request or accept donations.</p>}
          <div className="mt-4 space-y-3">{available.length === 0 ? <p className="text-sm text-slate-500">No available donations at this time.</p> : available.map((donation) => {
            const alreadyRequested = requests.some((item) => item.donation_id === donation.id && item.status !== 'REJECTED');
            return <article key={donation.id} className="rounded-2xl border border-slate-200 p-4">
              <div className="flex flex-wrap items-start justify-between gap-3"><div><h3 className="font-semibold text-slate-900">{donation.food_name}</h3><p className="mt-1 text-sm text-slate-600">{donation.category_name || donation.category} · {donation.quantity} {donation.unit} · expires {new Date(donation.expiry_time).toLocaleString()}</p><p className="mt-1 text-xs text-slate-500">Pickup: {donation.pickup_address}</p><p className="mt-1 inline-flex items-center gap-1 text-xs text-slate-500"><MapPinned size={13} />Map unavailable: no map provider is configured.</p></div>
                <button type="button" disabled={!approved || alreadyRequested || workingId === `request-${donation.id}`} onClick={() => requestDonation(donation)} className="rounded-xl bg-emerald-700 px-3 py-2 text-sm font-semibold text-white disabled:bg-slate-300">{alreadyRequested ? 'Requested' : workingId === `request-${donation.id}` ? 'Sending…' : 'Request donation'}</button>
              </div>
            </article>;
          })}</div>
        </section>

        <section className="rounded-[28px] border border-slate-200 bg-white p-6 shadow-sm">
          <h2 className="text-xl font-semibold text-slate-900">Donation requests</h2>
          <div className="mt-4 space-y-3">{requests.length === 0 ? <p className="text-sm text-slate-500">No requests yet.</p> : requests.map((item) => <article key={item.id} className="flex flex-wrap items-center justify-between gap-3 rounded-xl bg-slate-50 p-4"><div><p className="font-semibold text-slate-900">{item.donation_name} · {item.requested_quantity}</p><p className="text-sm text-slate-600">Status {item.status} · {item.message || 'No message'}</p></div><span className="rounded-full bg-white px-3 py-1 text-xs font-medium text-slate-600">{item.status}</span></article>)}</div>
        </section>

        <section className="rounded-[28px] border border-slate-200 bg-white p-6 shadow-sm">
          <h2 className="text-xl font-semibold text-slate-900">Recommended donations</h2><p className="mt-1 text-sm text-slate-600">Transparent weighted ranking scores—not ML probabilities.</p>
          <div className="mt-4 space-y-3">{matches.length === 0 ? <p className="text-sm text-slate-500">No active recommendations yet.</p> : matches.map((match) => <article key={match.id} className="rounded-2xl border border-slate-200 p-4">
            <div className="flex flex-wrap items-start justify-between gap-3"><div><h3 className="font-semibold text-slate-900">{match.donation_food_name} · {match.donation_category}</h3><p className="text-sm text-slate-600">{match.donation_quantity} {match.donation_unit} · compatibility {Number(match.compatibility_score).toFixed(0)}% · {match.distance_km == null ? 'distance unavailable' : `${Number(match.distance_km).toFixed(1)} km`}</p><p className="mt-1 text-xs text-slate-500">{match.status}</p></div><div className="flex items-center gap-2"><span className="text-xl font-bold text-emerald-800">{Number(match.match_score).toFixed(1)}/100</span>{match.status === 'RECOMMENDED' && <><button type="button" disabled={!approved || workingId === match.id} onClick={() => acceptRecommendation(match.id)} className="rounded-lg bg-emerald-700 px-3 py-2 text-sm font-semibold text-white disabled:bg-slate-300"><CheckCircle2 size={15} className="inline" /> Accept</button><button type="button" disabled={workingId === match.id} onClick={() => declineRecommendation(match.id)} className="rounded-lg border px-3 py-2 text-sm">Decline</button></>}</div></div>
            <ul className="mt-3 grid gap-1 text-xs text-slate-600 sm:grid-cols-2">{(match.explanation || []).map((line, index) => <li key={`${match.id}-${index}`}>{line}</li>)}</ul>
          </article>)}</div>
        </section>

        <section className="rounded-[28px] border border-slate-200 bg-white p-6 shadow-sm">
          <h2 className="text-xl font-semibold text-slate-900">Accepted donation history and pickups</h2>
          <div className="mt-4 space-y-4">{accepted.length === 0 ? <p className="text-sm text-slate-500">No accepted donations yet.</p> : accepted.map((donation) => {
            const pickup = pickups.find((item) => item.donation_id === donation.id);
            const window = windows[donation.id] || blankTimeWindow();
            const done = donation.status === 'COMPLETED';
            const currentFeedback = feedback[donation.id] || { rating: 5, comment: '' };
            return <article key={donation.id} className="rounded-2xl border border-slate-200 p-4">
              <div className="flex flex-wrap items-center justify-between gap-3"><div><h3 className="font-semibold text-slate-900">{donation.food_name}</h3><p className="text-sm text-slate-600">{donation.quantity} {donation.unit} · {donation.status}</p></div>{pickup && <span className="text-sm text-slate-600">Pickup {pickup.status}</span>}</div>
              {!pickup && donation.status === 'ACCEPTED' && <div className="mt-3 grid gap-2 sm:grid-cols-[1fr_1fr_auto]"><label className="text-xs text-slate-600">Pickup from<input type="datetime-local" value={window.start} onChange={(event) => setWindows((current) => ({ ...current, [donation.id]: { ...window, start: event.target.value } }))} className="mt-1 w-full rounded-lg border px-2 py-2" /></label><label className="text-xs text-slate-600">Pickup until<input type="datetime-local" value={window.end} onChange={(event) => setWindows((current) => ({ ...current, [donation.id]: { ...window, end: event.target.value } }))} className="mt-1 w-full rounded-lg border px-2 py-2" /></label><button type="button" disabled={!approved || workingId === `pickup-${donation.id}`} onClick={() => schedulePickup(donation.id)} className="self-end rounded-xl bg-slate-900 px-3 py-2 text-sm font-semibold text-white disabled:bg-slate-300">Schedule pickup</button></div>}
              {pickup && pickup.status === 'DELIVERED' && !done && <button type="button" onClick={() => confirmReceived(pickup.id)} disabled={!approved || workingId === `receive-${pickup.id}`} className="mt-3 rounded-xl bg-emerald-700 px-3 py-2 text-sm font-semibold text-white disabled:bg-slate-300">Confirm food received</button>}
              {done && !feedback[donation.id] && <form onSubmit={(event) => submitFeedback(event, donation.id)} className="mt-3 grid gap-2 sm:grid-cols-[140px_1fr_auto]"><select value={currentFeedback.rating} onChange={(event) => setFeedback((current) => ({ ...current, [donation.id]: { ...currentFeedback, rating: event.target.value } }))} className="rounded-lg border px-3 py-2"><option value="5">5 — Excellent</option><option value="4">4 — Good</option><option value="3">3 — Okay</option><option value="2">2 — Poor</option><option value="1">1 — Bad</option></select><input value={currentFeedback.comment} onChange={(event) => setFeedback((current) => ({ ...current, [donation.id]: { ...currentFeedback, comment: event.target.value } }))} placeholder="Feedback for this donation" className="rounded-lg border px-3 py-2" /><button className="rounded-xl border px-3 py-2 text-sm font-semibold">Send feedback</button></form>}
            </article>;
          })}</div>
        </section>

        <section className="rounded-[28px] border border-emerald-100 bg-emerald-50 p-6"><p className="text-sm font-semibold uppercase tracking-wide text-emerald-800">Need a volunteer?</p><p className="mt-2 text-sm text-slate-700">Scheduled pickups appear in the volunteer assignment queue. Volunteers confirm collection and delivery; your organization records final receipt below.</p></section>
      </div>
    </DashboardLayout>
  );
}

export default NGODashboard;
