'use client';
import { useState } from 'react';
import { AppShell } from '@/components/layout/AppShell';
import { PageHeader } from '@/components/layout/PageHeader';
import { AlertDrawer } from '@/components/layout/AlertDrawer';
import { TriageHero } from '@/components/triage/TriageHero';
export default function AlertsPage() { const [open, setOpen] = useState(true); return <AppShell><PageHeader title="Alerts" description="Acknowledge and review backend alert evaluations." /><div className="max-w-4xl rounded-xl border border-slate-800 bg-[#0F172A]/80 p-5"><TriageHero /><button className="mt-5 rounded-lg bg-cyan-500 px-4 py-2 text-sm font-semibold text-slate-950" onClick={() => setOpen(true)}>Open alert drawer</button></div><AlertDrawer open={open} onClose={() => setOpen(false)} /></AppShell>; }
