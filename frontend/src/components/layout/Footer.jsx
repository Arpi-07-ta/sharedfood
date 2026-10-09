import { Link } from 'react-router-dom';
import { Leaf } from 'lucide-react';

function Footer() {
  return (
    <footer className="border-t border-slate-200 bg-slate-950 text-slate-200">
      <div className="mx-auto grid max-w-7xl gap-10 px-4 py-10 sm:px-6 lg:grid-cols-4 lg:px-8">
        <div>
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-emerald-600 text-white">
              <Leaf size={18} />
            </div>
            <div>
              <div className="font-bold text-white">FoodShare AI</div>
              <div className="text-[10px] uppercase tracking-[0.22em] text-emerald-300">Impact platform</div>
            </div>
          </div>
          <p className="mt-4 text-sm text-slate-300">
            A sustainability-first platform concept for tracking food donations, reducing waste, and improving supply coordination.
          </p>
        </div>

        <div>
          <h3 className="text-sm font-semibold uppercase tracking-[0.2em] text-slate-400">Company</h3>
          <ul className="mt-4 space-y-2 text-sm text-slate-300">
            <li><Link to="/about" className="hover:text-white">About us</Link></li>
            <li><Link to="/how-it-works" className="hover:text-white">How it works</Link></li>
            <li><Link to="/contact" className="hover:text-white">Contact</Link></li>
          </ul>
        </div>

        <div>
          <h3 className="text-sm font-semibold uppercase tracking-[0.2em] text-slate-400">Resources</h3>
          <ul className="mt-4 space-y-2 text-sm text-slate-300">
            <li><a href="#features" className="hover:text-white">Features</a></li>
            <li><a href="#impact" className="hover:text-white">Impact</a></li>
            <li><a href="#partners" className="hover:text-white">Partners</a></li>
          </ul>
        </div>

        <div>
          <h3 className="text-sm font-semibold uppercase tracking-[0.2em] text-slate-400">Contact</h3>
          <ul className="mt-4 space-y-2 text-sm text-slate-300">
            <li>hello@foodshareai.example</li>
            <li>+1 (555) 942-8846</li>
            <li>Remote operations</li>
          </ul>
        </div>
      </div>

      <div className="border-t border-slate-800 py-4 text-center text-xs text-slate-400">
        © 2026 FoodShare AI. Designed for sustainable food operations.
      </div>
    </footer>
  );
}

export default Footer;
