'use client';

import React, { useRef, useEffect } from 'react';
import {
  TrendingUp,
  TrendingDown,
  Minus,
  Weight,
  RotateCw,
  Droplets,
  Gauge as GaugeIcon,
  Waves,
  Beaker,
} from 'lucide-react';
import { useDrillStore } from '@/store/useDrillStore';

/* ------------------------------------------------------------------ */
/*  Gauge definition                                                    */
/* ------------------------------------------------------------------ */
interface GaugeDef {
  key: string;
  label: string;
  unit: string;
  icon: React.ReactNode;
  color: string;        // text color for the value
  accentBg: string;     // icon container bg
  accentBorder: string; // icon container border
  warningHigh?: number; // above this → amber flash
  criticalHigh?: number;// above this → red flash
  getValue: (t: ReturnType<typeof useDrillStore.getState>['telemetry']) => number;
  format: (v: number) => string;
}

const GAUGES: GaugeDef[] = [
  {
    key: 'rop',
    label: 'ROP',
    unit: 'm/hr',
    icon: <TrendingUp className="w-3.5 h-3.5" />,
    color: 'text-emerald-400',
    accentBg: 'bg-emerald-950/60',
    accentBorder: 'border-emerald-800/50',
    warningHigh: 35,
    criticalHigh: 50,
    getValue: (t) => t.rop,
    format: (v) => v.toFixed(1),
  },
  {
    key: 'wob',
    label: 'WOB',
    unit: 'klbs',
    icon: <Weight className="w-3.5 h-3.5" />,
    color: 'text-cyan-400',
    accentBg: 'bg-cyan-950/60',
    accentBorder: 'border-cyan-800/50',
    warningHigh: 35,
    criticalHigh: 45,
    getValue: (t) => t.wob,
    format: (v) => v.toFixed(1),
  },
  {
    key: 'torque',
    label: 'Torque',
    unit: 'kft-lb',
    icon: <RotateCw className="w-3.5 h-3.5" />,
    color: 'text-amber-400',
    accentBg: 'bg-amber-950/60',
    accentBorder: 'border-amber-800/50',
    warningHigh: 22,
    criticalHigh: 30,
    getValue: (t) => t.torque,
    format: (v) => v.toFixed(1),
  },
  {
    key: 'flowRate',
    label: 'Flow Rate',
    unit: 'gpm',
    icon: <Droplets className="w-3.5 h-3.5" />,
    color: 'text-blue-400',
    accentBg: 'bg-blue-950/60',
    accentBorder: 'border-blue-800/50',
    warningHigh: 850,
    criticalHigh: 1000,
    getValue: (t) => t.flowRate,
    format: (v) => v.toFixed(0),
  },
  {
    key: 'spp',
    label: 'SPP',
    unit: 'psi',
    icon: <GaugeIcon className="w-3.5 h-3.5" />,
    color: 'text-purple-400',
    accentBg: 'bg-purple-950/60',
    accentBorder: 'border-purple-800/50',
    warningHigh: 3800,
    criticalHigh: 4200,
    getValue: (t) => t.standpipePressure,
    format: (v) => v.toFixed(0),
  },
  {
    key: 'mudWeight',
    label: 'Mud Wt',
    unit: 'SG',
    icon: <Beaker className="w-3.5 h-3.5" />,
    color: 'text-teal-400',
    accentBg: 'bg-teal-950/60',
    accentBorder: 'border-teal-800/50',
    warningHigh: 1.55,
    criticalHigh: 1.65,
    getValue: (t) => t.mudWeightSg,
    format: (v) => v.toFixed(2),
  },
];

/* ------------------------------------------------------------------ */
/*  Trend arrow logic (compares current value to previous)             */
/* ------------------------------------------------------------------ */
type Trend = 'up' | 'down' | 'flat';

const TrendIcon: React.FC<{ trend: Trend }> = ({ trend }) => {
  if (trend === 'up')
    return <TrendingUp className="w-3 h-3 text-emerald-400" />;
  if (trend === 'down')
    return <TrendingDown className="w-3 h-3 text-red-400" />;
  return <Minus className="w-3 h-3 text-slate-600" />;
};

/* ------------------------------------------------------------------ */
/*  Single Gauge Cell                                                   */
/* ------------------------------------------------------------------ */
const GaugeCell: React.FC<{
  def: GaugeDef;
  value: number;
  trend: Trend;
}> = React.memo(({ def, value, trend }) => {
  const isWarning =
    def.warningHigh !== undefined && value >= def.warningHigh && (def.criticalHigh === undefined || value < def.criticalHigh);
  const isCritical =
    def.criticalHigh !== undefined && value >= def.criticalHigh;

  return (
    <div
      className={`p-2.5 rounded-lg border transition-colors duration-300 ${
        isCritical
          ? 'bg-red-950/30 border-red-700/50'
          : isWarning
          ? 'bg-amber-950/20 border-amber-700/40'
          : 'bg-[#0A101D] border-slate-800/80'
      }`}
    >
      <div className="flex items-center justify-between mb-1.5">
        <div className="flex items-center gap-1.5">
          <div className={`p-1 rounded ${def.accentBg} border ${def.accentBorder}`}>
            {def.icon}
          </div>
          <span className="text-[10px] font-mono text-slate-500 uppercase tracking-wide">
            {def.label}
          </span>
        </div>
        <TrendIcon trend={trend} />
      </div>
      <div
        className={`font-mono font-bold text-lg leading-none ${
          isCritical ? 'text-red-400' : isWarning ? 'text-amber-400' : def.color
        }`}
        style={{ fontVariantNumeric: 'tabular-nums' }}
      >
        {def.format(value)}
        <span className="text-[10px] text-slate-500 font-normal ml-1">{def.unit}</span>
      </div>
    </div>
  );
});

GaugeCell.displayName = 'GaugeCell';

/* ================================================================== */
/*  TELEMETRY GAUGES — main export                                     */
/* ================================================================== */
export const TelemetryGauges: React.FC = () => {
  const telemetry = useDrillStore((s) => s.telemetry);

  // Track previous values for trend arrows using a ref to avoid re-renders
  const prevRef = useRef<Record<string, number>>({});

  const trends: Record<string, Trend> = {};
  for (const g of GAUGES) {
    const cur = g.getValue(telemetry);
    const prev = prevRef.current[g.key];
    if (prev === undefined) {
      trends[g.key] = 'flat';
    } else {
      const delta = cur - prev;
      const threshold = Math.max(Math.abs(prev) * 0.005, 0.05); // 0.5% or 0.05 absolute
      trends[g.key] = delta > threshold ? 'up' : delta < -threshold ? 'down' : 'flat';
    }
  }

  // Update prev values after computing trends
  useEffect(() => {
    const next: Record<string, number> = {};
    for (const g of GAUGES) {
      next[g.key] = g.getValue(telemetry);
    }
    prevRef.current = next;
  });

  return (
    <div className="grid grid-cols-3 gap-2">
      {GAUGES.map((g) => (
        <GaugeCell
          key={g.key}
          def={g}
          value={g.getValue(telemetry)}
          trend={trends[g.key] || 'flat'}
        />
      ))}
    </div>
  );
};
