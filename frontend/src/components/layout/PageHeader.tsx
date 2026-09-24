'use client';

import Link from 'next/link';
import { ChevronRight } from 'lucide-react';

export function PageHeader({ title, description }: { title: string; description?: string }) {
  return <header className="mb-5">
    <nav className="mb-2 flex items-center gap-1 text-xs text-slate-500"><Link href="/overview" className="hover:text-cyan-300">Operations</Link><ChevronRight className="h-3 w-3" /><span className="text-slate-300">{title}</span></nav>
    <div className="flex flex-wrap items-end justify-between gap-3"><div><h1 className="text-2xl font-semibold text-white">{title}</h1>{description && <p className="mt-1 text-sm text-slate-400">{description}</p>}</div><span className="rounded border border-amber-700/60 bg-amber-950/40 px-2 py-1 text-[10px] font-mono uppercase tracking-wider text-amber-300">Demo / Simulated</span></div>
  </header>;
}
