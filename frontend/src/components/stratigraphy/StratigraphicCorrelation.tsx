'use client';

import React, { useEffect, useState } from 'react';
import { Layers, AlertTriangle, Crosshair, ArrowDown, ChevronRight, Activity } from 'lucide-react';
import { useDrillStore } from '@/store/useDrillStore';
import { apiClient } from '@/lib/api';

// Geological Depth Bounds for the correlation window
const MIN_DEPTH = 2200;
const MAX_DEPTH = 3000;
const TOTAL_DEPTH_SPAN = MAX_DEPTH - MIN_DEPTH;

interface FormationBlock {
  name: string;
  shortName: string;
  topM: number;
  bottomM: number;
  colorBg: string;
  borderColor: string;
  textColor: string;
  lithology: string;
}

const OFFSET_FORMATIONS: FormationBlock[] = [
  {
    name: 'Chalk / Shetland Group',
    shortName: 'Chalk Gp',
    topM: 2200,
    bottomM: 2420,
    colorBg: 'bg-slate-800/80',
    borderColor: 'border-slate-700',
    textColor: 'text-slate-300',
    lithology: 'Dense Limestone / Chalk',
  },
  {
    name: 'Hugin Formation / Krishna Sand-B',
    shortName: 'Hugin / Krishna Sand-B',
    topM: 2420,
    bottomM: 2750,
    colorBg: 'bg-amber-950/40',
    borderColor: 'border-amber-700/60',
    textColor: 'text-amber-300',
    lithology: 'Porous Sandstone (Hydrocarbon Bearing)',
  },
  {
    name: 'Skagerrak Formation',
    shortName: 'Skagerrak Fm',
    topM: 2750,
    bottomM: 3000,
    colorBg: 'bg-teal-950/40',
    borderColor: 'border-teal-700/60',
    textColor: 'text-teal-300',
    lithology: 'Interbedded Sandstone & Claystone',
  },
];

// Severe Hazard Horizon Overlay (2440m - 2500m)
const HAZARD_HORIZON = {
  name: 'Severe Mud Loss Horizon',
  topM: 2440,
  bottomM: 2500,
  lossRate: '65 bbl/hr',
  citation: 'Offset ONGC-KG-07 @ 2450m',
};

