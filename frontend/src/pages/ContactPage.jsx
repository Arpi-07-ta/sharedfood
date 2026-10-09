import { useState } from 'react';
import { Mail, MapPin, Phone } from 'lucide-react';
import toast from 'react-hot-toast';

import Button from '../components/ui/Button';
import Input from '../components/ui/Input';

function ContactPage() {
  const [formData, setFormData] = useState({ name: '', email: '', message: '' });
  const [errors, setErrors] = useState({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  const validate = () => {
    const nextErrors = {};

    if (!formData.name.trim()) nextErrors.name = 'Name is required.';
    if (!formData.email.trim()) nextErrors.email = 'Email is required.';
    else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) nextErrors.email = 'Please enter a valid email.';
    if (!formData.message.trim()) nextErrors.message = 'Message is required.';

    return nextErrors;
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    const nextErrors = validate();
    setErrors(nextErrors);

    if (Object.keys(nextErrors).length > 0) {
      toast.error('Please fix the highlighted fields before sending.');
      return;
    }

    setIsSubmitting(true);
    await new Promise((resolve) => setTimeout(resolve, 1000));
    setIsSubmitting(false);
    toast.success('Thanks! Your message has been queued for review.');
    setFormData({ name: '', email: '', message: '' });
    setErrors({});
  };

  return (
    <div className="space-y-8 py-4">
      <section className="rounded-[30px] bg-slate-900 px-6 py-10 text-white sm:px-8 lg:px-12">
        <p className="text-sm font-semibold uppercase tracking-[0.2em] text-emerald-300">Contact</p>
        <h1 className="mt-3 text-4xl font-black tracking-tight">Discuss your local food recovery goals.</h1>
      </section>

      <section className="grid gap-8 lg:grid-cols-[0.9fr_1.1fr]">
        <div className="rounded-[28px] border border-slate-200 bg-white p-6 shadow-sm">
          <h2 className="text-2xl font-bold text-slate-900">Get in touch</h2>
          <div className="mt-6 space-y-5 text-slate-600">
            <div className="flex items-start gap-3">
              <Mail className="mt-0.5 text-emerald-600" size={18} />
              <span>hello@foodshareai.example</span>
            </div>
            <div className="flex items-start gap-3">
              <Phone className="mt-0.5 text-emerald-600" size={18} />
              <span>+1 (555) 942-8846</span>
            </div>
            <div className="flex items-start gap-3">
              <MapPin className="mt-0.5 text-emerald-600" size={18} />
              <span>Remote operations, regional partnerships, and field coordination</span>
            </div>
          </div>
        </div>

        <form onSubmit={handleSubmit} className="rounded-[28px] border border-slate-200 bg-white p-6 shadow-sm">
          <div className="grid gap-5 sm:grid-cols-2">
            <Input
              label="Full name"
              id="name"
              name="name"
              placeholder="Jane Donor"
              value={formData.name}
              onChange={(event) => setFormData({ ...formData, name: event.target.value })}
              error={errors.name}
            />
            <Input
              label="Email"
              id="email"
              name="email"
              type="email"
              placeholder="name@example.com"
              value={formData.email}
              onChange={(event) => setFormData({ ...formData, email: event.target.value })}
              error={errors.email}
            />
          </div>

          <div className="mt-5">
            <label htmlFor="message" className="mb-2 block text-sm font-medium text-slate-700">
              Your message
            </label>
            <textarea
              id="message"
              rows={6}
              value={formData.message}
              onChange={(event) => setFormData({ ...formData, message: event.target.value })}
              placeholder="Tell us about your food recovery goals or operational needs."
              className={`w-full rounded-xl border bg-white px-3.5 py-2.5 text-sm text-slate-800 shadow-sm outline-none transition focus:border-emerald-500 focus:ring-2 focus:ring-emerald-100 ${
                errors.message ? 'border-red-300' : 'border-slate-200'
              }`}
            />
            {errors.message ? <p className="mt-1 text-xs text-red-600">{errors.message}</p> : null}
          </div>

          <div className="mt-6 flex justify-end">
            <Button type="submit" disabled={isSubmitting} className="min-w-[160px]">
              {isSubmitting ? 'Sending...' : 'Send message'}
            </Button>
          </div>
        </form>
      </section>
    </div>
  );
}

export default ContactPage;
