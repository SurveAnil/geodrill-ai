'use client';

import React from 'react';
import { Target, Compass, Activity, Radio, ShieldAlert } from 'lucide-react';
import { useDrillStore } from '@/store/useDrillStore';

export const ActiveContextBar: React.FC = () => {
  const {
    activeWellId,
    wellName,
    activeWellLocation,
    telemetry,
    risk,
    operatingMode,
  } = useDrillStore();

  const wellIdentifier = wellName || activeWellId || 'OIL-NWIS-01';
  const md = telemetry.measuredDepthM || 3108.0;
  const tvd = telemetry.trueVerticalDepthM || 3032.0;
  const formation = telemetry.currentFormation || 'Northwind Sandstone';
  const lat = activeWellLocation?.latitude ?? 58.4121;
  const lon = activeWellLocation?.longitude ?? 1.8422;

  return (
    <section
      aria-label="Active Drilling Well Context"
      className="rounded-xl border border-cyan-500/30 bg-[#0F172A]/90 p-3.5 shadow-lg backdrop-blur-md"
    >
      <div className="flex flex-wrap items-center justify-between gap-3">
        {/* Left: Active Well Identity */}
        <div className="flex items-center gap-3">
          <div className="relative flex h-9 w-9 shrink-0 items-center justify-center rounded-lg border border-cyan-500/40 bg-cyan-950/60 text-cyan-300 shadow-[0_0_15px_-3px_rgba(6,182,212,0.4)]">
            <Target className="h-5 w-5 animate-pulse text-cyan-400" />
            <span className="absolute -top-1 -right-1 flex h-2.5 w-2.5">
              <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-cyan-400 opacity-75" />
              <span className="relative inline-flex h-2.5 w-2.5 rounded-full bg-cyan-500" />
            </span>
          </div>

          <div>
            <div className="flex items-center gap-2">
              <span className="font-mono text-[10px] font-bold tracking-wider uppercase text-cyan-400">
                ACTIVE WELL REFERENCE
              </span>
              <span className="rounded border border-emerald-500/40 bg-emerald-950/60 px-1.5 py-0.5 font-mono text-[9px] font-bold text-emerald-300">
                ROTARY DRILLING
              </span>
              <span className="rounded border border-amber-500/40 bg-amber-950/50 px-1.5 py-0.5 font-mono text-[9px] font-semibold text-amber-300">
                {operatingMode || 'DEMO'}
              </span>
            </div>
            <h2 className="font-mono text-base font-bold text-white tracking-tight">
              {wellIdentifier}
            </h2>
          </div>
        </div>

        {/* Center: Real-Time Drilling Horizon Metadata */}
        <div className="flex flex-wrap items-center gap-4 text-xs font-mono">
          <div className="rounded-lg border border-slate-800 bg-slate-900/60 px-3 py-1.5">
            <span className="text-[10px] uppercase text-slate-400">Current MD</span>
            <p className="font-bold text-slate-100">{md.toLocaleString()} m</p>
          </div>

          <div className="rounded-lg border border-slate-800 bg-slate-900/60 px-3 py-1.5">
            <span className="text-[10px] uppercase text-slate-400">Current TVD</span>
            <p className="font-bold text-slate-200">{tvd.toLocaleString()} m</p>
          </div>

          <div className="rounded-lg border border-slate-800 bg-slate-900/60 px-3 py-1.5">
            <span className="text-[10px] uppercase text-slate-400">Formation Horizon</span>
            <p className="font-bold text-cyan-300">{formation}</p>
          </div>

          <div className="hidden rounded-lg border border-slate-800 bg-slate-900/60 px-3 py-1.5 sm:block">
            <span className="text-[10px] uppercase text-slate-400">Surface Anchor</span>
            <p className="flex items-center gap-1 text-slate-300">
              <Compass className="h-3 w-3 text-cyan-400" />
              {lat.toFixed(4)}° N, {lon.toFixed(4)}° E
            </p>
          </div>
        </div>

        {/* Right: Operational Spatial Rule Notification */}
        <div className="flex items-center gap-2 rounded-lg border border-cyan-800/40 bg-cyan-950/20 px-3 py-1.5 text-right text-[11px] text-cyan-200">
          <Radio className="h-3.5 w-3.5 shrink-0 text-cyan-400" />
          <span className="hidden xl:inline">
            Nearby offset-well proximity, hazard logs & lithology cross-checks are indexed relative to this active rig position.
          </span>
          <span className="xl:hidden">Relative to active rig position</span>
        </div>
      </div>
    </section>
  );
};
