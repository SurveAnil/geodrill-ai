'use client';

import React from 'react';
import { Activity, TrendingUp } from 'lucide-react';
import { useDrillStore } from '@/store/useDrillStore';
import { TelemetryGauges } from './TelemetryGauges';
import { TelemetryChart } from './TelemetryChart';

export const TelemetryPanel: React.FC = () => {
  const isStreaming = useDrillStore((s) => s.isStreaming10Hz);
  const tickCount = useDrillStore((s) => s.simulationTickCount);

  return (
    <div className="flex flex-col h-full gap-3">
      {/* Panel Header */}
      <div className="flex items-center justify-between pb-2.5 border-b border-slate-800">
        <div className="flex items-center gap-2 text-xs font-semibold text-slate-200">
          <Activity className="w-4 h-4 text-emerald-400" />
          <span>10Hz Live Telemetry</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-[10px] font-mono text-slate-500">
            Ticks: <span className="text-slate-400" style={{ fontVariantNumeric: 'tabular-nums' }}>{tickCount}</span>
          </span>
          <span
            className={`flex items-center gap-1.5 px-2 py-0.5 rounded-full border text-[10px] font-mono font-semibold ${
              isStreaming
                ? 'bg-emerald-950/40 text-emerald-300 border-emerald-800/60'
                : 'bg-slate-900 text-slate-500 border-slate-800'
            }`}
          >
            <span className="relative flex h-1.5 w-1.5">
              {isStreaming && (
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75" />
              )}
              <span
                className={`relative inline-flex rounded-full h-1.5 w-1.5 ${
                  isStreaming ? 'bg-emerald-400' : 'bg-slate-600'
                }`}
              />
            </span>
            {isStreaming ? 'STREAMING' : 'PAUSED'}
          </span>
        </div>
      </div>

      {/* Gauges Section */}
      <TelemetryGauges />

      {/* Chart Section */}
      <div className="flex-1 min-h-0 flex flex-col">
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center gap-1.5 text-[11px] text-slate-400">
            <TrendingUp className="w-3.5 h-3.5 text-purple-400" />
            <span className="font-medium">SPP & ROP Trace</span>
          </div>
          <div className="flex items-center gap-3 text-[10px] font-mono text-slate-600">
            <span className="flex items-center gap-1">
              <span className="w-2 h-[2px] bg-emerald-500 rounded" />
              Safe Window
            </span>
            <span className="flex items-center gap-1">
              <span className="w-2 h-[2px] bg-red-500 rounded" />
              Frac Limit
            </span>
          </div>
        </div>
        <div className="flex-1 min-h-[220px] rounded-lg bg-[#0A101D] border border-slate-800/60 p-2">
          <TelemetryChart />
        </div>
      </div>

      {/* Footer */}
      <div className="text-[11px] text-slate-500 border-t border-slate-800/60 pt-2 font-mono flex items-center justify-between">
        <span>Buffer: 100 pts @ 3.3 Hz</span>
        <span className="text-emerald-400 font-semibold">Layer 4 Active</span>
      </div>
    </div>
  );
};