export const StratigraphicCorrelation: React.FC = () => {
  const { telemetry, activeWellId } = useDrillStore();
  const [correlationLabel, setCorrelationLabel] = useState('Demo correlation (API unavailable)');
  const currentMD = telemetry.measuredDepthM;
  useEffect(() => {
    let cancelled = false;
    apiClient.correlateFormations(
      [{ md: 0, inclination: 0, azimuth: 0 }, { md: currentMD, inclination: 5, azimuth: 90 }],
      OFFSET_FORMATIONS.map((formation) => ({ formation_name: formation.name, top_depth_m: formation.topM })),
    ).then((response) => {
      if (!cancelled) setCorrelationLabel(`Backend trajectory correlation • ${response.correlations.length} tops`);
    }).catch(() => {
      if (!cancelled) setCorrelationLabel('Demo correlation (API unavailable)');
    });
    return () => { cancelled = true; };
  }, [currentMD, activeWellId]);

  // Calculate percentage down the column (clamped between 0% and 100%)
  const bitProgressPct = Math.min(
    100,
    Math.max(0, ((currentMD - MIN_DEPTH) / TOTAL_DEPTH_SPAN) * 100)
  );

  const hazardTopPct = ((HAZARD_HORIZON.topM - MIN_DEPTH) / TOTAL_DEPTH_SPAN) * 100;
  const hazardHeightPct =
    ((HAZARD_HORIZON.bottomM - HAZARD_HORIZON.topM) / TOTAL_DEPTH_SPAN) * 100;

  // Calculate distance to mud loss hazard horizon
  const distanceToHazard = HAZARD_HORIZON.topM - currentMD;

  return (
    <div className="flex flex-col h-full justify-between">
      {/* Header */}
      <div className="flex items-center justify-between pb-2.5 border-b border-slate-800">
        <div className="flex items-center gap-2">
          <div className="p-1.5 rounded-lg bg-amber-950/60 border border-amber-800/50 text-amber-400">
            <Layers className="w-4 h-4" />
          </div>
          <div>
            <h3 className="text-xs font-bold text-white tracking-wide uppercase">
              Stratigraphic Depth Cross-Correlation
            </h3>
            <span className="text-[10px] text-slate-400 font-mono">
              Layer 3 • Active Depth vs Offset Lithology
            </span>
          </div>
        </div>

        {/* Live Horizon Proximity Pill */}
        <div className="flex items-center gap-2">
          {distanceToHazard > 0 && distanceToHazard <= 50 ? (
            <span className="px-2.5 py-1 rounded-full text-[10px] font-mono font-bold uppercase bg-red-950 text-red-300 border border-red-800/80 animate-pulse flex items-center gap-1.5">
              <AlertTriangle className="w-3 h-3 text-red-400" />
              <span>{distanceToHazard.toFixed(1)}m To Loss Zone</span>
            </span>
          ) : distanceToHazard <= 0 && currentMD <= HAZARD_HORIZON.bottomM ? (
            <span className="px-2.5 py-1 rounded-full text-[10px] font-mono font-bold uppercase bg-red-950 text-red-300 border border-red-800 animate-pulse">
              ⚠️ INSIDE HAZARD HORIZON
            </span>
          ) : (
            <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-[#0A101D] text-slate-400 border border-slate-800">
              Correlated Window: 2,200m – 3,000m
            </span>
          )}
        </div>
      </div>

      {/* Main Vertical Track Visualizer */}
      <div className="relative my-3 flex-1 min-h-[220px] bg-[#070B14] rounded-lg border border-slate-800/90 p-3 flex gap-3 overflow-hidden">
        {/* Y-Axis Depth Scale */}
        <div className="w-14 flex flex-col justify-between text-[10px] font-mono text-slate-500 border-r border-slate-800/80 pr-2 select-none">
          <span style={{ fontVariantNumeric: 'tabular-nums' }}>2,200m</span>
          <span style={{ fontVariantNumeric: 'tabular-nums' }}>2,400m</span>
          <span style={{ fontVariantNumeric: 'tabular-nums' }} className="text-amber-400/80">
            2,450m
          </span>
          <span style={{ fontVariantNumeric: 'tabular-nums' }}>2,600m</span>
          <span style={{ fontVariantNumeric: 'tabular-nums' }}>2,800m</span>
          <span style={{ fontVariantNumeric: 'tabular-nums' }}>3,000m</span>
        </div>

        {/* Tracks Area (Relative container for absolute bit projection line) */}
        <div className="relative flex-1 grid grid-cols-2 gap-4">
          {/* TRACK 1: Active Well (Target Rig) */}
          <div className="relative flex flex-col h-full bg-[#0A101D] rounded-lg border border-slate-800 p-2 overflow-hidden">
            <div className="text-[10px] font-mono font-semibold text-cyan-400 pb-1 border-b border-slate-800/80 flex items-center justify-between">
              <span>ACTIVE: {activeWellId}</span>
              <span className="text-[9px] text-slate-500 uppercase">Target 09</span>
            </div>

            {/* Borehole Center Track */}
            <div className="relative flex-1 my-1 flex justify-center">
              {/* Drilled Wellbore Cavity */}
              <div className="w-6 h-full bg-slate-900/90 border-x border-slate-800/60 relative">
                {/* Drilled Depth Fill */}
                <div
                  className="w-full bg-gradient-to-b from-cyan-900/30 to-cyan-500/40 border-b-2 border-cyan-400 transition-all duration-100 ease-linear"
                  style={{ height: `${bitProgressPct}%` }}
                />
              </div>
            </div>

            <div className="text-[10px] font-mono text-slate-400 pt-1 border-t border-slate-800/80 flex items-center justify-between">
              <span>Formation:</span>
              <span className="font-semibold text-amber-300 truncate max-w-[110px]">
                {telemetry.currentFormation}
              </span>
            </div>
          </div>

          {/* TRACK 2: Offset Well (ONGC-KG-07 / 15/9-F-12) with Geological Formations */}
          <div className="relative flex flex-col h-full bg-[#0A101D] rounded-lg border border-slate-800 p-2 overflow-hidden">
            <div className="text-[10px] font-mono font-semibold text-amber-400 pb-1 border-b border-slate-800/80 flex items-center justify-between">
              <span>OFFSET: ONGC-KG-07-ALOK</span>
              <span className="text-[9px] text-slate-500 uppercase">2.4 km</span>
            </div>

            {/* Stacked Geological Formations */}
            <div className="relative flex-1 my-1 flex flex-col justify-between">
              {OFFSET_FORMATIONS.map((f, i) => {
                const heightPct = ((f.bottomM - f.topM) / TOTAL_DEPTH_SPAN) * 100;
                return (
                  <div
                    key={i}
                    style={{ height: `${heightPct}%` }}
                    className={`w-full border-b ${f.borderColor} ${f.colorBg} px-2 py-1 flex flex-col justify-between transition-colors`}
                  >
                    <div className="flex items-center justify-between">
                      <span className={`text-[10px] font-bold ${f.textColor} truncate`}>
                        {f.shortName}
                      </span>
                      <span className="text-[9px] font-mono text-slate-500">
                        {f.topM}–{f.bottomM}m
                      </span>
                    </div>
                    <span className="text-[8.5px] text-slate-400 font-mono truncate">
                      {f.lithology}
                    </span>
                  </div>
                );
              })}

              {/* HAZARD HORIZON OVERLAY (Red Hatched Box with Glowing Border) */}
              <div
                style={{
                  top: `${hazardTopPct}%`,
                  height: `${hazardHeightPct}%`,
                }}
                className="absolute inset-x-0 bg-red-950/70 border-2 border-red-500/90 rounded px-2 flex items-center justify-between shadow-[0_0_15px_rgba(239,68,68,0.3)] z-10 animate-pulse"
              >
                <div className="flex items-center gap-1 text-[9.5px] font-bold text-red-200 font-mono">
                  <AlertTriangle className="w-3 h-3 text-red-400 flex-shrink-0" />
                  <span className="truncate">{HAZARD_HORIZON.name} ({HAZARD_HORIZON.lossRate})</span>
                </div>
                <span className="text-[8.5px] font-mono text-red-300 bg-red-900/60 px-1 py-0.5 rounded">
                  2,440–2,500m
                </span>
              </div>
            </div>

            <div className="text-[10px] font-mono text-slate-400 pt-1 border-t border-slate-800/80 flex items-center justify-between">
              <span>Historical NPT:</span>
              <span className="font-semibold text-red-400">42 hrs Loss Curing</span>
            </div>
          </div>

          {/* ========================================================================= */}
          {/* ACTIVE BIT HORIZONTAL LASER & CROSS-TRACK PROJECTION LINE                  */}
          {/* ========================================================================= */}
          <div
            className="absolute left-0 right-0 z-20 pointer-events-none transition-all duration-100 ease-linear flex items-center"
            style={{ top: `${bitProgressPct}%` }}
          >
            {/* Left Bit Marker & Depth Tag */}
            <div className="flex items-center gap-1 -translate-y-1/2 bg-cyan-500 text-slate-950 px-1.5 py-0.5 rounded shadow-lg shadow-cyan-500/50 text-[10px] font-mono font-bold border border-white">
              <Crosshair className="w-3 h-3 animate-spin-slow" />
              <span style={{ fontVariantNumeric: 'tabular-nums' }}>{currentMD.toFixed(1)}m</span>
            </div>

            {/* Real-time Dashed Laser Line Spanning across Track 1 and Track 2 */}
            <div className="flex-1 h-[2px] bg-cyan-400 shadow-[0_0_8px_#22d3ee] border-b border-dashed border-cyan-200" />

            {/* Right Projection Tag on Offset Track */}
            <div className="flex items-center gap-1 -translate-y-1/2 bg-slate-900/90 text-cyan-300 px-1.5 py-0.5 rounded border border-cyan-500/60 text-[9px] font-mono shadow-md">
              <span>Target Bit Horizon</span>
            </div>
          </div>
        </div>
      </div>

      {/* Stratigraphic Correlation Summary Footer */}
      <div className="text-[11px] text-slate-400 border-t border-slate-800/60 pt-2 font-mono flex items-center justify-between">
        <span className="flex items-center gap-1.5">
          <Activity className="w-3 h-3 text-cyan-400" />
          <span>{correlationLabel}: <strong className="text-emerald-400">94.2%</strong></span>
        </span>
        <span className="text-amber-400 font-semibold">Layer 3 Stratigraphy Active</span>
      </div>
    </div>
  );
};
