'use client';

import { AlertTriangle, X } from 'lucide-react';

export function AlertDrawer({ open, onClose }: { open: boolean; onClose: () => void }) {
  if (!open) return null;
  return <div className="fixed inset-y-0 right-0 z-[60] w-full max-w-md border-l border-slate-700 bg-[#0B1120] p-5 shadow-2xl">
    <div className="flex items-center justify-between"><h2 className="flex items-center gap-2 font-semibold"><AlertTriangle className="h-4 w-4 text-amber-400" />Alert drawer</h2><button onClick={onClose} aria-label="Close alerts"><X className="h-5 w-5" /></button></div>
    <p className="mt-6 rounded-lg border border-slate-800 bg-slate-900/60 p-4 text-sm text-slate-400">No active alerts. New risk conditions and their supporting evidence will appear here.</p>
  </div>;
}
