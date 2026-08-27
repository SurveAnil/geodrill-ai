'use client';

import React, { useEffect } from 'react';
import {
  Activity,
  Play,
  Pause,
  Compass,
  Layers,
  ChevronDown,
  Sparkles,
  Radio,
  SlidersHorizontal,
} from 'lucide-react';
import { useDrillStore, SCENARIO_PRESETS, ScenarioType } from '@/store/useDrillStore';

export const TopNav: React.FC = () => {
  const {
    activeWellId,
    field,
    operator,
    telemetry,
    risk,
    isSimulating,
    isStreaming10Hz,
    selectedScenario,
    setScenario,
    toggleSimulation,
    toggle10HzStream,
    stepSimulation,
  } = useDrillStore();

  // 10Hz live simulation ticker
  useEffect(() => {
    if (!isSimulating) return;
    const interval = setInterval(() => {
      stepSimulation();
    }, 100); // 10 ticks per second = 10Hz
    return () => clearInterval(interval);
  }, [isSimulating, stepSimulation]);

  return (
    <header className="w-full bg-[#0B1120] border-b border-[#1E293B] sticky top-0 z-50 select-none">
      <div className="max-w-[1920px] mx-auto px-4 py-2.5 flex items-center justify-between gap-4">
        {/* Left: Branding & Active Rig Metadata */}
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2.5">
            <div className="h-9 w-9 rounded-lg bg-gradient-to-br from-cyan-500 to-blue-600 flex items-center justify-center shadow-lg shadow-cyan-500/20">
              <Compass className="w-5 h-5 text-white animate-spin-slow" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="font-bold text-base tracking-wider text-white">
                  eRTMAC<span className="text-cyan-400">-NWIS</span>
                </span>
                <span className="px-1.5 py-0.5 rounded text-[10px] font-mono uppercase font-semibold bg-cyan-950/80 text-cyan-300 border border-cyan-800/60">
                  v2.4 RT
                </span>
              </div>
              <p className="text-[11px] text-slate-400 leading-none">
                AI-Powered Offset Well Intelligence
              </p>
            </div>
          </div>

          <div className="hidden lg:block h-6 w-px bg-slate-800" />

          {/* Active Well Header Pill */}
          <div className="hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-lg bg-[#111A2E] border border-slate-800">
            <div className="h-2 w-2 rounded-full bg-cyan-400" />
            <div className="text-xs">
              <span className="text-slate-400">Well: </span>
              <span className="font-semibold text-white font-mono">{activeWellId}</span>
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

        {/* Right: State Simulator & Live 10Hz Controls */}
        <div className="flex items-center gap-3">
          {/* State Simulator Scenario Dropdown */}
          <div className="flex items-center bg-[#111A2E] rounded-lg border border-slate-800 p-1">
            <div className="flex items-center gap-1.5 px-2 text-slate-400">
              <SlidersHorizontal className="w-3.5 h-3.5 text-cyan-400" />
              <span className="text-[11px] font-medium hidden md:inline">Scenario:</span>
            </div>
            <select
              value={selectedScenario}
              onChange={(e) => setScenario(e.target.value as ScenarioType)}
              className="bg-[#090D16] text-white text-xs font-medium rounded px-2.5 py-1 border border-slate-700/60 focus:outline-none focus:border-cyan-500 cursor-pointer"
            >
              {Object.entries(SCENARIO_PRESETS).map(([key, item]) => (
                <option key={key} value={key} className="bg-[#0F172A] text-white">
                  {item.name}
                </option>
              ))}
            </select>

            {/* Run / Pause Simulator Button */}
            <button
              onClick={toggleSimulation}
              title={isSimulating ? 'Pause 10Hz Drill Simulation' : 'Start 10Hz Drill Simulation'}
              className={`ml-1.5 px-2.5 py-1 rounded text-xs font-semibold flex items-center gap-1.5 transition-all ${
                isSimulating
                  ? 'bg-amber-500/20 text-amber-300 border border-amber-500/40 hover:bg-amber-500/30'
                  : 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 hover:bg-cyan-500/30'
              }`}
            >
              {isSimulating ? (
                <>
                  <Pause className="w-3 h-3 fill-current" />
                  <span className="hidden sm:inline">Pause</span>
                </>
              ) : (
                <>
                  <Play className="w-3 h-3 fill-current" />
                  <span className="hidden sm:inline">Simulate</span>
                </>
              )}
            </button>
          </div>

          {/* 10Hz Stream Status Badge */}
          <button
            onClick={toggle10HzStream}
            title="Click to toggle 10Hz Telemetry Stream"
            className={`flex items-center gap-2 px-2.5 py-1.5 rounded-lg border text-xs font-mono transition-all ${
              isStreaming10Hz
                ? 'bg-emerald-950/40 text-emerald-300 border-emerald-800/80 shadow-sm shadow-emerald-900/20'
                : 'bg-slate-900 text-slate-400 border-slate-800'
            }`}
          >
            <span className="relative flex h-2 w-2">
              {isStreaming10Hz && (
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75" />
              )}
              <span
                className={`relative inline-flex rounded-full h-2 w-2 ${
                  isStreaming10Hz ? 'bg-emerald-400' : 'bg-slate-500'
                }`}
              />
            </span>
            <span className="font-semibold text-[11px]">
              {isStreaming10Hz ? 'LIVE 10Hz' : 'OFFLINE'}
            </span>
          </button>
        </div>
      </div>
    </header>
  );
};
