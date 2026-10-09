import { ArrowUpRight } from 'lucide-react';

import StatusBadge from '../ui/StatusBadge';

const toneClasses = {
  emerald: 'bg-emerald-100 text-emerald-700',
  amber: 'bg-amber-100 text-amber-700',
  slate: 'bg-slate-100 text-slate-700',
  rose: 'bg-rose-100 text-rose-700',
};

const badgeToneMap = {
  emerald: 'success',
  amber: 'warning',
  slate: 'neutral',
  rose: 'danger',
};

function SummaryCard({ label, value, detail, tone = 'slate', icon: Icon }) {
  return (
    <div className="rounded-[24px] border border-slate-200 bg-white p-5 shadow-sm">
      <div className="flex items-center justify-between">
        <div className={`flex h-11 w-11 items-center justify-center rounded-xl ${toneClasses[tone]}`}>
          {Icon ? <Icon size={18} /> : null}
        </div>
        <ArrowUpRight size={18} className="text-slate-400" />
      </div>

      <p className="mt-5 text-sm text-slate-500">{label}</p>
      <p className="mt-2 text-2xl font-bold text-slate-900">{value}</p>
      <div className="mt-4">
        <StatusBadge label={detail} variant={badgeToneMap[tone] || 'neutral'} />
      </div>
    </div>
  );
}

export default SummaryCard;
