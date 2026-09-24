'use client';
import { AppShell } from '@/components/layout/AppShell';
import { PageHeader } from '@/components/layout/PageHeader';
import { StratigraphicCorrelation } from '@/components/stratigraphy/StratigraphicCorrelation';
export default function StratigraphyPage() { return <AppShell><PageHeader title="Stratigraphy" description="Formation correlation and depth context." /><div className="max-w-5xl rounded-xl border border-slate-800 bg-[#0F172A]/80 p-5"><StratigraphicCorrelation /></div></AppShell>; }
