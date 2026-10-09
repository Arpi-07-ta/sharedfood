import { ArrowLeft } from 'lucide-react';
import { Link } from 'react-router-dom';

import Button from '../components/ui/Button';

function NotFoundPage() {
  return (
    <div className="mx-auto max-w-xl py-12 text-center">
      <div className="rounded-[30px] border border-slate-200 bg-white p-8 shadow-sm">
        <p className="text-sm font-semibold uppercase tracking-[0.2em] text-amber-600">404</p>
        <h1 className="mt-3 text-4xl font-black text-slate-900">Page not found</h1>
        <p className="mt-4 text-slate-600">
          The route you requested is not part of the current FoodShare AI frontend build yet.
        </p>
        <Link to="/" className="mt-6 inline-flex items-center gap-2">
          <Button>
            <ArrowLeft size={16} />
            Back home
          </Button>
        </Link>
      </div>
    </div>
  );
}

export default NotFoundPage;
