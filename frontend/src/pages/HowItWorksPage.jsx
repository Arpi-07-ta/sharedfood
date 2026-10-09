import { ArrowRight, BellRing, PackageCheck, Route, SearchCheck } from 'lucide-react';

const steps = [
  {
    icon: SearchCheck,
    title: 'Identify surplus',
    description: 'Capture food availability, pickup timing, storage constraints, and priority needs before inventory is lost.',
  },
  {
    icon: Route,
    title: 'Match and route',
    description: 'Use operational logic and forecasting cues to route donations to the best recipient or recovery path.',
  },
  {
    icon: PackageCheck,
    title: 'Track fulfillment',
    description: 'Monitor handoff status, timing, and delivery readiness to keep stakeholders aligned.',
  },
  {
    icon: BellRing,
    title: 'Review impact',
    description: 'Measure response quality over time and understand whether the system is improving recovery performance.',
  },
];

function HowItWorksPage() {
  return (
    <div className="space-y-8 py-4">
      <section className="rounded-[28px] bg-slate-900 px-6 py-10 text-white sm:px-8 lg:px-12">
        <p className="text-sm font-semibold uppercase tracking-[0.2em] text-emerald-300">How it works</p>
        <h1 className="mt-3 text-4xl font-black tracking-tight">A simple flow for complex food recovery needs</h1>
      </section>

      <section className="grid gap-6 md:grid-cols-2 xl:grid-cols-4">
        {steps.map(({ icon: Icon, title, description }) => (
          <div key={title} className="rounded-[24px] border border-slate-200 bg-white p-6 shadow-sm">
            <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-xl bg-emerald-100 text-emerald-700">
              <Icon size={22} />
            </div>
            <div className="mb-3 text-sm font-semibold uppercase tracking-[0.2em] text-amber-600">Step</div>
            <h2 className="text-xl font-semibold text-slate-900">{title}</h2>
            <p className="mt-3 text-slate-600">{description}</p>
          </div>
        ))}
      </section>

      <section className="rounded-[28px] border border-slate-200 bg-white p-6 shadow-sm lg:p-8">
        <h2 className="text-3xl font-bold text-slate-900">From surplus detection to outcome visibility</h2>
        <div className="mt-6 grid gap-4 md:grid-cols-2">
          {[
            'Donation intake is aligned to eligibility and safety checks before action is taken.',
            'Planned recovery paths reduce operational friction and speed up matching with organizations.',
            'AI-driven insight supports prioritization when supply and demand shift quickly.',
            'Partner teams review outcomes and keep the cycle improving with better reporting contexts.',
          ].map((text, index) => (
            <div key={text} className="flex items-start gap-3 rounded-2xl bg-slate-50 p-4 text-slate-700">
              <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-emerald-600 text-sm font-bold text-white">
                {index + 1}
              </div>
              <span>{text}</span>
            </div>
          ))}
        </div>
        <div className="mt-6 inline-flex items-center gap-2 text-sm font-semibold text-emerald-700">
          Ready to pilot? <ArrowRight size={16} />
        </div>
      </section>
    </div>
  );
}

export default HowItWorksPage;
