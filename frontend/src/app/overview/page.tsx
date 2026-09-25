'use client';

import Link from 'next/link';
import { AppShell } from '@/components/layout/AppShell';
import { PageHeader } from '@/components/layout/PageHeader';
import { TriageHero } from '@/components/triage/TriageHero';
import { EvidenceTrail } from '@/components/triage/EvidenceTrail';
import { DEMO_OFFSET_WELLS } from '@/lib/presentation';
import { useDrillStore } from '@/store/useDrillStore';

export default function OverviewPage() {
  const { telemetry } = useDrillStore();
  return <AppShell><PageHeader title="Operations overview" description="Current drilling context, risk triage, and offset-well intelligence." /><div className="mx-auto max-w-6xl space-y-4"><TriageHero /><EvidenceTrail /><div className="grid gap-4 md:grid-cols-3"><section className="ops-panel p-4"><p className="ops-eyebrow">Offset wells</p><p className="mt-1 text-lg font-semibold">{DEMO_OFFSET_WELLS.length} demo historical wells</p><p className="mt-1 text-xs text-slate-400">Historical reference data is shown without a proximity claim for the active well.</p><Link href="/offset-wells" className="mt-3 inline-block text-xs text-cyan-300">Explore wells →</Link></section><section className="ops-panel p-4"><p className="ops-eyebrow">Formation risk</p><p className="mt-1 text-lg font-semibold">{telemetry.currentFormation}</p><p className="mt-1 text-xs text-slate-400">Historical incidents are reference context for the current {telemetry.measuredDepthM.toLocaleString()} m MD.</p><Link href="/stratigraphy" className="mt-3 inline-block text-xs text-cyan-300">View stratigraphy →</Link></section><section className="ops-panel p-4"><p className="ops-eyebrow">Knowledge base</p><p className="mt-1 text-lg font-semibold">Evidence ready</p><p className="mt-1 text-xs text-slate-400">Query traceable offset-well records and manage source documents.</p><Link href="/ai" className="mt-3 inline-block text-xs text-cyan-300">Open AI Copilot →</Link></section></div><section className="ops-panel overflow-hidden"><div className="flex items-center justify-between px-4 py-3"><div><p className="text-sm font-semibold">Historical demo comparison</p><p className="text-xs text-slate-400">Reference incidents from the seeded offset-well dataset.</p></div><Link href="/offset-wells" className="text-xs text-cyan-300">Full comparison →</Link></div><div className="divide-y divide-slate-800">{DEMO_OFFSET_WELLS.map(well => <div key={well.id} className="flex flex-wrap items-center justify-between gap-2 px-4 py-2.5 text-xs"><span className="font-mono font-semibold text-cyan-300">{well.name}</span><span className="text-slate-300">{well.hazard}</span></div>)}</div></section></div></AppShell>;
}
