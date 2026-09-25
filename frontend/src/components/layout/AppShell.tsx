'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Activity, AlertTriangle, Brain, BookOpen, ChevronLeft, ChevronRight, Layers, Map, Radio, X } from 'lucide-react';
import { TopNav } from './TopNav';
import { apiClient } from '@/lib/api';
import { useDrillStore } from '@/store/useDrillStore';

const navigation = [
  { href: '/overview', label: 'Overview', icon: Activity },
  { href: '/telemetry', label: 'Telemetry', icon: Radio },
  { href: '/ai', label: 'AI Copilot', icon: Brain },
  { href: '/offset-wells', label: 'Offset Wells', icon: Map },
  { href: '/stratigraphy', label: 'Stratigraphy', icon: Layers },
  { href: '/lessons', label: 'Lessons', icon: BookOpen },
  { href: '/alerts', label: 'Alerts', icon: AlertTriangle },
];

export function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const [collapsed, setCollapsed] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);
  const setActiveWellContext = useDrillStore((state) => state.setActiveWellContext);
  const setBackendStatus = useDrillStore((state) => state.setBackendStatus);
  const activeWellId = useDrillStore((state) => state.activeWellId);
  React.useEffect(() => {
    apiClient.listWells()
      .then((wells) => {
        const persistedWellId = typeof window !== 'undefined'
          ? window.localStorage.getItem('geodrill.activeWellId')
          : null;
        const active = wells.find((well) => well.well_id === persistedWellId)
          || wells.find((well) => well.well_id === activeWellId)
          || wells.find((well) => well.status === 'active')
          || wells[0];
        if (active) setActiveWellContext(active);
        setBackendStatus('online');
      })
      .catch(() => {
        setBackendStatus('unavailable');
      });
  }, [activeWellId, setActiveWellContext, setBackendStatus]);
  return (
    <div className="min-h-screen bg-[#090D16] text-slate-100">
      <TopNav onMenuOpen={() => setMobileOpen(true)} />
      <div className="flex">
        {mobileOpen && <button aria-label="Close navigation" onClick={() => setMobileOpen(false)} className="fixed inset-0 z-[55] bg-slate-950/70 md:hidden" />}
        <aside aria-label="Primary navigation" className={`${mobileOpen ? 'translate-x-0' : '-translate-x-full hidden md:block'} fixed inset-y-0 left-0 z-[60] w-72 border-r border-slate-800 bg-[#0B1120] pt-3 shadow-2xl transition-transform md:static md:translate-x-0 md:pt-0 ${collapsed ? 'md:w-16' : 'md:w-56'} shrink-0 min-h-[calc(100vh-64px)]`}>
          <button onClick={() => setMobileOpen(false)} className="absolute right-3 top-3 rounded p-1 text-slate-400 md:hidden" aria-label="Close navigation"><X className="h-5 w-5" /></button>
          <div className="p-3 space-y-1">
            {navigation.map(({ href, label, icon: Icon }) => {
              const active = pathname === href;
              return <Link key={href} href={href} onClick={() => setMobileOpen(false)} aria-label={`Navigate to ${label}`} title={collapsed && !mobileOpen ? label : undefined} className={`flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm transition ${active ? 'bg-cyan-500/15 text-cyan-300 border border-cyan-500/25' : 'text-slate-400 hover:bg-slate-800/70 hover:text-white'}`}>
                <Icon className="h-4 w-4 shrink-0" /><span className={collapsed && !mobileOpen ? 'sr-only' : ''}>{label}</span>
              </Link>;
            })}
          </div>
          <button onClick={() => setCollapsed(!collapsed)} className="m-3 rounded border border-slate-700 p-1 text-slate-400 hover:text-white" aria-label="Toggle sidebar">
            {collapsed ? <ChevronRight className="h-4 w-4" /> : <ChevronLeft className="h-4 w-4" />}
          </button>
        </aside>
        <main className="min-w-0 flex-1 p-4 lg:p-6">{children}</main>
      </div>
    </div>
  );
}
