import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';

import donationApi from '../api/donations';
import Button from '../components/ui/Button';
import Input from '../components/ui/Input';
import Select from '../components/ui/Select';

const initialForm = {
  food_name: '',
  category: '',
  description: '',
  quantity: '',
  unit: 'kg',
  storage_condition: 'AMBIENT',
  preparation_time: '',
  expiry_time: '',
  pickup_address: '',
  latitude: '',
  longitude: '',
};

function fieldErrorsFromResponse(data) {
  if (!data || typeof data !== 'object') {
    return {};
  }

  const flattened = {};

  Object.entries(data).forEach(([key, value]) => {
    if (Array.isArray(value)) {
      flattened[key] = value[0];
      return;
    }

    if (typeof value === 'object' && value !== null) {
      flattened[key] = value[0] || Object.values(value)[0];
      return;
    }

    flattened[key] = value;
  });

  return flattened;
}

function CreateDonationPage() {
  const navigate = useNavigate();
  const [formData, setFormData] = useState(initialForm);
  const [categories, setCategories] = useState([]);
  const [image, setImage] = useState(null);
  const [errors, setErrors] = useState({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    donationApi
      .categories()
      .then(({ data }) => setCategories(data))
      .catch(() => setCategories([]));
  }, []);

  const handleChange = (event) => {
    const { name, value } = event.target;
    setFormData((previous) => ({ ...previous, [name]: value }));
    setErrors((previous) => ({ ...previous, [name]: '' }));
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setErrors({});
    setIsSubmitting(true);

    try {
      const payload = new FormData();
      Object.entries(formData).forEach(([key, value]) => {
        if (value !== '' && value !== null) {
          payload.append(key, value);
        }
      });

      if (image) {
        payload.append('image', image);
      }

      const response = await donationApi.create(payload);
      toast.success('Donation created successfully.');
      navigate(`/donations/${response.data.id}`);
    } catch (submissionError) {
      const serverErrors = fieldErrorsFromResponse(submissionError.response?.data);
      setErrors(serverErrors);
      toast.error(serverErrors.detail || 'Please review the donation form and try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="mx-auto max-w-4xl py-8">
      <div className="rounded-[30px] border border-slate-200 bg-white p-6 shadow-sm sm:p-8">
        <p className="text-sm font-semibold uppercase tracking-[0.2em] text-emerald-700">Create donation</p>
        <h1 className="mt-3 text-3xl font-bold text-slate-900">Add a new food donation listing</h1>

        <form onSubmit={handleSubmit} className="mt-6 space-y-6" encType="multipart/form-data">
          <div className="grid gap-5 md:grid-cols-2">
            <Input label="Food name" id="food_name" name="food_name" value={formData.food_name} onChange={handleChange} error={errors.food_name} placeholder="Fresh apples" required />
            <Select label="Category" id="category" name="category" value={formData.category} onChange={handleChange} error={errors.category} options={[{ label: 'Select category', value: '' }, ...categories.map((category) => ({ label: category.name, value: category.id }))]} />
          </div>

          <div className="grid gap-5 md:grid-cols-2">
            <Input label="Quantity" id="quantity" name="quantity" type="number" min="0.01" step="0.01" value={formData.quantity} onChange={handleChange} error={errors.quantity} placeholder="10" required />
            <Input label="Unit" id="unit" name="unit" value={formData.unit} onChange={handleChange} error={errors.unit} placeholder="kg" />
          </div>

          <div className="grid gap-5 md:grid-cols-2">
            <Select label="Storage condition" id="storage_condition" name="storage_condition" value={formData.storage_condition} onChange={handleChange} options={[
              { label: 'Ambient', value: 'AMBIENT' },
              { label: 'Refrigerated', value: 'REFRIGERATED' },
              { label: 'Frozen', value: 'FROZEN' },
              { label: 'Room temperature', value: 'ROOM_TEMPERATURE' },
            ]} />
            <Input label="Expiry time" id="expiry_time" name="expiry_time" type="datetime-local" value={formData.expiry_time} onChange={handleChange} error={errors.expiry_time} required />
          </div>

          <div className="grid gap-5 md:grid-cols-2">
            <Input label="Preparation time" id="preparation_time" name="preparation_time" type="datetime-local" value={formData.preparation_time} onChange={handleChange} error={errors.preparation_time} />
            <Input label="Pickup address" id="pickup_address" name="pickup_address" value={formData.pickup_address} onChange={handleChange} error={errors.pickup_address} placeholder="123 Main Street" required />
          </div>

          <div className="grid gap-5 md:grid-cols-2">
            <Input label="Latitude" id="latitude" name="latitude" type="number" step="0.000001" value={formData.latitude} onChange={handleChange} error={errors.latitude} placeholder="48.8566" />
            <Input label="Longitude" id="longitude" name="longitude" type="number" step="0.000001" value={formData.longitude} onChange={handleChange} error={errors.longitude} placeholder="2.3522" />
          </div>

          <div>
            <label htmlFor="image" className="mb-2 block text-sm font-medium text-slate-700">Donation image</label>
            <input
              id="image"
              type="file"
              accept="image/*"
              onChange={(event) => setImage(event.target.files?.[0] || null)}
              className="block w-full rounded-xl border border-slate-200 bg-white px-3.5 py-2.5 text-sm text-slate-700 file:mr-4 file:rounded-lg file:border-0 file:bg-emerald-50 file:px-3 file:py-2 file:text-sm file:font-medium file:text-emerald-700"
            />
            {errors.image ? <p className="mt-1 text-xs text-red-600">{errors.image}</p> : null}
          </div>

          <div>
            <label htmlFor="description" className="mb-2 block text-sm font-medium text-slate-700">Description</label>
            <textarea
              id="description"
              name="description"
              value={formData.description}
              onChange={handleChange}
              rows="4"
              className="w-full rounded-xl border border-slate-200 bg-white px-3.5 py-2.5 text-sm text-slate-800 shadow-sm outline-none transition focus:border-emerald-500 focus:ring-2 focus:ring-emerald-100"
              placeholder="Describe the donation, freshness, and any handling notes."
            />
            {errors.description ? <p className="mt-1 text-xs text-red-600">{errors.description}</p> : null}
          </div>

          <div className="flex flex-wrap gap-3">
            <Button type="submit" disabled={isSubmitting}>{isSubmitting ? 'Creating donation...' : 'Create donation'}</Button>
            <Button type="button" variant="secondary" onClick={() => navigate('/donations/my')}>View my donations</Button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default CreateDonationPage;
