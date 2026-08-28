'use client';

import React from 'react';
import { AlertCircle, AlertTriangle, CheckCircle2, Navigation } from 'lucide-react';

export interface OffsetWellItem {
  id: string;
  name: string;
  distanceKm: number;
  hazard: string;
  status: 'critical' | 'warning' | 'safe';
  lat: number;
  lon: number;
}

export const OFFSET_WELLS: OffsetWellItem[] = [
  {
    id: 'w-1',
    name: 'ONGC-KG-07-ALOK',
    distanceKm: 2.4,
    hazard: 'Severe Mud Loss (65 bbl/hr @ 2450m)',
    status: 'critical',
    lat: 16.262,
    lon: 82.368,
  },
  {
    id: 'w-2',
    name: 'ONGC-KG-12-BRAVO',
    distanceKm: 5.1,
    hazard: 'Gas Kick / Influx (12 bbl @ 2510m)',
    status: 'warning',
    lat: 16.221,
    lon: 82.385,
  },
  {
    id: 'w-3',
    name: 'ONGC-KG-04-DELTA',
    distanceKm: 8.3,
    hazard: 'Normal Drilling (No Major Loss)',
    status: 'safe',
    lat: 16.295,
    lon: 82.312,
  },
];

const STATUS_CONFIG = {
  critical: {
    bg: 'bg-red-950/20 hover:bg-red-950/30',
    border: 'border-red-900/40',
    badge: 'bg-red-950 text-red-300 border-red-800/80',
    icon: <AlertCircle className="w-3.5 h-3.5 text-red-400" />,
    label: 'Critical',
    dot: 'bg-red-500',
  },
  warning: {
    bg: 'bg-amber-950/20 hover:bg-amber-950/30',
    border: 'border-amber-900/40',
    badge: 'bg-amber-950 text-amber-300 border-amber-800/80',
    icon: <AlertTriangle className="w-3.5 h-3.5 text-amber-400" />,
    label: 'Warning',
    dot: 'bg-amber-500',
  },
  safe: {
    bg: 'bg-emerald-950/20 hover:bg-emerald-950/30',
    border: 'border-emerald-900/40',
    badge: 'bg-emerald-950 text-emerald-300 border-emerald-800/80',
    icon: <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />,
    label: 'Safe',
    dot: 'bg-emerald-500',
  },
};

interface OffsetRadarTableProps {
  onSelectWell?: (well: OffsetWellItem) => void;
  selectedWellId?: string;
  wells?: OffsetWellItem[];
}

export const OffsetRadarTable: React.FC<OffsetRadarTableProps> = ({
  onSelectWell,
  selectedWellId,
  wells = OFFSET_WELLS,
}) => {
  return (
    <div className="w-full flex flex-col">
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center gap-1.5 text-xs font-semibold text-slate-300">
          <Navigation className="w-3.5 h-3.5 text-cyan-400" />
          <span>Offset Wells Radar (10 km Radius)</span>
        </div>
        <span className="text-[10px] font-mono text-slate-500">{wells.length} Wells In Range</span>
      </div>

      <div className="w-full overflow-hidden rounded-lg border border-slate-800/80 bg-[#0A101D]">
        <table className="w-full text-left text-xs border-collapse">
          <thead>
            <tr className="border-b border-slate-800 bg-[#0F172A]/80 text-[10px] uppercase font-mono text-slate-400">
              <th className="py-2 px-2.5 font-medium">Well Name</th>
              <th className="py-2 px-2 font-medium text-right">Dist</th>
              <th className="py-2 px-2.5 font-medium">Historical Hazard</th>
              <th className="py-2 px-2 font-medium text-center">Status</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/60 font-sans">
            {wells.map((well) => {
              const cfg = STATUS_CONFIG[well.status];
              const isSelected = selectedWellId === well.id;
              return (
                <tr
                  key={well.id}
                  onClick={() => onSelectWell?.(well)}
                  className={`transition-colors cursor-pointer ${cfg.bg} ${
                    isSelected ? 'ring-1 ring-cyan-500 bg-cyan-950/30' : ''
                  }`}
                >
                  <td className="py-2 px-2.5">
                    <div className="flex items-center gap-1.5">
                      <span className={`h-1.5 w-1.5 rounded-full ${cfg.dot}`} />
                      <span className="font-semibold text-slate-200 text-xs font-mono">
                        {well.name}
                      </span>
                    </div>
                  </td>
                  <td
                    className="py-2 px-2 text-right font-mono font-semibold text-cyan-300 text-xs"
                    style={{ fontVariantNumeric: 'tabular-nums' }}
                  >
                    {well.distanceKm.toFixed(1)}
                    <span className="text-[10px] text-slate-500 font-normal ml-0.5">km</span>
                  </td>
                  <td className="py-2 px-2.5 text-slate-300 text-[11px] max-w-[140px] truncate" title={well.hazard}>
                    {well.hazard}
                  </td>
                  <td className="py-2 px-2 text-center">
                    <span
                      className={`inline-flex items-center gap-1 px-1.5 py-0.5 rounded text-[9px] font-mono uppercase font-bold border ${cfg.badge}`}
                    >
                      {cfg.icon}
                      {cfg.label}
                    </span>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
};
