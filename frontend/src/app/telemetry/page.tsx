'use client';
import { SCENARIO_PRESETS, ScenarioType, useDrillStore } from '@/store/useDrillStore';
import { AppShell } from '@/components/layout/AppShell';
import { PageHeader } from '@/components/layout/PageHeader';
import { TelemetryPanel } from '@/components/telemetry/TelemetryPanel';
import Link from 'next/link';
export default function TelemetryPage() {
  const { selectedScenario, setScenario, isSimulating, toggleSimulation, isStreaming10Hz, toggle10HzStream, telemetry } = useDrillStore();
  return <AppShell>
    <PageHeader title="Telemetry" description="Current drilling parameters and simulated 10 Hz stream." />
    <div className="mb-4 flex flex-wrap items-center gap-3 rounded-xl border border-slate-700 bg-slate-900/60 p-3 text-xs text-slate-200">
      <span className="font-mono font-semibold">Simulation controls</span>
      <label className="flex items-center gap-2">Scenario
        <select value={selectedScenario} onChange={(event) => setScenario(event.target.value as ScenarioType)} className="rounded bg-[#090D16] px-2 py-1 text-slate-100">
          {Object.entries(SCENARIO_PRESETS).map(([key, item]) => <option key={key} value={key}>{item.name}</option>)}
        </select>
      </label>
      <button onClick={toggleSimulation} className="rounded border border-cyan-700 px-3 py-1 text-cyan-200">{isSimulating ? 'Pause simulation' : 'Start simulation'}</button>
      <button onClick={toggle10HzStream} className="rounded border border-slate-700 px-3 py-1 text-slate-200">{isStreaming10Hz ? 'Pause API stream' : 'Start API stream'}</button>
    </div>
    <div className="mb-4 flex flex-wrap items-center justify-between gap-3 rounded-xl border border-orange-700/60 bg-orange-950/20 p-3 text-sm"><div><span className="font-semibold text-orange-200">Historical depth alert:</span> <span className="text-slate-200">OIL-NWIS-02 kick at 3,118 m — {Math.max(0, 3118 - telemetry.measuredDepthM).toFixed(0)} m ahead at current depth.</span></div><Link href="/lessons?evidence=northwind" className="text-xs font-semibold text-cyan-300">View evidence →</Link></div>
    <div className="mb-4 rounded-xl border border-slate-800 bg-slate-900/50 p-3 text-xs"><div className="flex justify-between text-slate-300"><span>Formation progress: {telemetry.currentFormation}</span><span>{Math.max(0, telemetry.nextFormationDepthM - telemetry.measuredDepthM).toFixed(0)} m to next boundary</span></div><div className="mt-2 h-2 overflow-hidden rounded-full bg-slate-800"><div className="h-full w-[55%] rounded-full bg-amber-400" /></div></div>
    <div className="max-w-3xl rounded-xl border border-slate-800 bg-[#0F172A]/80 p-5"><TelemetryPanel /></div>
  </AppShell>;
}
