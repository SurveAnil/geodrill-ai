'use client';

import React from 'react';
import { AlertCircle, AlertTriangle, CheckCircle2, Clock } from 'lucide-react';
import { HistoricalEvent } from './types';

interface WellEventsProps {
  events: HistoricalEvent[];
  wellName: string;
}

export const WellEvents: React.FC<WellEventsProps> = ({ events, wellName }) => {
  if (!events || events.length === 0) {
    return (
      <div className="rounded-lg border border-slate-800 bg-slate-900/40 p-4 text-center">
        <CheckCircle2 className="mx-auto h-6 w-6 text-emerald-400" />
        <p className="mt-2 text-xs font-semibold text-slate-200">
          No Significant Operational NPT Events Logged
        </p>
        <p className="mt-1 text-[11px] text-slate-400">
          Drilling was executed within nominal window with zero documented well control incidents or stuck pipe.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-2.5">
      {events.map((ev) => {
        const isHigh = ev.severity === 'high';
        const isMed = ev.severity === 'medium';

        const borderColor = isHigh
          ? 'border-red-900/60 bg-red-950/20'
          : isMed
          ? 'border-amber-900/60 bg-amber-950/20'
          : 'border-emerald-900/50 bg-emerald-950/20';

        const badgeColor = isHigh
          ? 'border-red-700 bg-red-950 text-red-200'
          : isMed
          ? 'border-amber-700 bg-amber-950 text-amber-200'
          : 'border-emerald-700 bg-emerald-950 text-emerald-200';

        return (
          <div
            key={ev.id}
            className={`rounded-lg border p-3 transition-colors ${borderColor}`}
          >
            <div className="flex items-start justify-between gap-2">
              <div className="flex items-center gap-2">
                {isHigh ? (
                  <AlertCircle className="h-4 w-4 shrink-0 text-red-400" />
                ) : (
                  <AlertTriangle className="h-4 w-4 shrink-0 text-amber-400" />
                )}
                <span className="font-semibold text-xs text-white">
                  {ev.type}
                </span>
                <span className="font-mono text-[11px] text-cyan-300">
                  {ev.depthInterval}
                </span>
              </div>

              <div className="flex items-center gap-2">
                {ev.nptHours > 0 && (
                  <span className="flex items-center gap-1 font-mono text-[10px] text-slate-300">
                    <Clock className="h-3 w-3 text-slate-400" />
                    {ev.nptHours} hrs NPT
                  </span>
                )}
                <span
                  className={`rounded border px-1.5 py-0.5 font-mono text-[9px] font-bold uppercase ${badgeColor}`}
                >
                  {ev.severity}
                </span>
              </div>
            </div>

            <p className="mt-2 text-xs leading-relaxed text-slate-300">
              {ev.description}
            </p>
          </div>
        );
      })}
    </div>
  );
};
