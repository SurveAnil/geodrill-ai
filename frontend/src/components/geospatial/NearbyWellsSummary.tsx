'use client';

import React from 'react';
import { Target, Layers, AlertCircle, Compass, Radio } from 'lucide-react';

interface NearbyWellsSummaryProps {
  wellsFoundCount: number;
  relevantWellsCount: number;
  totalEventsCount: number;
  radiusKm: number;
  activeFormation: string;
}

export const NearbyWellsSummary: React.FC<NearbyWellsSummaryProps> = ({
  wellsFoundCount,
  relevantWellsCount,
  totalEventsCount,
  radiusKm,
  activeFormation,
}) => {
  return (
    <footer
      aria-label="Offset Wells Intelligence Summary"
      className="flex flex-wrap items-center justify-between gap-3 rounded-xl border border-slate-800 bg-[#0F172A]/90 px-4 py-2.5 shadow-md backdrop-blur-sm font-mono text-xs"
    >
      {/* Metric 1: Wells Found */}
      <div className="flex items-center gap-2">
        <Target className="h-4 w-4 text-cyan-400" />
        <span className="text-slate-400">Wells Found:</span>
        <span className="font-bold text-white text-sm">{wellsFoundCount}</span>
      </div>

      <div className="hidden h-4 w-px bg-slate-800 sm:block" />

      {/* Metric 2: Relevant Wells in Formation */}
      <div className="flex items-center gap-2">
        <Layers className="h-4 w-4 text-purple-400" />
        <span className="text-slate-400">Relevant in {activeFormation}:</span>
        <span className="font-bold text-purple-300 text-sm">{relevantWellsCount}</span>
      </div>

      <div className="hidden h-4 w-px bg-slate-800 sm:block" />

      {/* Metric 3: Historical NPT Events */}
      <div className="flex items-center gap-2">
        <AlertCircle className="h-4 w-4 text-amber-400" />
        <span className="text-slate-400">Historical Events:</span>
        <span className="font-bold text-amber-300 text-sm">{totalEventsCount}</span>
      </div>

      <div className="hidden h-4 w-px bg-slate-800 sm:block" />

      {/* Metric 4: Current Radius */}
      <div className="flex items-center gap-2">
        <Compass className="h-4 w-4 text-cyan-400" />
        <span className="text-slate-400">Search Radius:</span>
        <span className="font-bold text-cyan-300 text-sm">{radiusKm} km</span>
      </div>

      {/* Right status badge */}
      <div className="ml-auto hidden md:flex items-center gap-1.5 text-[11px] text-slate-500">
        <Radio className="h-3 w-3 text-emerald-400 animate-pulse" />
        <span>SPATIAL EVIDENCE SYNCHRONIZED</span>
      </div>
    </footer>
  );
};
