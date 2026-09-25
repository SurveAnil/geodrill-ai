'use client';

import React, { useEffect } from 'react';
import {
  Activity,
  Compass,
  Layers,
  Menu,
} from 'lucide-react';
import { useDrillStore } from '@/store/useDrillStore';
import { apiClient, toTelemetryPoint } from '@/lib/api';

export const TopNav: React.FC<{ onMenuOpen?: () => void }> = ({ onMenuOpen }) => {
  const {
    activeWellId,
    wellName,
    field,
    telemetry,
    isSimulating,
    isStreaming10Hz,
    stepSimulation,
    setRisk,
    setBackendStatus,
    backendStatus,
    alertCount,
  } = useDrillStore();

  // 10Hz live simulation ticker
  useEffect(() => {
    if (!isSimulating) return;
    const interval = setInterval(() => {
      stepSimulation();
    }, 100); // 10 ticks per second = 10Hz
    return () => clearInterval(interval);
  }, [isSimulating, stepSimulation]);

  // Keep the simulator useful offline while synchronising samples and risk when the API is available.
  useEffect(() => {
    if (!isStreaming10Hz) return;
    let busy = false;
    let ticks = 0;
    const interval = setInterval(async () => {
      if (busy) return;
      busy = true;
      const state = useDrillStore.getState();
      const point = toTelemetryPoint(state.activeWellId, state.telemetry);
      try {
        await apiClient.ingestTelemetry([point]);
        if (++ticks % 10 === 0) {
          const [prediction, alerts] = await Promise.all([
            apiClient.predictRisk(point, state.telemetry.currentFormation),
            apiClient.evaluateAlerts(point, state.telemetry.currentFormation),
          ]);
          const hasHistoricalEvidence = Object.values(prediction.hazards).some(
            (hazard) => (hazard.evidence?.length || 0) > 0
          );
          if (!hasHistoricalEvidence) {
            setBackendStatus('online');
            return;
          }
          const ranked = Object.entries(prediction.hazards).sort((a, b) => b[1].probability - a[1].probability)[0];
          const alert = alerts.alerts[0];
          if (ranked) {
            const level = ranked[1].risk_level;
            const riskLevel = level === 'high' && (alert?.severity === 'critical') ? 'critical' : level;
            setRisk({
              riskLevel: riskLevel as 'low' | 'medium' | 'high' | 'critical',
              riskScore: Math.round(ranked[1].probability * 100),
              predictedHazard: alert?.hazard || ranked[0].replace(/_/g, ' '),
              immediateAction: alerts.recommendations[0]?.action || 'Continue surveillance and follow the approved well programme.',
              offsetWellCitation: ranked[1].evidence?.[0]?.source_doc || 'Backend predictive-risk baseline; no citation returned.',
              alertId: alert?.alert_id,
            });
          }
        }
        setBackendStatus('online');
      } catch {
        setBackendStatus('unavailable');
      } finally {
        busy = false;
      }
    }, 1000);
    return () => clearInterval(interval);
  }, [isStreaming10Hz, setRisk, setBackendStatus]);

  return (
    <header className="w-full bg-[#0B1120] border-b border-[#1E293B] sticky top-0 z-50 select-none">
      <div className="max-w-[1920px] mx-auto px-4 py-2.5 flex items-center justify-between gap-4">
        {/* Left: Branding & Active Rig Metadata */}
        <div className="flex items-center gap-4">
          <button onClick={onMenuOpen} className="rounded border border-slate-700 p-1.5 text-slate-300 md:hidden" aria-label="Open navigation"><Menu className="h-4 w-4" /></button>
          <div className="flex items-center gap-2.5">
            <div className="h-9 w-9 rounded-lg bg-gradient-to-br from-cyan-500 to-blue-600 flex items-center justify-center shadow-lg shadow-cyan-500/20">
              <Compass className="w-5 h-5 text-white animate-spin-slow" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="font-bold text-base tracking-wider text-white">
                  Geo<span className="text-cyan-400">Drill</span>
                </span>
                <span className="px-1.5 py-0.5 rounded text-[10px] font-mono uppercase font-semibold bg-cyan-950/80 text-cyan-300 border border-cyan-800/60">
                  v2.4 RT
                </span>
              </div>
              <p className="text-[11px] text-slate-400 leading-none">
                NWIS drilling intelligence
              </p>
            </div>
          </div>

          <div className="hidden lg:block h-6 w-px bg-slate-800" />

          {/* Active Well Header Pill */}
          <div className="hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-lg bg-[#111A2E] border border-slate-800">
            <div className="h-2 w-2 rounded-full bg-cyan-400" />
            <div className="text-xs">
              <span className="text-slate-400">Well: </span>
              <span className="font-semibold text-white font-mono">{wellName || activeWellId}</span>
              <span className="text-slate-500 mx-1.5">•</span>
              <span className="text-slate-400">{field}</span>
            </div>
          </div>
        </div>

        {/* Center: Live Depth & Stratigraphy Banner */}
        <div className="hidden xl:flex items-center gap-4 px-4 py-1.5 rounded-lg bg-[#0F172A] border border-slate-800/80 shadow-inner">
          <div className="flex items-center gap-2 text-xs">
            <span className="text-slate-400 uppercase font-mono text-[10px]">Active MD:</span>
            <span className="font-mono font-bold text-sm text-cyan-300">
              {telemetry.measuredDepthM.toFixed(1)} <span className="text-[10px] text-slate-400 font-normal">m</span>
            </span>
          </div>
          <div className="h-4 w-px bg-slate-800" />
          <div className="flex items-center gap-2 text-xs">
            <span className="text-slate-400 uppercase font-mono text-[10px]">TVD:</span>
            <span className="font-mono font-semibold text-slate-200">
              {telemetry.trueVerticalDepthM.toFixed(1)} <span className="text-[10px] text-slate-400 font-normal">m</span>
            </span>
          </div>
          <div className="h-4 w-px bg-slate-800" />
          <div className="flex items-center gap-2 text-xs">
            <span className="text-slate-400 uppercase font-mono text-[10px]">Formation:</span>
            <span className="font-semibold text-amber-300 flex items-center gap-1">
              <Layers className="w-3.5 h-3.5" />
              {telemetry.currentFormation}
            </span>
          </div>
        </div>

        {/* Right: global connection and operating mode only */}
        <div className="flex items-center gap-3">
          <span className="rounded border border-amber-800/70 bg-amber-950/40 px-2 py-1 text-[10px] font-mono font-semibold text-amber-300">
            DEMO / SIMULATED
          </span>
          <span className="rounded border border-slate-700 px-2 py-1 text-[10px] font-mono text-slate-300">
            Alerts: {alertCount}
          </span>
          <span className={`hidden sm:flex items-center gap-1 text-[10px] font-mono ${backendStatus === 'online' ? 'text-emerald-400' : backendStatus === 'unavailable' ? 'text-amber-400' : 'text-slate-500'}`}>
            <span className="h-1.5 w-1.5 rounded-full bg-current" /> API: {backendStatus === 'online' ? 'CONNECTED' : backendStatus === 'unavailable' ? 'UNAVAILABLE' : 'DEMO'}
          </span>
        </div>
      </div>
    </header>
  );
};
