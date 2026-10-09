import { BarChart3, Bell, Boxes, HandHeart, LayoutDashboard, Users } from 'lucide-react';
import { Link, NavLink } from 'react-router-dom';

const defaultNavItems = [
  { label: 'Overview', to: '/dashboard', icon: LayoutDashboard },
  { label: 'Inventory', to: '/dashboard', icon: Boxes },
  { label: 'Donations', to: '/dashboard', icon: HandHeart },
  { label: 'Analytics', to: '/dashboard', icon: BarChart3 },
  { label: 'Users', to: '/admin', icon: Users },
  { label: 'Alerts', to: '/dashboard', icon: Bell },
];

function Sidebar({ navItems = defaultNavItems, title = 'Operations hub', subtitle = 'Workspace' }) {
  return (
    <aside className="hidden w-72 shrink-0 rounded-2xl border border-slate-200 bg-white p-5 shadow-sm lg:block">
      <div className="mb-8">
        <p className="text-sm font-semibold uppercase tracking-[0.2em] text-emerald-600">{subtitle}</p>
        <h2 className="mt-2 text-xl font-bold text-slate-900">{title}</h2>
      </div>

      <nav className="space-y-2">
        {navItems.map(({ label, to, icon: Icon }) => (
          <NavLink
            key={label}
            to={to}
            className={({ isActive }) =>
              `flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium transition ${
                isActive ? 'bg-emerald-100 text-emerald-800' : 'text-slate-600 hover:bg-slate-100 hover:text-slate-900'
              }`
            }
          >
            {Icon ? <Icon size={16} /> : null}
            {label}
          </NavLink>
        ))}
      </nav>

      <div className="mt-8 rounded-2xl bg-slate-900 p-4 text-slate-100">
        <p className="text-xs uppercase tracking-[0.18em] text-slate-400">Preview mode</p>
        <p className="mt-2 text-sm text-slate-200">This dashboard shell is ready for future operational modules, analytics widgets, and partner workflows.</p>
        <Link to="/contact" className="mt-4 inline-block text-sm font-medium text-emerald-300">
          Request pilot access
        </Link>
      </div>
    </aside>
  );
}

export default Sidebar;
