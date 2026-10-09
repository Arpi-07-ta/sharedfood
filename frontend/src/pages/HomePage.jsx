import { ArrowRight, CheckCircle2, HeartHandshake, Leaf, Recycle, ShieldCheck, Sparkles, Store, Users } from 'lucide-react';
import { Link } from 'react-router-dom';
import { Area, AreaChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';

import Button from '../components/ui/Button';

const featureCards = [
  {
    icon: Leaf,
    title: 'AI waste forecasting',
    description: 'Surface food surplus risk with clearer demand and expiry signals before waste accumulates.',
  },
  {
    icon: Recycle,
    title: 'Circular recovery flow',
    description: 'Coordinate pickups, redistribution, and treatment paths in a single easy-to-monitor workflow.',
  },
  {
    icon: HeartHandshake,
    title: 'Donor-to-recipient bridge',
    description: 'Match donation requests to organization capacity and reduce friction across stakeholders.',
  },
  {
    icon: ShieldCheck,
    title: 'Trust and oversight',
    description: 'Keep food safety, permissions, and operational status visible to the teams that need context.',
  },
];

const steps = [
  'Capture donation inventory and availability details',
  'Assess predicted demand, expiry pressure, and logistics fit',
  'Triangulate the best recovery or redistribution route',
  'Monitor real-time impact and operational follow-up',
];

const audienceCards = [
  {
    icon: Store,
    title: 'For donors',
    description: 'List surplus food, reduce disposal costs, and contribute to measurable community outcomes.',
  },
  {
    icon: Users,
    title: 'For NGOs and partners',
    description: 'Track incoming supply, align inventory with local needs, and reduce excess through better planning.',
  },
];

const chartData = [
  { name: 'Week 1', recovery: 45, demand: 34, surplus: 20 },
  { name: 'Week 2', recovery: 52, demand: 41, surplus: 28 },
  { name: 'Week 3', recovery: 58, demand: 44, surplus: 24 },
  { name: 'Week 4', recovery: 62, demand: 49, surplus: 18 },
  { name: 'Week 5', recovery: 68, demand: 52, surplus: 16 },
  { name: 'Week 6', recovery: 70, demand: 56, surplus: 15 },
];

function HomePage() {
  return (
    <div className="space-y-16">
      <section className="overflow-hidden rounded-[30px] bg-gradient-to-br from-emerald-700 via-emerald-600 to-slate-900 px-6 py-10 text-white shadow-xl sm:px-8 lg:px-12 lg:py-16">
        <div className="grid items-center gap-10 lg:grid-cols-[1.2fr_0.8fr]">
          <div>
            <div className="mb-5 inline-flex items-center gap-2 rounded-full bg-white/10 px-3 py-1 text-xs font-medium uppercase tracking-[0.18em] text-emerald-100">
              <Sparkles size={14} />
              Sustainable coordination
            </div>
            <h1 className="max-w-xl text-4xl font-black leading-tight tracking-tight sm:text-5xl">
              Turn surplus food into measurable community impact.
            </h1>
            <p className="mt-5 max-w-xl text-base text-emerald-50 sm:text-lg">
              FoodShare AI brings together food donors, redistribution teams, and AI-assisted planning to reduce avoidable waste and improve donation readiness.
            </p>
            <div className="mt-8 flex flex-col gap-3 sm:flex-row">
              <Link to="/register">
                <Button variant="primary" className="bg-white text-emerald-700 hover:bg-emerald-50">
                  Join as a donor
                </Button>
              </Link>
              <Link to="/how-it-works">
                <Button variant="outline" className="border-white/40 bg-transparent text-white hover:bg-white/10">
                  Explore process
                </Button>
              </Link>
            </div>
          </div>

          <div className="rounded-[28px] border border-white/10 bg-slate-950/20 p-5 backdrop-blur-sm">
            <div className="mb-4 flex items-center justify-between">
              <div>
                <p className="text-xs uppercase tracking-[0.2em] text-emerald-200">Illustrative forecast</p>
                <h2 className="mt-2 text-xl font-bold">Recovery outlook</h2>
              </div>
              <div className="rounded-full bg-emerald-500/20 px-2 py-1 text-xs font-medium text-emerald-100">
                Live preview
              </div>
            </div>
            <div className="h-64 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={chartData}>
                  <defs>
                    <linearGradient id="recovery" x1="0" x2="0" y1="0" y2="1">
                      <stop offset="5%" stopColor="#34d399" stopOpacity={0.8} />
                      <stop offset="95%" stopColor="#34d399" stopOpacity={0.1} />
                    </linearGradient>
                    <linearGradient id="demand" x1="0" x2="0" y1="0" y2="1">
                      <stop offset="5%" stopColor="#fdba74" stopOpacity={0.75} />
                      <stop offset="95%" stopColor="#fdba74" stopOpacity={0.08} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.15)" />
                  <XAxis dataKey="name" stroke="#d1fae5" tickLine={false} axisLine={false} />
                  <YAxis stroke="#d1fae5" tickLine={false} axisLine={false} />
                  <Tooltip />
                  <Area type="monotone" dataKey="recovery" stroke="#34d399" fill="url(#recovery)" />
                  <Area type="monotone" dataKey="demand" stroke="#fdba74" fill="url(#demand)" />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>
      </section>

      <section id="features" className="space-y-8">
        <div className="text-center">
          <p className="text-sm font-semibold uppercase tracking-[0.2em] text-emerald-700">Why it matters</p>
          <h2 className="mt-3 text-3xl font-bold text-slate-900">Built for smarter food recovery</h2>
        </div>

        <div className="grid gap-6 md:grid-cols-2 xl:grid-cols-4">
          {featureCards.map(({ icon: Icon, title, description }) => (
            <div key={title} className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm transition hover:-translate-y-1 hover:shadow-md">
              <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-xl bg-emerald-100 text-emerald-700">
                <Icon size={22} />
              </div>
              <h3 className="text-xl font-semibold text-slate-900">{title}</h3>
              <p className="mt-3 text-sm leading-6 text-slate-600">{description}</p>
            </div>
          ))}
        </div>
      </section>

      <section className="grid gap-8 rounded-[28px] border border-slate-200 bg-white p-6 shadow-sm lg:grid-cols-2 lg:p-8">
        <div>
          <p className="text-sm font-semibold uppercase tracking-[0.2em] text-amber-600">How it works</p>
          <h2 className="mt-3 text-3xl font-bold text-slate-900">Operational clarity without the overwhelm</h2>
          <div className="mt-6 space-y-4">
            {steps.map((step, index) => (
              <div key={step} className="flex items-start gap-4 rounded-2xl bg-slate-50 p-4">
                <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-emerald-600 text-sm font-bold text-white">
                  {index + 1}
                </div>
                <p className="text-slate-700">{step}</p>
              </div>
            ))}
          </div>
        </div>

        <div className="rounded-[24px] bg-slate-900 p-6 text-white">
          <p className="text-sm uppercase tracking-[0.2em] text-emerald-300">Process snapshot</p>
          <h3 className="mt-4 text-2xl font-bold">Coordination with a sustainability lens</h3>
          <ul className="mt-6 space-y-4">
            {[
              'Inventory visibility before food reaches rejection point',
              'Donation routing based on real-time logistics needs',
              'Operational review for food safety and fulfillment quality',
              'Simple follow-up and stakeholder communication',
            ].map((item) => (
              <li key={item} className="flex items-start gap-3 text-sm text-slate-200">
                <CheckCircle2 className="mt-0.5 text-emerald-400" size={18} />
                <span>{item}</span>
              </li>
            ))}
          </ul>
        </div>
      </section>

      <section id="partners" className="space-y-8">
        <div className="text-center">
          <p className="text-sm font-semibold uppercase tracking-[0.2em] text-emerald-700">Who it helps</p>
          <h2 className="mt-3 text-3xl font-bold text-slate-900">Designed for both donors and delivery partners</h2>
        </div>

        <div className="grid gap-6 md:grid-cols-2">
          {audienceCards.map(({ icon: Icon, title, description }) => (
            <div key={title} className="rounded-[26px] border border-slate-200 bg-white p-6 shadow-sm">
              <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-xl bg-amber-100 text-amber-700">
                <Icon size={22} />
              </div>
              <h3 className="text-2xl font-semibold text-slate-900">{title}</h3>
              <p className="mt-3 text-slate-600">{description}</p>
              <Link to="/register" className="mt-5 inline-flex items-center gap-2 text-sm font-semibold text-emerald-700">
                Get started <ArrowRight size={16} />
              </Link>
            </div>
          ))}
        </div>
      </section>

      <section id="impact" className="rounded-[30px] border border-emerald-100 bg-emerald-50 p-6 lg:p-8">
        <div className="grid gap-8 lg:grid-cols-[0.9fr_1.1fr] lg:items-center">
          <div>
            <p className="text-sm font-semibold uppercase tracking-[0.2em] text-emerald-700">Food sustainability impact</p>
            <h2 className="mt-3 text-3xl font-bold text-slate-900">A platform built to make recovery more visible and resilient</h2>
            <p className="mt-4 text-slate-600">
              FoodShare AI is designed to help teams act earlier, respond faster, and keep more high-quality food moving toward the people who need it most.
            </p>
            <div className="mt-6 space-y-4">
              {[
                'Reduce avoidable disposal risk by improving timing and coordination.',
                'Create more consistent donation workflows across multiple organizations.',
                'Support a sustainability narrative with clearer operational transparency.',
              ].map((item) => (
                <div key={item} className="flex items-start gap-3 text-slate-700">
                  <CheckCircle2 className="mt-0.5 text-emerald-600" size={18} />
                  <span>{item}</span>
                </div>
              ))}
            </div>
          </div>

          <div className="rounded-[24px] border border-emerald-200 bg-white p-4 shadow-sm">
            <div className="mb-3 flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-slate-500">Operational preview</p>
                <h3 className="text-lg font-semibold text-slate-900">Donation readiness map</h3>
              </div>
              <span className="rounded-full bg-emerald-100 px-2 py-1 text-xs font-medium text-emerald-700">Preview</span>
            </div>
            <div className="grid gap-4 sm:grid-cols-3">
              {[
                { title: 'Recovery planning', tone: 'bg-emerald-100 text-emerald-800' },
                { title: 'Donation tracking', tone: 'bg-orange-100 text-orange-800' },
                { title: 'Partner visibility', tone: 'bg-slate-100 text-slate-800' },
              ].map(({ title, tone }) => (
                <div key={title} className={`rounded-2xl p-4 ${tone}`}>
                  <div className="mb-2 h-16 rounded-xl bg-white/70" />
                  <p className="text-sm font-semibold">{title}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}

export default HomePage;
