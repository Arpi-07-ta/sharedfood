function FilterBar({ items = [], activeItem, onChange }) {
  return (
    <div className="flex flex-wrap gap-2 rounded-2xl border border-slate-200 bg-slate-50 p-2">
      {items.map((item) => {
        const isActive = activeItem === item;

        return (
          <button
            key={item}
            type="button"
            onClick={() => onChange(item)}
            className={`rounded-xl px-3 py-2 text-sm font-medium transition ${
              isActive
                ? 'bg-emerald-600 text-white shadow-sm'
                : 'bg-white text-slate-600 hover:bg-slate-100 hover:text-slate-900'
            }`}
          >
            {item}
          </button>
        );
      })}
    </div>
  );
}

export default FilterBar;
