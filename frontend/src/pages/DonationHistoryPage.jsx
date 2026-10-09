import { useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';

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

function DonationHistoryPage() {
  const { id } = useParams();
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    donationApi
      .history(id)
      .then(({ data }) => setHistory(data))
      .finally(() => setLoading(false));
  }, [id]);

  if (loading) {
    return <div className="rounded-[24px] border border-slate-200 bg-white p-6 text-slate-500">Loading donation history...</div>;
  }

  return (
    <div className="mx-auto max-w-4xl py-8">
      <div className="mb-6 flex items-center justify-between gap-3">
        <div>
          <p className="text-sm font-semibold uppercase tracking-[0.2em] text-emerald-700">Donation history</p>
          <h1 className="mt-2 text-3xl font-bold text-slate-900">Status timeline</h1>
        </div>
        <Link to={`/donations/${id}`}>
          <Button variant="secondary">Back to details</Button>
        </Link>
      </div>

      <div className="space-y-4 rounded-[28px] border border-slate-200 bg-white p-6 shadow-sm">
        {history.length === 0 ? (
          <p className="text-slate-500">No status history is available for this donation yet.</p>
        ) : (
          history.map((entry) => (
            <div key={entry.id} className="rounded-2xl border border-slate-200 bg-slate-50 p-4">
              <div className="flex flex-wrap items-center justify-between gap-2">
                <StatusBadge label={entry.new_status} variant={statusToneMap[entry.new_status] || 'neutral'} />
                <span className="text-xs text-slate-500">{new Date(entry.created_at).toLocaleString()}</span>
              </div>
              <p className="mt-3 text-sm text-slate-600">
                {entry.previous_status ? `From ${entry.previous_status} to ${entry.new_status}` : `Created as ${entry.new_status}`}
              </p>
              {entry.note ? <p className="mt-2 text-sm text-slate-700">{entry.note}</p> : null}
            </div>
          ))
        )}
      </div>
    </div>
  );
}

export default DonationHistoryPage;
