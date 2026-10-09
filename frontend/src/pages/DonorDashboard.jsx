import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { HandHeart, RefreshCw, Sparkles } from 'lucide-react';

import donationApi from '../api/donations';
import matchingApi from '../api/matching';
import DashboardLayout from '../components/dashboard/DashboardLayout';
import StatusBadge from '../components/ui/StatusBadge';

const navItems = [
  { label: 'Overview', to: '/dashboard/donor', icon: Sparkles },
  { label: 'Donations', to: '/donations/my', icon: HandHeart },
];

function unwrapList(data) {
  return data?.results || data || [];
}

function DonorDashboard() {
  const [donations, setDonations] = useState([]);
  const [matches, setMatches] = useState({});
  const [requests, setRequests] = useState([]);
  const [loading, setLoading] = useState(true);
  const [workingId, setWorkingId] = useState(null);
  const [error, setError] = useState('');
  const [notice, setNotice] = useState('');

  const loadDonations = async () => {
    setError('');
    try {
      const [{ data }, requestsResponse] = await Promise.all([donationApi.myDonations(), donationApi.myRequests()]);
      setRequests(unwrapList(requestsResponse.data));
      const donationList = unwrapList(data);
      setDonations(donationList);
      const matchEntries = await Promise.all(donationList.map(async (donation) => {
        try {
          const response = await matchingApi.forDonation(donation.id);
          return [donation.id, unwrapList(response.data)];
        } catch {
          return [donation.id, []];
        }
      }));
      setMatches(Object.fromEntries(matchEntries));
    } catch {
      setError('Could not load donations. Please try again in a moment.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDonations();
  }, []);

  const generateMatches = async (donation) => {
    setWorkingId(donation.id);
    setError('');
    try {
      const { data } = await matchingApi.generate(donation.id);
      setMatches((current) => ({ ...current, [donation.id]: data.results || [] }));
    } catch (requestError) {
      setError(requestError.response?.data?.detail || 'Could not generate recommendations for this donation.');
    } finally {
      setWorkingId(null);
    }
  };

  const decideRequest = async (requestId, decision) => {
    setWorkingId(`request-${requestId}`);
    setError('');
    try {
      if (decision === 'accept') await donationApi.acceptRequest(requestId);
      else await donationApi.rejectRequest(requestId);
      setNotice(decision === 'accept' ? 'Request accepted. This NGO now owns the donation assignment.' : 'Request rejected.');
      await loadDonations();
    } catch (requestError) {
      setError(requestError.response?.data?.detail || 'Could not update the donation request.');
    } finally {
      setWorkingId(null);
    }
  };

  return (
    <DashboardLayout title="Donor dashboard" subtitle="Find verified community partners for your available food donations." roleLabel="Donor" navItems={navItems}>
      <section className="rounded-[28px] border border-emerald-100 bg-white p-6 shadow-sm">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <p className="text-sm font-semibold uppercase tracking-[0.2em] text-emerald-700">Smart matching</p>
            <h2 className="mt-2 text-2xl font-semibold text-slate-900">Recommended NGOs</h2>
            <p className="mt-1 max-w-2xl text-sm text-slate-600">Matches are ranked with a transparent weighted score, not an ML probability.</p>
          </div>
          <Link to="/donations/my" className="rounded-xl border border-slate-200 px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50">Manage donations</Link>
        </div>

        {error && <p role="alert" className="mt-4 rounded-xl bg-rose-50 px-4 py-3 text-sm text-rose-700">{error}</p>}
        {notice && <p role="status" className="mt-3 rounded-xl bg-emerald-50 px-4 py-3 text-sm text-emerald-800">{notice}</p>}
        {loading ? (
          <p className="mt-6 text-sm text-slate-500">Loading your available donations…</p>
        ) : donations.length === 0 ? (
          <div className="mt-6 rounded-2xl border border-dashed border-slate-300 p-6 text-center">
            <p className="font-medium text-slate-800">No donations yet</p>
            <Link to="/donations/create" className="mt-2 inline-block text-sm font-semibold text-emerald-700">Create a donation</Link>
          </div>
        ) : (
          <div className="mt-6 space-y-5">
            {donations.map((donation) => {
              const recommendationList = matches[donation.id] || [];
              const available = donation.status === 'AVAILABLE';
              return (
                <article key={donation.id} className="rounded-2xl border border-slate-200 p-5">
                  <div className="flex flex-wrap items-start justify-between gap-3">
                    <div>
                      <div className="flex flex-wrap items-center gap-3">
                        <h3 className="text-lg font-semibold text-slate-900">{donation.food_name}</h3>
                        <StatusBadge label={donation.status} variant={available ? 'success' : 'neutral'} />
                      </div>
                      <p className="mt-1 text-sm text-slate-600">{donation.quantity} {donation.unit} · {donation.pickup_address}</p>
                    </div>
                    <button
                      type="button"
                      disabled={!available || workingId === donation.id}
                      onClick={() => generateMatches(donation)}
                      className="inline-flex items-center gap-2 rounded-xl bg-emerald-700 px-4 py-2 text-sm font-semibold text-white hover:bg-emerald-800 disabled:cursor-not-allowed disabled:bg-slate-300"
                    >
                      <RefreshCw size={16} className={workingId === donation.id ? 'animate-spin' : ''} />
                      {workingId === donation.id ? 'Finding NGOs…' : recommendationList.length ? 'Refresh matches' : 'Find NGOs'}
                    </button>
                  </div>

                  {recommendationList.length ? (
                    <div className="mt-5 space-y-3">
                      {recommendationList.map((match) => (
                        <div key={match.id} className="grid gap-4 rounded-xl bg-emerald-50/70 p-4 md:grid-cols-[1fr_auto]">
                          <div>
                            <div className="flex flex-wrap items-center gap-2">
                              <h4 className="font-semibold text-slate-900">{match.ngo_name}</h4>
                              <span className="rounded-full bg-white px-2.5 py-1 text-xs font-medium text-emerald-800">
                                Compatibility {Number(match.compatibility_score).toFixed(0)}%
                              </span>
                              <span className="text-xs text-slate-600">{match.distance_km == null ? 'Distance unavailable' : `${Number(match.distance_km).toFixed(1)} km away`}</span>
                            </div>
                            <ul className="mt-3 grid gap-1 text-xs leading-relaxed text-slate-600 sm:grid-cols-2">
                              {(match.explanation || []).map((line, index) => <li key={`${match.id}-${index}`}>{line}</li>)}
                            </ul>
                          </div>
                          <div className="self-start rounded-xl bg-white px-4 py-3 text-center">
                            <p className="text-2xl font-bold text-emerald-800">{Number(match.match_score).toFixed(1)}</p>
                            <p className="text-[11px] font-medium uppercase tracking-wide text-slate-500">Ranking score / 100</p>
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <p className="mt-4 rounded-xl bg-slate-50 px-4 py-3 text-sm text-slate-500">
                      {available ? 'No eligible verified NGOs yet. NGOs need an active matching profile, accepted category, and sufficient capacity.' : 'Recommendations are only generated for available donations.'}
                    </p>
                  )}
                </article>
              );
            })}
          </div>
        )}
      </section>
      <section className="mt-6 rounded-[28px] border border-slate-200 bg-white p-6 shadow-sm">
        <h2 className="text-xl font-semibold text-slate-900">Incoming NGO requests</h2>
        <p className="mt-1 text-sm text-slate-600">Review the organization and full-donation request before approving assignment.</p>
        <div className="mt-4 space-y-3">
          {requests.filter((request) => request.status === 'PENDING').length === 0 ? (
            <p className="rounded-xl border border-dashed border-slate-300 p-5 text-sm text-slate-500">No pending NGO requests.</p>
          ) : requests.filter((request) => request.status === 'PENDING').map((request) => (
            <article key={request.id} className="flex flex-wrap items-center justify-between gap-3 rounded-xl border border-slate-200 p-4">
              <div><h3 className="font-semibold text-slate-900">{request.ngo_name} requests {request.donation_name}</h3><p className="mt-1 text-sm text-slate-600">{request.requested_quantity} · {request.message || 'No message provided'} · submitted {new Date(request.created_at).toLocaleString()}</p></div>
              <div className="flex gap-2"><button type="button" disabled={workingId === `request-${request.id}`} onClick={() => decideRequest(request.id, 'accept')} className="rounded-xl bg-emerald-700 px-3 py-2 text-sm font-semibold text-white disabled:bg-slate-300">Accept</button><button type="button" disabled={workingId === `request-${request.id}`} onClick={() => decideRequest(request.id, 'reject')} className="rounded-xl border border-rose-200 px-3 py-2 text-sm font-semibold text-rose-700 disabled:opacity-50">Reject</button></div>
            </article>
          ))}
        </div>
      </section>
    </DashboardLayout>
  );
}

export default DonorDashboard;
