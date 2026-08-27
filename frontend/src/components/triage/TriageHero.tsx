'use client';

import React from 'react';
import {
  Crosshair,
  AlertTriangle,
  ShieldAlert,
  Layers,
  ArrowDown,
  Gauge,
  BookOpen,
  Siren,
} from 'lucide-react';
import { useDrillStore, RiskLevel } from '@/store/useDrillStore';

/* ------------------------------------------------------------------ */
/*  Risk-level → visual theme mapping                                  */
/* ------------------------------------------------------------------ */
const RISK_THEMES: Record<
  RiskLevel,
  {
    cardBg: string;
    border: string;
    glow: string;
    badge: string;
    badgeText: string;
    scoreColor: string;
    iconColor: string;
    pulseClass: string;
  }
> = {
  low: {
    cardBg: 'bg-emerald-950/20',
    border: 'border-emerald-800/40',
    glow: '',
    badge: 'bg-emerald-950 border-emerald-700/60',
    badgeText: 'text-emerald-300',
    scoreColor: 'text-emerald-400',
    iconColor: 'text-emerald-400',
    pulseClass: '',
  },
  medium: {
    cardBg: 'bg-amber-950/20',
    border: 'border-amber-700/50',
    glow: '',
    badge: 'bg-amber-950 border-amber-700/60',
    badgeText: 'text-amber-300',
    scoreColor: 'text-amber-400',
    iconColor: 'text-amber-400',
    pulseClass: '',
  },
  high: {
    cardBg: 'bg-orange-950/25',
    border: 'border-orange-600/50',
    glow: 'shadow-[0_0_15px_-3px_rgba(249,115,22,0.15)]',
    badge: 'bg-orange-950 border-orange-600/60',
    badgeText: 'text-orange-300',
    scoreColor: 'text-orange-400',
    iconColor: 'text-orange-400',
    pulseClass: '',
  },
  critical: {
    cardBg: 'bg-red-950/30',
    border: 'border-red-600/60',
    glow: 'shadow-[0_0_24px_-3px_rgba(239,68,68,0.25)]',
    badge: 'bg-red-950 border-red-500/70',
    badgeText: 'text-red-300',
    scoreColor: 'text-red-400',
    iconColor: 'text-red-400',
    pulseClass: 'animate-pulse',
  },
};

const RISK_LABEL: Record<RiskLevel, string> = {
  low: 'LOW',
  medium: 'ELEVATED',
  high: 'HIGH',
  critical: 'CRITICAL',
};

const RISK_EMOJI: Record<RiskLevel, string> = {
  low: '🟢',
  medium: '🟡',
  high: '🟠',
  critical: '🔴',
};

/* ------------------------------------------------------------------ */
/*  Utility: tabular-number formatting                                 */
/* ------------------------------------------------------------------ */
const TabNum: React.FC<{ value: string; unit?: string; className?: string }> = ({
  value,
  unit,
  className = '',
}) => (
  <span className={className} style={{ fontVariantNumeric: 'tabular-nums' }}>
    {value}
    {unit && (
      <span className="text-[11px] text-slate-500 font-normal ml-0.5">{unit}</span>
    )}
  </span>
);

/* ------------------------------------------------------------------ */
/*  Score Arc: a compact radial gauge for 0–100 risk score             */
/* ------------------------------------------------------------------ */
const ScoreArc: React.FC<{ score: number; color: string }> = ({ score, color }) => {
  const radius = 26;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (score / 100) * circumference;

  return (
    <div className="relative w-16 h-16 flex-shrink-0">
      <svg viewBox="0 0 64 64" className="w-full h-full -rotate-90">
        <circle
          cx="32"
          cy="32"
          r={radius}
          fill="none"
          stroke="currentColor"
          strokeWidth="5"
          className="text-slate-800"
        />
        <circle
          cx="32"
          cy="32"
          r={radius}
          fill="none"
          stroke="currentColor"
          strokeWidth="5"
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          className={color}
          style={{ transition: 'stroke-dashoffset 0.6s ease' }}
        />
      </svg>
      <span
        className={`absolute inset-0 flex items-center justify-center font-mono font-bold text-sm ${color}`}
        style={{ fontVariantNumeric: 'tabular-nums' }}
      >
        {score}
      </span>
    </div>
  );
};

