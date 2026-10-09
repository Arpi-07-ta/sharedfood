import { useState } from 'react';
import { Bell, ChevronDown, LogOut, Search, UserCircle2 } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

import { useAuth } from '../../hooks/useAuth';
import Sidebar from '../layout/Sidebar';

function DashboardLayout({ title, subtitle, roleLabel, navItems, children }) {
  const navigate = useNavigate();
  const { user, logout } = useAuth();
  const [menuOpen, setMenuOpen] = useState(false);

  const displayUser = user || { name: 'Guest user', role: roleLabel || 'Dashboard' };

  const handleLogout = () => {
    logout();
    setMenuOpen(false);
    navigate('/login');
  };

  return (
    <div className="flex gap-6 py-4">
      <Sidebar navItems={navItems} title={`${roleLabel} workspace`} />

      <div className="flex-1 space-y-6">
        <header className="rounded-[28px] border border-slate-200 bg-white p-5 shadow-sm">
          <div className="flex flex-col gap-4 xl:flex-row xl:items-center xl:justify-between">
            <div>
              <p className="text-sm uppercase tracking-[0.2em] text-emerald-700">FoodShare AI</p>
              <h1 className="mt-2 text-3xl font-bold text-slate-900">{title}</h1>
              {subtitle ? <p className="mt-2 text-sm text-slate-500">{subtitle}</p> : null}
            </div>

            <div className="flex items-center gap-3">
              <div className="hidden items-center gap-2 rounded-full border border-slate-200 bg-slate-50 px-3 py-2 text-sm text-slate-600 md:flex">
                <Search size={15} />
                Quick overview
              </div>

              <button
                type="button"
                className="relative flex h-11 w-11 items-center justify-center rounded-full border border-slate-200 bg-slate-50 text-slate-700"
                aria-label="Notifications"
              >
                <Bell size={18} />
                <span className="absolute -right-1 -top-1 flex h-5 min-w-5 items-center justify-center rounded-full bg-emerald-600 px-1 text-[10px] font-bold text-white">
                  3
                </span>
              </button>

              <div className="relative">
                <button
                  type="button"
                  onClick={() => setMenuOpen((current) => !current)}
                  className="flex items-center gap-3 rounded-full border border-slate-200 bg-slate-50 px-2 py-2 text-left"
                >
                  <div className="flex h-10 w-10 items-center justify-center rounded-full bg-emerald-100 text-emerald-700">
                    <UserCircle2 size={22} />
                  </div>
                  <div className="hidden text-left sm:block">
                    <p className="text-sm font-semibold text-slate-800">{displayUser.name}</p>
                    <p className="text-[10px] uppercase tracking-[0.18em] text-slate-500">{displayUser.role}</p>
                  </div>
                  <ChevronDown size={16} className="text-slate-500" />
                </button>

                {menuOpen ? (
                  <div className="absolute right-0 z-20 mt-2 w-52 rounded-2xl border border-slate-200 bg-white p-2 shadow-lg">
                    <button type="button" className="flex w-full items-center justify-between rounded-xl px-3 py-2 text-sm text-slate-700 hover:bg-slate-50">
                      <span>Profile</span>
                    </button>
                    <button type="button" onClick={handleLogout} className="mt-1 flex w-full items-center justify-between rounded-xl px-3 py-2 text-sm text-red-600 hover:bg-red-50">
                      <span>Logout</span>
                      <LogOut size={16} />
                    </button>
                  </div>
                ) : null}
              </div>
            </div>
          </div>
        </header>

        {children}
      </div>
    </div>
  );
}

export default DashboardLayout;
