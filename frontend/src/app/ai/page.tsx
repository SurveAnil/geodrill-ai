'use client';
import { Suspense } from 'react';
import { AppShell } from '@/components/layout/AppShell';
import { PageHeader } from '@/components/layout/PageHeader';
import { AIPanelContainer } from '@/components/ai/AIPanelContainer';
export default function AIPage() { return <AppShell><PageHeader title="AI Copilot" description="Ask traceable questions about current drilling context and historical offset-well evidence." /><div className="mx-auto max-w-4xl rounded-xl border border-slate-800 bg-[#0F172A]/80 p-3 sm:p-5"><Suspense fallback={<div className="p-5 text-sm text-slate-400">Loading AI Copilot…</div>}><AIPanelContainer /></Suspense></div></AppShell>; }
