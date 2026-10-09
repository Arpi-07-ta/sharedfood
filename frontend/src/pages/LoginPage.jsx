import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';

import Button from '../components/ui/Button';
import ErrorMessage from '../components/ui/ErrorMessage';
import Input from '../components/ui/Input';
import { useAuth } from '../hooks/useAuth';

function LoginPage() {
  const navigate = useNavigate();
  const { login } = useAuth();
  const [formData, setFormData] = useState({ email: '', password: '' });
  const [error, setError] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (event) => {
    event.preventDefault();

    const emailValid = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email);
    const passwordValid = formData.password.length >= 8;

    if (!emailValid || !passwordValid) {
      const nextError = 'Please enter a valid email address and a password with at least 8 characters.';
      setError(nextError);
      toast.error(nextError);
      return;
    }

    setError('');
    setIsSubmitting(true);

    try {
      await login({ email: formData.email, password: formData.password });
      toast.success('Signed in successfully.');
      navigate('/dashboard');
    } catch (loginError) {
      const nextError = loginError.response?.data?.detail || loginError.response?.data?.non_field_errors?.[0] || 'Unable to sign in. Please check your credentials.';
      setError(nextError);
      toast.error(nextError);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="mx-auto max-w-xl py-8">
      <div className="rounded-[30px] border border-slate-200 bg-white p-6 shadow-sm sm:p-8">
        <p className="text-sm font-semibold uppercase tracking-[0.2em] text-emerald-700">Welcome back</p>
        <h1 className="mt-3 text-3xl font-bold text-slate-900">Sign in to your workspace</h1>

        <form onSubmit={handleSubmit} className="mt-6 space-y-5">
          {error ? <ErrorMessage message={error} /> : null}

          <Input
            label="Email"
            id="login-email"
            type="email"
            placeholder="name@example.com"
            value={formData.email}
            onChange={(event) => setFormData({ ...formData, email: event.target.value })}
          />

          <Input
            label="Password"
            id="login-password"
            type="password"
            placeholder="Enter your password"
            value={formData.password}
            onChange={(event) => setFormData({ ...formData, password: event.target.value })}
          />

          <Button type="submit" className="w-full" disabled={isSubmitting}>
            {isSubmitting ? 'Signing in...' : 'Sign in'}
          </Button>
        </form>

        <p className="mt-5 text-sm text-slate-600">
          Need an account?{' '}
          <Link to="/register" className="font-semibold text-emerald-700">
            Create one here
          </Link>
        </p>
      </div>
    </div>
  );
}

export default LoginPage;
