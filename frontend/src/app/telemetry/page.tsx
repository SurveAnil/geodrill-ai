'use client';
import { SCENARIO_PRESETS, ScenarioType, useDrillStore } from '@/store/useDrillStore';
import { AppShell } from '@/components/layout/AppShell';
import { PageHeader } from '@/components/layout/PageHeader';
import { TelemetryPanel } from '@/components/telemetry/TelemetryPanel';
export default function TelemetryPage() {
  const { selectedScenario, setScenario, isSimulating, toggleSimulation, isStreaming10Hz, toggle10HzStream } = useDrillStore();
  return <AppShell>
    <PageHeader title="Telemetry" description="Current drilling parameters and simulated 10 Hz stream." />
    <div className="mb-4 flex flex-wrap items-center gap-3 rounded-xl border border-amber-800/60 bg-amber-950/20 p-3 text-xs text-amber-200">
      <span className="font-mono font-semibold">DEMO MODE — simulated telemetry only</span>
      <label className="flex items-center gap-2">Scenario
        <select value={selectedScenario} onChange={(event) => setScenario(event.target.value as ScenarioType)} className="rounded bg-[#090D16] px-2 py-1 text-slate-100">
          {Object.entries(SCENARIO_PRESETS).map(([key, item]) => <option key={key} value={key}>{item.name}</option>)}
        </select>
      </label>
      <button onClick={toggleSimulation} className="rounded border border-cyan-700 px-3 py-1 text-cyan-200">{isSimulating ? 'Pause simulation' : 'Start simulation'}</button>
      <button onClick={toggle10HzStream} className="rounded border border-slate-700 px-3 py-1 text-slate-200">{isStreaming10Hz ? 'Pause API stream' : 'Start API stream'}</button>
    </div>
    <div className="max-w-3xl rounded-xl border border-slate-800 bg-[#0F172A]/80 p-5"><TelemetryPanel /></div>
  </AppShell>;
}