/* ================================================================== */
/*  TRIAGE HERO — main export                                          */
/* ================================================================== */
export const TriageHero: React.FC = () => {
  const { telemetry, risk } = useDrillStore();
  const theme = RISK_THEMES[risk.riskLevel];
  const isCritical = risk.riskLevel === 'critical';

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-3">
      {/* ============================================================ */}
      {/*  CARD 1 — Current Drill Bit Position                         */}
      {/* ============================================================ */}
      <div className="relative bg-slate-800/50 border border-slate-700/80 rounded-xl p-4 shadow-md overflow-hidden">
        {/* Subtle left-edge accent */}
        <div className="absolute left-0 top-0 bottom-0 w-[3px] rounded-l-xl bg-gradient-to-b from-cyan-500 to-cyan-700" />

        <div className="flex items-start justify-between mb-3">
          <div className="flex items-center gap-2">
            <div className="p-1.5 rounded-md bg-cyan-950/60 border border-cyan-800/50">
              <Crosshair className="w-4 h-4 text-cyan-400" />
            </div>
            <div>
              <h3 className="text-[11px] font-semibold uppercase tracking-wider text-slate-400">
                Drill Bit Position
              </h3>
              <span className="text-[10px] text-slate-500 font-mono">CARD 1 of 3</span>
            </div>
          </div>
          <span className="flex items-center gap-1.5 px-2 py-0.5 rounded-full bg-emerald-950/60 border border-emerald-800/50 text-[10px] font-semibold text-emerald-300">
            <span className="relative flex h-1.5 w-1.5">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75" />
              <span className="relative inline-flex rounded-full h-1.5 w-1.5 bg-emerald-400" />
            </span>
            DRILLING ACTIVE
          </span>
        </div>

        {/* Primary depth readouts */}
        <div className="grid grid-cols-2 gap-x-4 gap-y-2 mb-3">
          <div>
            <span className="text-[10px] font-mono text-slate-500 uppercase">Measured Depth</span>
            <div className="font-mono font-bold text-xl text-white leading-tight">
              <TabNum value={telemetry.measuredDepthM.toFixed(1)} unit="m MD" />
            </div>
          </div>
          <div>
            <span className="text-[10px] font-mono text-slate-500 uppercase">True Vertical</span>
            <div className="font-mono font-bold text-xl text-slate-200 leading-tight">
              <TabNum value={telemetry.trueVerticalDepthM.toFixed(1)} unit="m TVD" />
            </div>
          </div>
        </div>

        {/* Formation & ROP sub-strip */}
        <div className="flex items-center justify-between pt-2.5 border-t border-slate-700/60">
          <div className="flex items-center gap-1.5 text-xs">
            <Layers className="w-3.5 h-3.5 text-amber-400" />
            <span className="text-slate-400">Formation:</span>
            <span className="font-semibold text-amber-300">{telemetry.currentFormation}</span>
          </div>
          <div className="flex items-center gap-1.5 text-xs">
            <Gauge className="w-3.5 h-3.5 text-emerald-400" />
            <span className="text-slate-400">ROP:</span>
            <span className="font-mono font-semibold text-emerald-300">
              <TabNum value={telemetry.rop.toFixed(1)} unit="m/hr" />
            </span>
          </div>
        </div>
      </div>

      {/* ============================================================ */}
      {/*  CARD 2 — Hazard Predicted Ahead                             */}
      {/* ============================================================ */}
      <div
        className={`relative rounded-xl p-4 shadow-md overflow-hidden transition-all duration-500 ${theme.cardBg} border ${theme.border} ${theme.glow} ${theme.pulseClass}`}
      >
        {/* Risk-colored left accent bar */}
        <div
          className={`absolute left-0 top-0 bottom-0 w-[3px] rounded-l-xl ${
            risk.riskLevel === 'low'
              ? 'bg-gradient-to-b from-emerald-500 to-emerald-700'
              : risk.riskLevel === 'medium'
              ? 'bg-gradient-to-b from-amber-500 to-amber-700'
              : risk.riskLevel === 'high'
              ? 'bg-gradient-to-b from-orange-500 to-orange-700'
              : 'bg-gradient-to-b from-red-500 to-red-700'
          }`}
        />

        <div className="flex items-start justify-between mb-2.5">
          <div className="flex items-center gap-2">
            <div className={`p-1.5 rounded-md border ${theme.badge}`}>
              <AlertTriangle className={`w-4 h-4 ${theme.iconColor}`} />
            </div>
            <div>
              <h3 className="text-[11px] font-semibold uppercase tracking-wider text-slate-400">
                Hazard Predicted Ahead
              </h3>
              <span className="text-[10px] text-slate-500 font-mono">CARD 2 of 3</span>
            </div>
          </div>
          <span
            className={`flex items-center gap-1.5 px-2 py-0.5 rounded-full border text-[10px] font-bold uppercase tracking-wide ${theme.badge} ${theme.badgeText}`}
          >
            {RISK_EMOJI[risk.riskLevel]} {RISK_LABEL[risk.riskLevel]}
          </span>
        </div>

        {/* Score arc + hazard text */}
        <div className="flex items-start gap-3 mb-3">
          <ScoreArc score={risk.riskScore} color={theme.scoreColor} />
          <div className="flex-1 min-w-0">
            <p className="text-sm font-semibold text-white leading-snug mb-1">
              {risk.predictedHazard}
            </p>
            <div className="flex items-start gap-1.5 mt-1.5">
              <BookOpen className="w-3.5 h-3.5 text-slate-500 mt-0.5 flex-shrink-0" />
              <p className="text-[11px] text-slate-400 leading-relaxed italic">
                {risk.offsetWellCitation}
              </p>
            </div>
          </div>
        </div>

        {/* Next formation look-ahead sub-strip */}
        <div className="flex items-center justify-between pt-2.5 border-t border-slate-700/40">
          <div className="flex items-center gap-1.5 text-xs text-slate-400">
            <ArrowDown className="w-3.5 h-3.5" />
            <span>Next:</span>
            <span className="font-medium text-slate-300">{telemetry.nextFormation}</span>
          </div>
          <span className="text-xs font-mono text-slate-500">
            @ {telemetry.nextFormationDepthM.toFixed(0)}m MD
          </span>
        </div>
      </div>

      {/* ============================================================ */}
      {/*  CARD 3 — Immediate Action Required                          */}
      {/* ============================================================ */}
      <div
        className={`relative rounded-xl p-4 shadow-md overflow-hidden transition-all duration-500 ${
          isCritical
            ? 'bg-red-950/30 border border-red-600/60 shadow-[0_0_20px_-3px_rgba(239,68,68,0.2)]'
            : 'bg-slate-800/50 border border-slate-700/80'
        }`}
      >
        {/* Left accent */}
        <div
          className={`absolute left-0 top-0 bottom-0 w-[3px] rounded-l-xl ${
            isCritical
              ? 'bg-gradient-to-b from-red-500 to-red-700'
              : 'bg-gradient-to-b from-purple-500 to-purple-700'
          }`}
        />

        <div className="flex items-start justify-between mb-3">
          <div className="flex items-center gap-2">
            <div
              className={`p-1.5 rounded-md border ${
                isCritical
                  ? 'bg-red-950 border-red-600/60'
                  : 'bg-purple-950/60 border-purple-800/50'
              }`}
            >
              {isCritical ? (
                <Siren className="w-4 h-4 text-red-400" />
              ) : (
                <ShieldAlert className="w-4 h-4 text-purple-400" />
              )}
            </div>
            <div>
              <h3 className="text-[11px] font-semibold uppercase tracking-wider text-slate-400">
                Immediate Action
              </h3>
              <span className="text-[10px] text-slate-500 font-mono">CARD 3 of 3</span>
            </div>
          </div>

          {/* Priority badge — only visible at critical */}
          {isCritical ? (
            <span className="flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-red-600/90 text-white text-[10px] font-bold uppercase tracking-widest animate-pulse shadow-lg shadow-red-900/30">
              <Siren className="w-3 h-3" />
              PRIORITY 1
            </span>
          ) : (
            <span className="flex items-center gap-1.5 px-2 py-0.5 rounded-full bg-slate-800 border border-slate-700 text-[10px] font-semibold text-slate-400 uppercase">
              ADVISORY
            </span>
          )}
        </div>

        {/* Action text */}
        <div
          className={`rounded-lg p-3 mb-3 ${
            isCritical
              ? 'bg-red-950/40 border border-red-800/40'
              : 'bg-[#0A101D] border border-slate-800/60'
          }`}
        >
          <p
            className={`text-sm leading-relaxed ${
              isCritical ? 'text-red-100 font-semibold' : 'text-slate-200'
            }`}
          >
            {risk.immediateAction}
          </p>
        </div>

        {/* Footer context */}
        <div className="flex items-center justify-between pt-2 border-t border-slate-700/40">
          <span className="text-[11px] text-slate-500">
            Risk Score:{' '}
            <span
              className={`font-mono font-bold ${theme.scoreColor}`}
              style={{ fontVariantNumeric: 'tabular-nums' }}
            >
              {risk.riskScore}/100
            </span>
          </span>
          <span className="text-[11px] text-slate-500 font-mono">
            Layer 5 Alerting
          </span>
        </div>
      </div>
    </div>
  );
};
