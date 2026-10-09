const variants = {
  success: 'bg-emerald-100 text-emerald-800 border border-emerald-200',
  warning: 'bg-amber-100 text-amber-800 border border-amber-200',
  neutral: 'bg-slate-100 text-slate-700 border border-slate-200',
  danger: 'bg-red-100 text-red-700 border border-red-200',
};

function StatusBadge({ label, variant = 'neutral' }) {
  return (
    <span className={`inline-flex items-center rounded-full px-2.5 py-1 text-xs font-semibold ${variants[variant]}`}>
      {label}
    </span>
  );
}

export default StatusBadge;
