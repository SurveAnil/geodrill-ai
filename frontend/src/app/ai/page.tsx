'use client';
import { AppShell } from '@/components/layout/AppShell';
import { PageHeader } from '@/components/layout/PageHeader';
import { AIPanelContainer } from '@/components/ai/AIPanelContainer';
export default function AIPage() { return <AppShell><PageHeader title="AI copilot" description="Traceable search and predictive risk context. No new model or OCR processing is performed here." /><div className="max-w-4xl rounded-xl border border-slate-800 bg-[#0F172A]/80 p-5"><AIPanelContainer /></div></AppShell>; }
