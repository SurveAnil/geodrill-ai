'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Activity, AlertTriangle, Brain, BookOpen, ChevronLeft, ChevronRight, Layers, Map, Radio, Shield } from 'lucide-react';
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
      <TopNav />
      <div className="flex">
        <aside className={`${collapsed ? 'w-16' : 'w-56'} shrink-0 border-r border-slate-800 bg-[#0B1120] min-h-[calc(100vh-64px)] transition-all`}>
          <div className="p-3 space-y-1">
            {navigation.map(({ href, label, icon: Icon }) => {
              const active = pathname === href;
              return <Link key={href} href={href} title={collapsed ? label : undefined} className={`flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm transition ${active ? 'bg-cyan-500/15 text-cyan-300 border border-cyan-500/25' : 'text-slate-400 hover:bg-slate-800/70 hover:text-white'}`}>
                <Icon className="h-4 w-4 shrink-0" /><span className={collapsed ? 'sr-only' : ''}>{label}</span>
              </Link>;
            })}
          </div>
          <div className="mt-auto border-t border-slate-800 p-3 text-[10px] font-mono text-slate-500">
            {!collapsed && <><div className="flex items-center gap-2 text-amber-400"><Shield className="h-3 w-3" /> DEMO / SIMULATED</div><p className="mt-2">Backend-connected data is clearly marked.</p></>}
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
