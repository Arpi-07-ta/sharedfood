import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';

import donationApi from '../api/donations';
import Button from '../components/ui/Button';
import StatusBadge from '../components/ui/StatusBadge';

const statusToneMap = {
  AVAILABLE: 'success',
  MATCHED: 'warning',
  ACCEPTED: 'info',
  PICKUP_SCHEDULED: 'warning',
  PICKED_UP: 'info',
  DELIVERED: 'success',
  COMPLETED: 'success',
  CANCELLED: 'neutral',
  EXPIRED: 'danger',
  REJECTED: 'danger',
};

function MyDonationsPage() {
  const [donations, setDonations] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    donationApi
      .myDonations()
      .then(({ data }) => setDonations(data.results || data))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return <div className="rounded-[24px] border border-slate-200 bg-white p-6 text-slate-500">Loading your donations...</div>;
  }

  return (
    <div className="mx-auto max-w-6xl py-8">
      <div className="mb-6 flex items-center justify-between gap-3">
        <div>
          <p className="text-sm font-semibold uppercase tracking-[0.2em] text-emerald-700">My donations</p>
          <h1 className="mt-2 text-3xl font-bold text-slate-900">Donation history and status</h1>
        </div>
        <Link to="/donations/create">
          <Button>Create donation</Button>
        </Link>
      </div>

      <div className="space-y-4">
        {donations.length === 0 ? (
          <div className="rounded-[24px] border border-dashed border-slate-300 bg-white p-8 text-center text-slate-500">
            You have not created any donations yet.
          </div>
        ) : (
          donations.map((donation) => (
            <div key={donation.id} className="rounded-[24px] border border-slate-200 bg-white p-5 shadow-sm">
              <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
                <div>
                  <div className="flex flex-wrap items-center gap-3">
                    <h2 className="text-xl font-semibold text-slate-900">{donation.food_name}</h2>
                    <StatusBadge label={donation.status} variant={statusToneMap[donation.status] || 'neutral'} />
                  </div>
                  <p className="mt-2 text-sm text-slate-600">{donation.quantity} {donation.unit} • {donation.pickup_address}</p>
                </div>
                <div className="flex flex-wrap gap-2">
                  <Link to={`/donations/${donation.id}`}>
                    <Button variant="secondary" size="sm">Details</Button>
                  </Link>
                  <Link to={`/donations/${donation.id}/history`}>
                    <Button variant="outline" size="sm">History</Button>
                  </Link>
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}

export default MyDonationsPage;
