'use client';
import { AppShell } from '@/components/layout/AppShell';
import { PageHeader } from '@/components/layout/PageHeader';
import { LessonsLearnedRepository } from '@/components/lessons/LessonsLearnedRepository';
export default function LessonsPage() { return <AppShell><PageHeader title="Lessons learned" description="Traceable incident knowledge and remediation notes." /><div className="max-w-5xl rounded-xl border border-slate-800 bg-[#0F172A]/80 p-5"><LessonsLearnedRepository /></div></AppShell>; }
