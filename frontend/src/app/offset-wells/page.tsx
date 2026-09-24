'use client';
import { AppShell } from '@/components/layout/AppShell';
import { PageHeader } from '@/components/layout/PageHeader';
import { GeospatialPanel } from '@/components/geospatial/GeospatialPanel';
export default function OffsetWellsPage() { return <AppShell><PageHeader title="Offset wells" description="Nearby-well results from the backend spatial API." /><div className="max-w-5xl rounded-xl border border-slate-800 bg-[#0F172A]/80 p-5"><GeospatialPanel /></div></AppShell>; }
