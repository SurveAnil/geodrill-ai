'use client';

import React from 'react';
import { useDrillStore } from '@/store/useDrillStore';
import { ShieldAlert, Activity, MapPin, Bot, Database, Layers, History } from 'lucide-react';

interface DashboardGridProps {
  heroSlot?: React.ReactNode;
  leftSlot?: React.ReactNode;
  centerSlot?: React.ReactNode;
  rightSlot?: React.ReactNode;
  bottomLeftSlot?: React.ReactNode;
  bottomRightSlot?: React.ReactNode;
}

export const DashboardGrid: React.FC<DashboardGridProps> = ({
  heroSlot,
  leftSlot,
  centerSlot,
  rightSlot,
  bottomLeftSlot,
  bottomRightSlot,
}) => {
  const { risk, telemetry } = useDrillStore();

  return (
    <div className="flex-1 w-full max-w-[1920px] mx-auto p-3.5 space-y-3.5 flex flex-col">
      {/* Top Section: Phase 2 Hero Slot (1-2-3 Triage Cards) */}
      <section id="hero-triage-section" className="w-full">
        {heroSlot || (
          <div className="w-full bg-[#0F172A] border border-slate-800 rounded-xl p-4 flex items-center justify-between shadow-lg">
            <div className="flex items-center gap-3">
              <div className="p-2.5 rounded-lg bg-cyan-950/60 border border-cyan-800/60 text-cyan-400">
                <ShieldAlert className="w-5 h-5" />
              </div>
              <div>
                <h2 className="text-sm font-semibold text-white tracking-wide flex items-center gap-2">
                  Layer 5: 1-2-3 Predictive Triage Hero
                </h2>
                <p className="text-xs text-slate-400">
                  Current Simulation Depth: <span className="font-mono text-cyan-300 font-semibold">{telemetry.measuredDepthM.toFixed(1)}m MD</span> • Formation: <span className="text-amber-300 font-medium">{telemetry.currentFormation}</span>
                </p>
              </div>
            </div>
            <div className="text-right">
              <span className="text-xs text-slate-400">Risk Assessment: </span>
              <span className="text-xs font-mono font-bold uppercase px-2 py-0.5 rounded bg-amber-950/80 text-amber-300 border border-amber-800">
                {risk.riskLevel} (Score {risk.riskScore}/100)
              </span>
            </div>
          </div>
        )}
      </section>

      {/* Main 3-Column Operations Layout */}
      <main className="grid grid-cols-1 lg:grid-cols-12 gap-3.5 min-h-[580px]">
        {/* Left Column: Geospatial & Radar (Phase 4) */}
        <section
          id="left-gis-column"
          className="lg:col-span-3 bg-[#0F172A]/80 border border-slate-800/90 rounded-xl p-4 flex flex-col justify-between shadow-md"
        >
          {leftSlot || (
            <div className="flex flex-col h-full justify-between text-xs text-slate-500">
              <span>Geospatial Radar</span>
            </div>
          )}
        </section>

        {/* Center Column: AI Panels (Layer 1 & 2 - Phase 5) */}
        <section
          id="center-ai-column"
          className="lg:col-span-5 bg-[#0F172A]/80 border border-slate-800/90 rounded-xl p-4 flex flex-col justify-between shadow-md"
        >
          {centerSlot || (
            <div className="flex flex-col h-full justify-between text-xs text-slate-500">
              <span>AI Copilot & Document Intelligence</span>
            </div>
          )}
        </section>

        {/* Right Column: Live Telemetry & Timeline (Layer 3 & 4 - Phase 3) */}
        <section
          id="right-telemetry-column"
          className="lg:col-span-4 bg-[#0F172A]/80 border border-slate-800/90 rounded-xl p-4 flex flex-col justify-between shadow-md"
        >
          {rightSlot || (
            <div className="flex flex-col h-full justify-between text-xs text-slate-500">
              <span>10Hz Live Telemetry</span>
            </div>
          )}
        </section>
      </main>

      {/* Bottom Section: 2-Column Grid for Phase 6 (Stratigraphy) and Phase 7 (Lessons Learned) */}
      <section id="bottom-correlation-section" className="grid grid-cols-1 lg:grid-cols-12 gap-3.5 min-h-[380px]">
        {/* Bottom Left: Stratigraphic Depth Cross-Correlation (Layer 3 - Phase 6) */}
        <div className="lg:col-span-6 bg-[#0F172A]/80 border border-slate-800/90 rounded-xl p-4 flex flex-col shadow-md">
          {bottomLeftSlot || (
            <div className="flex flex-col h-full justify-between">
              <div className="flex items-center justify-between pb-3 border-b border-slate-800">
                <div className="flex items-center gap-2 text-xs font-semibold text-slate-200">
                  <Layers className="w-4 h-4 text-amber-400" />
                  <span>Stratigraphic Depth Cross-Correlation</span>
                </div>
                <span className="text-[10px] font-mono text-slate-500 uppercase">Phase 6</span>
              </div>
              <div className="h-44 rounded-lg border border-dashed border-slate-800 bg-[#0A101D] flex items-center justify-center text-xs text-slate-500 mt-4">
                Vertical Track Chart & Hazard Horizon Overlay
              </div>
              <div className="text-[11px] text-slate-500 border-t border-slate-800/60 pt-2 font-mono mt-3">
                Layer 3 Stratigraphic Correlation
              </div>
            </div>
          )}
        </div>

        {/* Bottom Right: Lessons Learned Repository (Phase 7) */}
        <div className="lg:col-span-6 bg-[#0F172A]/80 border border-slate-800/90 rounded-xl p-4 flex flex-col shadow-md">
          {bottomRightSlot || (
            <div className="flex flex-col h-full justify-between">
              <div className="flex items-center justify-between pb-3 border-b border-slate-800">
                <div className="flex items-center gap-2 text-xs font-semibold text-slate-200">
                  <History className="w-4 h-4 text-cyan-400" />
                  <span>Historical Lessons Learned Repository</span>
                </div>
                <span className="text-[10px] font-mono text-slate-500 uppercase">Phase 7</span>
              </div>
              <div className="h-44 rounded-lg border border-dashed border-slate-800 bg-[#0A101D] flex items-center justify-center text-xs text-slate-500 mt-4">
                Structured Incident Timeline & Remediation Log
              </div>
              <div className="text-[11px] text-slate-500 border-t border-slate-800/60 pt-2 font-mono mt-3">
                Traceable Incident Knowledge Store
              </div>
            </div>
          )}
        </div>
      </section>
    </div>
  );
};
