'use client';
import { AppShell } from '@/components/layout/AppShell';
import { PageHeader } from '@/components/layout/PageHeader';
import { GeospatialPanel } from '@/components/geospatial/GeospatialPanel';
export default function OffsetWellsPage() { return <AppShell><PageHeader title="Offset Wells" description="Compare nearby wells and their historical evidence against the active drilling context." /><div className="mx-auto mb-4 max-w-5xl rounded-xl border border-cyan-800/50 bg-cyan-950/20 p-3 text-sm text-cyan-100">OIL-NWIS-01 is currently at 3,108 m MD in Northwind Sandstone — the wells below contain comparable historical evidence.</div><div className="mx-auto max-w-5xl rounded-xl border border-slate-800 bg-[#0F172A]/80 p-3 sm:p-5"><GeospatialPanel /></div></AppShell>; }
