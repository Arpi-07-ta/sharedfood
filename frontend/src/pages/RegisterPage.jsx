import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';

import Button from '../components/ui/Button';
import ErrorMessage from '../components/ui/ErrorMessage';
import Input from '../components/ui/Input';
import Select from '../components/ui/Select';
import { useAuth } from '../hooks/useAuth';

function RegisterPage() {
  const navigate = useNavigate();
  const { register } = useAuth();
  const [formData, setFormData] = useState({
    name: '', email: '', password: '', role: 'donor', confirmPassword: '', phoneNumber: '',
    organizationName: '', registrationNumber: '', mission: '', address: '', city: '', state: '', country: '', contactEmail: '',
  });
  const [error, setError] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (event) => {
    event.preventDefault();

    if (!formData.name.trim()) {
      setError('Please provide your full name.');
      toast.error('Please provide your full name.');
      return;
    }

    const emailValid = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email);
    if (!emailValid) {
      setError('Please enter a valid email address.');
      toast.error('Please enter a valid email address.');
      return;
    }

    if (formData.password.length < 8) {
      setError('Password must be at least 8 characters long.');
      toast.error('Password must be at least 8 characters long.');
      return;
    }

    if (formData.password !== formData.confirmPassword) {
      setError('Passwords do not match.');
      toast.error('Passwords do not match.');
      return;
    }

    if (formData.role === 'ngo' && (!formData.organizationName.trim() || !formData.registrationNumber.trim())) {
      setError('Organization name and registration number are required for NGO registration.');
      toast.error('Add your organization name and registration number.');
      return;
    }

    const [firstName, ...restName] = formData.name.trim().split(/\s+/);
    const lastName = restName.join(' ');

    setError('');
    setIsSubmitting(true);

    try {
      await register({
        username: `${firstName}${lastName ? lastName.charAt(0) : ''}`.toLowerCase(),
        email: formData.email,
        first_name: firstName,
        last_name: lastName,
        phone_number: formData.phoneNumber,
        role: formData.role.toUpperCase(),
        password: formData.password,
        confirm_password: formData.confirmPassword,
        ...(formData.role === 'ngo' ? {
          organization_name: formData.organizationName,
          registration_number: formData.registrationNumber,
          mission: formData.mission,
          address: formData.address,
          city: formData.city,
          state: formData.state,
          country: formData.country,
          contact_email: formData.contactEmail || formData.email,
        } : {}),
      });
      toast.success('Your profile is ready.');
      navigate('/dashboard');
    } catch (registerError) {
      const nextError = registerError.response?.data?.detail || registerError.response?.data?.non_field_errors?.[0] || registerError.response?.data?.role?.[0] || 'Unable to create your account.';
      setError(nextError);
      toast.error(nextError);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="mx-auto max-w-2xl py-8">
      <div className="rounded-[30px] border border-slate-200 bg-white p-6 shadow-sm sm:p-8">
        <p className="text-sm font-semibold uppercase tracking-[0.2em] text-emerald-700">Create account</p>
        <h1 className="mt-3 text-3xl font-bold text-slate-900">Register your FoodShare AI profile</h1>

        <form onSubmit={handleSubmit} className="mt-6 space-y-5">
          {error ? <ErrorMessage message={error} /> : null}

          <div className="grid gap-5 sm:grid-cols-2">
            <Input
              label="Full name"
              id="register-name"
              placeholder="Jane Donor"
              value={formData.name}
              onChange={(event) => setFormData({ ...formData, name: event.target.value })}
            />
            <Select
              label="Role"
              id="register-role"
              value={formData.role}
              onChange={(event) => setFormData({ ...formData, role: event.target.value })}
              options={[
                { label: 'Donor', value: 'donor' },
                { label: 'NGO partner', value: 'ngo' },
                { label: 'Volunteer', value: 'volunteer' },
              ]}
            />
          </div>

          <Input
            label="Email"
            id="register-email"
            type="email"
            placeholder="name@example.com"
            value={formData.email}
            onChange={(event) => setFormData({ ...formData, email: event.target.value })}
          />

          <Input label="Contact phone" id="register-phone" type="tel" placeholder="+1 555 123 4567" value={formData.phoneNumber} onChange={(event) => setFormData({ ...formData, phoneNumber: event.target.value })} />

          {formData.role === 'ngo' && <section className="space-y-4 rounded-2xl border border-emerald-100 bg-emerald-50/50 p-4">
            <div>
              <h2 className="font-semibold text-slate-900">Organization details</h2>
              <p className="mt-1 text-sm text-slate-600">Your account will remain unverified until an administrator reviews your documents.</p>
            </div>
            <div className="grid gap-4 sm:grid-cols-2">
              <Input label="Organization name" id="register-org-name" value={formData.organizationName} onChange={(event) => setFormData({ ...formData, organizationName: event.target.value })} />
              <Input label="Registration number" id="register-reg-number" value={formData.registrationNumber} onChange={(event) => setFormData({ ...formData, registrationNumber: event.target.value })} />
              <Input label="Contact email" id="register-contact-email" type="email" value={formData.contactEmail} onChange={(event) => setFormData({ ...formData, contactEmail: event.target.value })} />
              <Input label="City" id="register-city" value={formData.city} onChange={(event) => setFormData({ ...formData, city: event.target.value })} />
              <Input label="State / region" id="register-state" value={formData.state} onChange={(event) => setFormData({ ...formData, state: event.target.value })} />
              <Input label="Country" id="register-country" value={formData.country} onChange={(event) => setFormData({ ...formData, country: event.target.value })} />
              <div className="sm:col-span-2"><Input label="Street address" id="register-address" value={formData.address} onChange={(event) => setFormData({ ...formData, address: event.target.value })} /></div>
              <div className="sm:col-span-2"><Input label="Mission (optional)" id="register-mission" value={formData.mission} onChange={(event) => setFormData({ ...formData, mission: event.target.value })} /></div>
            </div>
          </section>}

          <div className="grid gap-5 sm:grid-cols-2">
            <Input
              label="Password"
              id="register-password"
              type="password"
              placeholder="At least 8 characters"
              value={formData.password}
              onChange={(event) => setFormData({ ...formData, password: event.target.value })}
            />
            <Input
              label="Confirm password"
              id="register-confirm-password"
              type="password"
              placeholder="Repeat your password"
              value={formData.confirmPassword}
              onChange={(event) => setFormData({ ...formData, confirmPassword: event.target.value })}
            />
          </div>

          <Button type="submit" className="w-full" disabled={isSubmitting}>
            {isSubmitting ? 'Creating account...' : 'Create account'}
          </Button>
        </form>

        <p className="mt-5 text-sm text-slate-600">
          Already have an account?{' '}
          <Link to="/login" className="font-semibold text-emerald-700">
            Sign in
          </Link>
        </p>
      </div>
    </div>
  );
}

export default RegisterPage;
