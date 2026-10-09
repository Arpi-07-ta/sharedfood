import { useEffect, useState } from 'react';
import { Link, useNavigate, useParams } from 'react-router-dom';
import toast from 'react-hot-toast';

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

function resolveImageUrl(value) {
  if (!value) return null;
  if (value.startsWith('http')) return value;
  return `http://localhost:8000${value}`;
}

function DonationDetailsPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [donation, setDonation] = useState(null);
  const [loading, setLoading] = useState(true);

  const fetchDonation = () => {
    donationApi
      .getById(id)
      .then(({ data }) => setDonation(data))
      .catch(() => toast.error('Unable to load this donation.'))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    fetchDonation();
  }, [id]);

  const handleCancel = async () => {
    try {
      const { data } = await donationApi.cancel(id);
      setDonation(data);
      toast.success('Donation cancelled.');
    } catch (cancelError) {
      const message = cancelError.response?.data?.status || 'This donation cannot be cancelled in its current state.';
      toast.error(message);
    }
  };

  if (loading) {
    return <div className="rounded-[24px] border border-slate-200 bg-white p-6 text-slate-500">Loading donation details...</div>;
  }

  if (!donation) {
    return <div className="rounded-[24px] border border-slate-200 bg-white p-6 text-slate-500">Donation not found.</div>;
  }

  return (
    <div className="mx-auto max-w-5xl py-8">
      <div className="mb-6 flex flex-wrap items-center justify-between gap-3">
        <div>
          <p className="text-sm font-semibold uppercase tracking-[0.2em] text-emerald-700">Donation details</p>
          <h1 className="mt-2 text-3xl font-bold text-slate-900">{donation.food_name}</h1>
        </div>
        <div className="flex gap-2">
          <Link to="/donations/my"><Button variant="secondary">Back to my donations</Button></Link>
          <Link to={`/donations/${id}/history`}><Button variant="outline">View history</Button></Link>
          {donation.status === 'AVAILABLE' || donation.status === 'MATCHED' || donation.status === 'ACCEPTED' || donation.status === 'PICKUP_SCHEDULED' ? (
            <Button variant="danger" onClick={handleCancel}>Cancel donation</Button>
          ) : null}
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-[1.2fr_0.8fr]">
        <div className="rounded-[28px] border border-slate-200 bg-white p-6 shadow-sm">
          <div className="mb-5 flex items-center gap-3">
            <StatusBadge label={donation.status} variant={statusToneMap[donation.status] || 'neutral'} />
            <span className="text-sm text-slate-500">{donation.quantity} {donation.unit}</span>
          </div>

          {donation.image ? (
            <img src={resolveImageUrl(donation.image)} alt={donation.food_name} className="mb-5 h-72 w-full rounded-2xl object-cover" />
          ) : null}

          <div className="grid gap-4 sm:grid-cols-2">
            <div className="rounded-2xl bg-slate-50 p-4">
              <p className="text-xs uppercase tracking-[0.18em] text-slate-500">Category</p>
              <p className="mt-2 font-semibold text-slate-900">{donation.category}</p>
            </div>
            <div className="rounded-2xl bg-slate-50 p-4">
              <p className="text-xs uppercase tracking-[0.18em] text-slate-500">Storage</p>
              <p className="mt-2 font-semibold text-slate-900">{donation.storage_condition}</p>
            </div>
            <div className="rounded-2xl bg-slate-50 p-4">
              <p className="text-xs uppercase tracking-[0.18em] text-slate-500">Expiry</p>
              <p className="mt-2 font-semibold text-slate-900">{new Date(donation.expiry_time).toLocaleString()}</p>
            </div>
            <div className="rounded-2xl bg-slate-50 p-4">
              <p className="text-xs uppercase tracking-[0.18em] text-slate-500">Pickup</p>
              <p className="mt-2 font-semibold text-slate-900">{donation.pickup_address}</p>
            </div>
          </div>

          <div className="mt-6">
            <p className="text-xs uppercase tracking-[0.18em] text-slate-500">Description</p>
            <p className="mt-2 text-slate-700">{donation.description || 'No description provided.'}</p>
          </div>
        </div>

        <div className="rounded-[28px] border border-emerald-100 bg-emerald-50 p-6 shadow-sm">
          <h2 className="text-xl font-semibold text-slate-900">Actions</h2>
          <div className="mt-4 space-y-3 text-sm text-slate-700">
            <p>• Review the current availability and handling state.</p>
            <p>• Open the status timeline to trace progress over time.</p>
            <p>• Cancel only when the donation is still editable.</p>
          </div>
          <div className="mt-6">
            <Button variant="secondary" className="w-full" onClick={() => navigate(`/donations/${id}/history`)}>Status history</Button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default DonationDetailsPage;
