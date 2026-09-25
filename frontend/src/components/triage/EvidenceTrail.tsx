'use client';

import Link from 'next/link';
import { ArrowRight, Brain, ChevronDown, ChevronUp, FileSearch } from 'lucide-react';
import { useState } from 'react';
import { OFFSET_EVIDENCE } from '@/lib/presentation';
import { useDrillStore } from '@/store/useDrillStore';

export function EvidenceTrail({ expandedByDefault = false }: { expandedByDefault?: boolean }) {
  const [open, setOpen] = useState(expandedByDefault);
  const { telemetry, risk } = useDrillStore();
  return <section className="rounded-xl border border-orange-700/40 bg-orange-950/15 p-4" aria-label="Offset evidence trail">
    <div className="flex flex-wrap items-start justify-between gap-3">
      <div><p className="ops-eyebrow text-orange-300">Offset evidence</p><h2 className="mt-1 text-base font-semibold text-white">Why this risk matters</h2><p className="mt-1 text-xs text-slate-400">Current: {telemetry.measuredDepthM.toLocaleString()} m MD • {telemetry.currentFormation} • Risk {risk.riskScore}/100</p></div>
      <button onClick={() => setOpen(!open)} aria-expanded={open} aria-controls="offset-evidence-details" className="inline-flex items-center gap-1 rounded-lg border border-orange-700/60 px-3 py-1.5 text-xs font-semibold text-orange-200 hover:bg-orange-950/60">{open ? 'Hide evidence' : 'View 2 incidents'} {open ? <ChevronUp className="h-3.5 w-3.5" /> : <ChevronDown className="h-3.5 w-3.5" />}</button>
    </div>
    {open && <div id="offset-evidence-details" className="mt-4 grid gap-3 md:grid-cols-2">{OFFSET_EVIDENCE.map((item) => <article key={item.well} className="rounded-lg border border-slate-700/70 bg-[#0A101D] p-3"><div className="flex items-center gap-2 text-xs"><FileSearch className="h-4 w-4 text-cyan-400" /><span className="font-mono font-semibold text-cyan-300">{item.well}</span><span className="text-slate-500">→</span><span className="font-semibold text-white">{item.incident}</span></div><p className="mt-2 text-xs text-slate-300">{item.depthM.toLocaleString()} m MD • {item.detail}</p></article>)}</div>}
    <div className="mt-4 flex flex-wrap gap-3 text-xs"><Link href="/lessons?evidence=northwind" className="inline-flex items-center gap-1 text-cyan-300 hover:text-cyan-200">View evidence <ArrowRight className="h-3.5 w-3.5" /></Link><Link href={`/ai?prompt=${encodeURIComponent('Why was this alert generated? Summarize the offset incidents near my current depth.')}`} className="inline-flex items-center gap-1 text-purple-300 hover:text-purple-200">Ask AI <Brain className="h-3.5 w-3.5" /></Link></div>
  </section>;
}
