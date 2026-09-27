'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import {
  X,
  Compass,
  Layers,
  FileText,
  Activity,
  AlertTriangle,
  ArrowRight,
  Sparkles,
  ExternalLink,
  Milestone,
} from 'lucide-react';
import { OffsetWellFeature } from './types';
import { WellEvents } from './WellEvents';
import { WellLessons } from './WellLessons';

interface WellDetailPanelProps {
  well: OffsetWellFeature;
  onClose: () => void;
}

export const WellDetailPanel: React.FC<WellDetailPanelProps> = ({ well, onClose }) => {
  const [activeTab, setActiveTab] = useState<'overview' | 'events' | 'drilling' | 'documents'>('overview');

  const isHighRisk = well.riskLevel === 'high';
  const isMedRisk = well.riskLevel === 'medium';

  const riskBadgeClass = isHighRisk
    ? 'border-red-600/70 bg-red-950/80 text-red-200'
    : isMedRisk
    ? 'border-amber-600/70 bg-amber-950/80 text-amber-200'
    : 'border-emerald-600/70 bg-emerald-950/80 text-emerald-200';

  return (
    <div className="flex h-full min-h-0 flex-col overflow-hidden rounded-xl border border-slate-800 bg-[#0F172A] shadow-2xl">
      {/* Panel Header */}
      <div className="flex items-start justify-between border-b border-slate-800 bg-[#162032] p-4">
        <div>
          <div className="flex items-center gap-2">
            <span className="font-mono text-lg font-bold text-white tracking-tight">
              {well.name}
            </span>
            <span
              className={`rounded-full border px-2 py-0.5 font-mono text-[10px] font-bold uppercase tracking-wider ${riskBadgeClass}`}
            >
              {well.riskLevel} RISK
            </span>
          </div>
          <p className="mt-0.5 text-xs text-slate-400">
            Offset Well (Historical Reference) • {well.direction}
          </p>
        </div>

        <button
          onClick={onClose}
          aria-label="Close well details"
          className="rounded-lg border border-slate-700/80 p-1.5 text-slate-400 transition hover:bg-slate-800 hover:text-white"
        >
          <X className="h-4 w-4" />
        </button>
      </div>

      {/* Tabs Bar */}
      <div className="flex border-b border-slate-800 bg-[#0B1120] px-3">
        <button
          onClick={() => setActiveTab('overview')}
          className={`border-b-2 px-3 py-2 text-xs font-medium transition ${
            activeTab === 'overview'
              ? 'border-cyan-400 text-cyan-300'
              : 'border-transparent text-slate-400 hover:text-slate-200'
          }`}
        >
          Overview
        </button>

        <button
          onClick={() => setActiveTab('events')}
          className={`flex items-center gap-1.5 border-b-2 px-3 py-2 text-xs font-medium transition ${
            activeTab === 'events'
              ? 'border-cyan-400 text-cyan-300'
              : 'border-transparent text-slate-400 hover:text-slate-200'
          }`}
        >
          Events
          <span className="rounded-full bg-slate-800 px-1.5 py-0.2 font-mono text-[10px] text-slate-300">
            {well.historicalEvents.length}
          </span>
        </button>

        <button
          onClick={() => setActiveTab('drilling')}
          className={`border-b-2 px-3 py-2 text-xs font-medium transition ${
            activeTab === 'drilling'
              ? 'border-cyan-400 text-cyan-300'
              : 'border-transparent text-slate-400 hover:text-slate-200'
          }`}
        >
          Drilling Data
        </button>

        <button
          onClick={() => setActiveTab('documents')}
          className={`flex items-center gap-1.5 border-b-2 px-3 py-2 text-xs font-medium transition ${
            activeTab === 'documents'
              ? 'border-cyan-400 text-cyan-300'
              : 'border-transparent text-slate-400 hover:text-slate-200'
          }`}
        >
          Documents
          <span className="rounded-full bg-slate-800 px-1.5 py-0.2 font-mono text-[10px] text-slate-300">
            {well.historicalEvents.length > 0 ? 3 : 1}
          </span>
        </button>
      </div>

      {/* Panel Scrollable Body */}
      <div className="min-h-0 flex-1 overflow-y-auto p-4 space-y-4">
        {activeTab === 'overview' && (
          <>
            {/* Quick Metrics Grid */}
            <div className="grid grid-cols-2 gap-2 text-xs font-mono">
              <div className="rounded-lg border border-slate-800 bg-[#090D16] p-2.5">
                <span className="text-[10px] text-slate-400 uppercase">Distance & Bearing</span>
                <p className="font-bold text-cyan-300">{well.direction}</p>
              </div>

              <div className="rounded-lg border border-slate-800 bg-[#090D16] p-2.5">
                <span className="text-[10px] text-slate-400 uppercase">Total Depth (MD)</span>
                <p className="font-bold text-white">{well.totalDepthM.toLocaleString()} m</p>
              </div>

              <div className="rounded-lg border border-slate-800 bg-[#090D16] p-2.5">
                <span className="text-[10px] text-slate-400 uppercase">Spud Date</span>
                <p className="font-bold text-slate-200">{well.spudDate}</p>
              </div>

              <div className="rounded-lg border border-slate-800 bg-[#090D16] p-2.5">
                <span className="text-[10px] text-slate-400 uppercase">Completion</span>
                <p className="font-bold text-slate-200">{well.completionDate}</p>
              </div>

              <div className="rounded-lg border border-slate-800 bg-[#090D16] p-2.5">
                <span className="text-[10px] text-slate-400 uppercase">Well Status</span>
                <p className="font-bold text-emerald-400">{well.status}</p>
              </div>

              <div className="rounded-lg border border-slate-800 bg-[#090D16] p-2.5">
                <span className="text-[10px] text-slate-400 uppercase">Primary Formation</span>
                <p className="font-bold text-cyan-400">{well.formation}</p>
              </div>

              <div className="rounded-lg border border-slate-800 bg-[#090D16] p-2.5">
                <span className="text-[10px] text-slate-400 uppercase">Reservoir Target</span>
                <p className="font-bold text-slate-200">{well.reservoir}</p>
              </div>

              <div className="rounded-lg border border-slate-800 bg-[#090D16] p-2.5">
                <span className="text-[10px] text-slate-400 uppercase">Trajectory</span>
                <p className="font-bold text-purple-300">{well.trajectory}</p>
              </div>
            </div>

            {/* Representative Subsurface Trajectory Profile */}
            <div className="rounded-lg border border-slate-800 bg-[#090D16] p-3">
              <div className="flex items-center justify-between text-xs font-mono text-slate-400 mb-2">
                <span className="flex items-center gap-1.5 text-slate-300 font-semibold">
                  <Milestone className="h-3.5 w-3.5 text-cyan-400" />
                  Subsurface Trajectory Profile ({well.trajectory})
                </span>
                <span className="text-[10px] text-cyan-400">Surface to TD {well.totalDepthM} m</span>
              </div>

              <div className="relative h-20 w-full overflow-hidden rounded border border-slate-800/80 bg-slate-950/80 p-2">
                <svg className="h-full w-full" viewBox="0 0 300 60" preserveAspectRatio="none">
                  {/* Geological Strata Bands */}
                  <rect x="0" y="0" width="300" height="20" fill="#1e293b" opacity="0.3" />
                  <rect x="0" y="20" width="300" height="20" fill="#0f172a" opacity="0.4" />
                  <rect x="0" y="40" width="300" height="20" fill="#082f49" opacity="0.4" />

                  {/* Horizon Labels */}
                  <text x="5" y="14" fill="#64748b" fontSize="8" fontFamily="monospace">Harbour Shale</text>
                  <text x="5" y="34" fill="#64748b" fontSize="8" fontFamily="monospace">Northwind Sandstone</text>
                  <text x="5" y="54" fill="#64748b" fontSize="8" fontFamily="monospace">Reservoir Sand</text>

                  {/* Well Trajectory Curve */}
                  {well.trajectory === 'Vertical' ? (
                    <line x1="150" y1="5" x2="150" y2="55" stroke="#38bdf8" strokeWidth="2.5" strokeDasharray="none" />
                  ) : (
                    <path
                      d="M 100 5 Q 120 25, 200 45 T 260 55"
                      fill="none"
                      stroke="#38bdf8"
                      strokeWidth="2.5"
                    />
                  )}

                  {/* Surface Rig Icon Point */}
                  <circle cx={well.trajectory === 'Vertical' ? 150 : 100} cy="5" r="4" fill="#06b6d4" />
                  {/* Total Depth Target Point */}
                  <circle cx={well.trajectory === 'Vertical' ? 150 : 260} cy="55" r="4" fill={isHighRisk ? '#ef4444' : '#10b981'} />
                </svg>
              </div>
              <div className="mt-1.5 flex justify-between font-mono text-[9px] text-slate-500">
                <span>RKB Surface: 0 m MD</span>
                <span>Kick-off: ~1,850 m</span>
                <span>TD: {well.totalDepthM} m MD</span>
              </div>
            </div>

            {/* Lessons Learned Card */}
            <WellLessons lessons={well.lessonsLearned} wellName={well.name} />
          </>
        )}

        {activeTab === 'events' && (
          <div className="space-y-3">
            <div className="flex items-center justify-between text-xs text-slate-400">
              <span>Documented drilling events and NPT logs</span>
              <span className="font-mono text-cyan-300 font-semibold">{well.nptHours} Total NPT hrs</span>
            </div>
            <WellEvents events={well.historicalEvents} wellName={well.name} />
          </div>
        )}

        {activeTab === 'drilling' && (
          <div className="space-y-3 text-xs">
            <div className="rounded-lg border border-slate-800 bg-[#090D16] p-3 space-y-2">
              <h4 className="font-semibold text-white">Historical Mud Program Summary</h4>
              <div className="grid grid-cols-2 gap-2 text-slate-300 font-mono text-[11px]">
                <div>• Interval Mud Wt: 1.38 – 1.48 SG</div>
                <div>• Mud System: KCL Polymer / Glycol</div>
                <div>• Flow Rate: 680 – 760 GPM</div>
                <div>• Standpipe Avg: 3,150 PSI</div>
              </div>
            </div>

            <div className="rounded-lg border border-slate-800 bg-[#090D16] p-3 space-y-2">
              <h4 className="font-semibold text-white">BHA & Bit Configuration</h4>
              <p className="text-slate-400 leading-relaxed text-[11px]">
                8-1/2&quot; PDC Bit (5 blades, 16mm cutters) with rotary steerable system (RSS), MWD/LWD dual telemetry and energized hydraulic drilling jars spaced at 120m above bit.
              </p>
            </div>
          </div>
        )}

        {activeTab === 'documents' && (
          <div className="space-y-2.5">
            <div className="flex items-center justify-between rounded-lg border border-slate-800 bg-[#090D16] p-3 transition hover:border-slate-700">
              <div className="flex items-center gap-2.5">
                <FileText className="h-5 w-5 text-cyan-400" />
                <div>
                  <p className="font-medium text-xs text-white">End of Well Report (WCR)</p>
                  <p className="text-[10px] text-slate-400 font-mono">{well.name}_WCR_Final.pdf • 14.8 MB</p>
                </div>
              </div>
              <span className="rounded bg-slate-800 px-2 py-0.5 text-[10px] text-cyan-300 font-mono">
                Indexed in RAG
              </span>
            </div>

            <div className="flex items-center justify-between rounded-lg border border-slate-800 bg-[#090D16] p-3 transition hover:border-slate-700">
              <div className="flex items-center gap-2.5">
                <FileText className="h-5 w-5 text-purple-400" />
                <div>
                  <p className="font-medium text-xs text-white">Composite Mud & Lithology Log</p>
                  <p className="text-[10px] text-slate-400 font-mono">{well.name}_MasterLog.las • 4.2 MB</p>
                </div>
              </div>
              <span className="rounded bg-slate-800 px-2 py-0.5 text-[10px] text-slate-400 font-mono">
                Available
              </span>
            </div>
          </div>
        )}
      </div>

      {/* Bottom Action Footer with Real Routing */}
      <div className="border-t border-slate-800 bg-[#162032] p-3 space-y-2">
        <div className="grid grid-cols-2 gap-2">
          <Link
            href="/stratigraphy"
            className="flex items-center justify-center gap-1.5 rounded-lg border border-cyan-700/60 bg-cyan-950/40 px-3 py-2 text-xs font-semibold text-cyan-200 transition hover:bg-cyan-900/60"
          >
            <Layers className="h-3.5 w-3.5 text-cyan-400" />
            View in Stratigraphy
          </Link>

          <Link
            href={`/lessons?well=${encodeURIComponent(well.wellId)}`}
            className="flex items-center justify-center gap-1.5 rounded-lg border border-amber-700/60 bg-amber-950/40 px-3 py-2 text-xs font-semibold text-amber-200 transition hover:bg-amber-900/60"
          >
            <AlertTriangle className="h-3.5 w-3.5 text-amber-400" />
            Open in Lessons
          </Link>
        </div>

        <Link
          href={`/ai?prompt=${encodeURIComponent(
            `What historical drilling hazards and mud weight recommendations are documented for ${well.wellId}?`
          )}`}
          className="flex w-full items-center justify-center gap-2 rounded-lg border border-purple-600/70 bg-purple-950/40 px-3 py-2 text-xs font-semibold text-purple-200 transition hover:bg-purple-900/60 shadow-sm"
        >
          <Sparkles className="h-3.5 w-3.5 text-purple-400" />
          Ask AI Copilot About {well.wellId}
          <ArrowRight className="h-3.5 w-3.5" />
        </Link>
      </div>
    </div>
  );
};
