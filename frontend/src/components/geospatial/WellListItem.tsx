'use client';

import React from 'react';
import { AlertCircle, AlertTriangle, CheckCircle2, ChevronRight, Navigation } from 'lucide-react';
import { OffsetWellFeature } from './types';

interface WellListItemProps {
  well: OffsetWellFeature;
  isSelected: boolean;
  onSelect: (well: OffsetWellFeature) => void;
}

export const WellListItem: React.FC<WellListItemProps> = ({
  well,
  isSelected,
  onSelect,
}) => {
  const isHigh = well.riskLevel === 'high';
  const isMed = well.riskLevel === 'medium';

  const riskBadge = isHigh ? (
    <span className="flex items-center gap-1 rounded border border-red-700/80 bg-red-950/70 px-1.5 py-0.5 font-mono text-[9px] font-bold text-red-200">
      <AlertCircle className="h-2.5 w-2.5 text-red-400" />
      HIGH
    </span>
  ) : isMed ? (
    <span className="flex items-center gap-1 rounded border border-amber-700/80 bg-amber-950/70 px-1.5 py-0.5 font-mono text-[9px] font-bold text-amber-200">
      <AlertTriangle className="h-2.5 w-2.5 text-amber-400" />
      MED
    </span>
  ) : (
    <span className="flex items-center gap-1 rounded border border-emerald-700/80 bg-emerald-950/70 px-1.5 py-0.5 font-mono text-[9px] font-bold text-emerald-200">
      <CheckCircle2 className="h-2.5 w-2.5 text-emerald-400" />
      LOW
    </span>
  );

  return (
    <button
      onClick={() => onSelect(well)}
      className={`group w-full rounded-lg border p-2.5 text-left transition-all ${
        isSelected
          ? 'border-cyan-500 bg-cyan-950/30 shadow-[0_0_15px_-4px_rgba(6,182,212,0.4)]'
          : 'border-slate-800 bg-[#090D16] hover:border-slate-700 hover:bg-slate-800/40'
      }`}
    >
      <div className="flex items-start justify-between gap-2">
        <div className="flex items-center gap-2">
          <span className="font-mono text-xs font-bold text-white group-hover:text-cyan-300">
            {well.name}
          </span>
          {riskBadge}
        </div>

        <div className="flex items-center gap-1 font-mono text-[11px] font-semibold text-cyan-300">
          <Navigation className="h-2.5 w-2.5 rotate-45 text-cyan-400" />
          <span>{well.direction}</span>
        </div>
      </div>

      <div className="mt-1.5 flex items-center justify-between text-[11px] text-slate-400">
        <span className="truncate">{well.formation}</span>
        <span className="font-mono text-[10px] text-slate-500">TD {well.totalDepthM} m</span>
      </div>

      {well.hazardSummary && (
        <div className="mt-1.5 truncate rounded bg-slate-900/60 px-1.5 py-0.5 text-[10px] text-slate-300">
          ⚠️ {well.hazardSummary}
        </div>
      )}
    </button>
  );
};
