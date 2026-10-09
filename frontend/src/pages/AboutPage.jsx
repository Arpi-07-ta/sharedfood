import { ArrowRight, Leaf, ShieldCheck, Sparkles } from 'lucide-react';
import { Link } from 'react-router-dom';

import Button from '../components/ui/Button';

const values = [
  {
    title: 'Operational clarity',
    text: 'Every donation, inventory record, and redistribution step should be easy to understand and trace.',
  },
  {
    title: 'Sustainability first',
    text: 'The platform is designed to keep food moving longer, reduce waste, and improve social and environmental impact.',
  },
  {
    title: 'Human-centered systems',
    text: 'Donors, volunteers, and partner organizations all need clear workflows and transparent status updates.',
  },
];

function AboutPage() {
  return (
    <div className="space-y-10 py-4">
      <section className="rounded-[30px] bg-slate-900 px-6 py-10 text-white sm:px-8 lg:px-12">
        <div className="grid gap-8 lg:grid-cols-[1.1fr_0.9fr] lg:items-center">
          <div>
            <p className="text-sm font-semibold uppercase tracking-[0.2em] text-emerald-300">About FoodShare AI</p>
            <h1 className="mt-3 text-4xl font-black tracking-tight">Built to make surplus food coordination smarter and more humane.</h1>
            <p className="mt-4 max-w-2xl text-slate-300">
              FoodShare AI is a concept platform for reducing food waste and improving donation visibility across communities, organizations, and supply chains.
            </p>
            <div className="mt-6 flex flex-col gap-3 sm:flex-row">
              <Link to="/register">
                <Button className="bg-emerald-500 text-white hover:bg-emerald-400">Join the initiative</Button>
              </Link>
              <Link to="/how-it-works">
                <Button variant="outline" className="border-white/30 bg-transparent text-white hover:bg-white/10">
                  Learn the flow
                </Button>
              </Link>
            </div>
          </div>

          <div className="rounded-[28px] border border-white/10 bg-white/5 p-6">
            <div className="flex items-center gap-3 text-emerald-300">
              <Leaf size={18} />
              <span className="text-sm uppercase tracking-[0.18em]">Mission</span>
            </div>
            <p className="mt-4 text-lg text-slate-200">
              To create a better bridge between surplus food availability and community need, using transparent data and smart coordination tools.
            </p>
          </div>
        </div>
      </section>

      <section className="grid gap-6 md:grid-cols-3">
        {values.map(({ title, text }) => (
          <div key={title} className="rounded-[24px] border border-slate-200 bg-white p-6 shadow-sm">
            <div className="mb-3 flex h-12 w-12 items-center justify-center rounded-xl bg-emerald-100 text-emerald-700">
              {title === 'Operational clarity' ? <Sparkles size={20} /> : title === 'Sustainability first' ? <Leaf size={20} /> : <ShieldCheck size={20} />}
            </div>
            <h2 className="text-xl font-semibold text-slate-900">{title}</h2>
            <p className="mt-3 text-slate-600">{text}</p>
          </div>
        ))}
      </section>

      <section className="rounded-[28px] border border-slate-200 bg-gradient-to-br from-emerald-50 to-white p-6 lg:p-8">
        <div className="flex items-center gap-3 text-emerald-700">
          <Sparkles size={18} />
          <p className="text-sm font-semibold uppercase tracking-[0.2em]">Our approach</p>
        </div>
        <h2 className="mt-3 text-3xl font-bold text-slate-900">Clear data, faster action, stronger outcomes</h2>
        <div className="mt-6 grid gap-4 md:grid-cols-2">
          {[
            'Use smarter logistics recommendations to reduce friction between donors and NGOs.',
            'Keep everyone aligned through clear status updates, permission rules, and audit-friendly workflows.',
            'Support a measurable sustainability story with forecasting and decision-making aids.',
            'Promote collaboration between institutions that need impact visibility and operational consistency.',
          ].map((item) => (
            <div key={item} className="flex items-start gap-3 rounded-2xl bg-white p-4 shadow-sm">
              <ArrowRight className="mt-1 text-emerald-600" size={18} />
              <span className="text-slate-700">{item}</span>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}

export default AboutPage;
