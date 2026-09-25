'use client';
import { Suspense } from 'react';
import { AppShell } from '@/components/layout/AppShell';
import { PageHeader } from '@/components/layout/PageHeader';
import { LessonsLearnedRepository } from '@/components/lessons/LessonsLearnedRepository';
export default function LessonsPage() { return <AppShell><PageHeader title="Lessons Learned" description="Traceable incident knowledge and remediation notes." /><div className="mx-auto max-w-5xl rounded-xl border border-slate-800 bg-[#0F172A]/80 p-3 sm:p-5"><Suspense fallback={<div className="p-5 text-sm text-slate-400">Loading lessons…</div>}><LessonsLearnedRepository /></Suspense></div></AppShell>; }
