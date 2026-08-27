import { create } from 'zustand';

export type RiskLevel = 'low' | 'medium' | 'high' | 'critical';

export type ScenarioType =
  | 'normal_drilling'
  | 'approaching_hugin_losses'
  | 'gas_kick_influx'
  | 'tight_hole_overpull';

export interface TelemetryData {
  measuredDepthM: number;
  trueVerticalDepthM: number;
  rop: number; // m/hr
  wob: number; // klbs
  torque: number; // kft-lbs
  flowRate: number; // gpm
  standpipePressure: number; // psi
  mudWeightSg: number; // SG
  currentFormation: string;
  nextFormation: string;
  nextFormationDepthM: number;
}

export interface RiskState {
  riskLevel: RiskLevel;
  riskScore: number; // 0 - 100
  predictedHazard: string;
  immediateAction: string;
  offsetWellCitation: string;
}

interface DrillStore {
  // Well Header Info
  activeWellId: string;
  wellName: string;
  field: string;
  operator: string;
  targetTotalDepthM: number;

  // Real-time Telemetry (10Hz stream state)
  telemetry: TelemetryData;
  risk: RiskState;

  // Simulator Controls
  isSimulating: boolean;
  isStreaming10Hz: boolean;
  selectedScenario: ScenarioType;
  simulationTickCount: number;

  // Actions
  setDepth: (md: number) => void;
  setTelemetry: (data: Partial<TelemetryData>) => void;
  setScenario: (scenario: ScenarioType) => void;
  toggleSimulation: () => void;
  toggle10HzStream: () => void;
  setActiveWell: (wellId: string) => void;
  stepSimulation: () => void;
}

export const SCENARIO_PRESETS: Record<
  ScenarioType,
  {
    name: string;
    description: string;
    telemetry: TelemetryData;
    risk: RiskState;
  }
> = {
  normal_drilling: {
    name: 'Normal Drilling (Stable Chalk)',
    description: 'Drilling smoothly through Rogaland / Chalk Group with nominal parameters.',
    telemetry: {
      measuredDepthM: 1850.0,
      trueVerticalDepthM: 1820.0,
      rop: 24.5,
      wob: 22.0,
      torque: 11.2,
      flowRate: 750,
      standpipePressure: 2850,
      mudWeightSg: 1.35,
      currentFormation: 'Chalk Group',
      nextFormation: 'Hugin Formation',
      nextFormationDepthM: 2420.0,
    },
    risk: {
      riskLevel: 'low',
      riskScore: 8,
      predictedHazard: 'No immediate geological anomalies detected ahead in next 100m.',
      immediateAction: 'Continue rotary drilling with standard surveillance. Maintain 1.35 SG mud weight.',
      offsetWellCitation: 'Offset wells 15/9-F-11B & 15/9-F-12 show clean drilling through Chalk.',
    },
  },
  approaching_hugin_losses: {
    name: 'Approaching Hugin (Loss Risk)',
    description: 'Entering Hugin sandstone reservoir. Offset well 15/9-F-11B experienced 15 bbl/hr mud loss at 2450m.',
    telemetry: {
      measuredDepthM: 2445.0,
      trueVerticalDepthM: 2390.2,
      rop: 16.2,
      wob: 28.5,
      torque: 16.4,
      flowRate: 640,
      standpipePressure: 3100,
      mudWeightSg: 1.45,
      currentFormation: 'Hugin Formation',
      nextFormation: 'Skagerrak Formation',
      nextFormationDepthM: 2750.0,
    },
    risk: {
      riskLevel: 'high',
      riskScore: 78,
      predictedHazard: 'Severe Mud Loss Zone Ahead (Depth 2450.0m MD / Hugin Formation)',
      immediateAction: 'Stage 50 bbl LCM pill (40 ppb blend) in active pit. Reduce flow rate to 550 gpm; monitor return pit volume.',
      offsetWellCitation: 'Well 15/9-F-11B (5.2km offset, WCR p.3): 15 bbl/hr loss at 2450m cured with 50 bbl LCM pill.',
    },
  },
  gas_kick_influx: {
    name: 'Hugin Gas Influx (Kick Risk)',
    description: 'Gas cap zone warning. Offset well 15/9-F-12 took a 12 bbl kick with pit gain at 2510m.',
    telemetry: {
      measuredDepthM: 2505.0,
      trueVerticalDepthM: 2440.0,
      rop: 28.0,
      wob: 18.0,
      torque: 18.9,
      flowRate: 680,
      standpipePressure: 3350,
      mudWeightSg: 1.48,
      currentFormation: 'Hugin Formation (Gas Cap)',
      nextFormation: 'Skagerrak Formation',
      nextFormationDepthM: 2750.0,
    },
    risk: {
      riskLevel: 'critical',
      riskScore: 92,
      predictedHazard: 'Gas Influx / Overpressured Reservoir Pocket Ahead at 2510m MD',
      immediateAction: 'Perform flow check. Space out and prepare annular preventer. Have Driller Method circulation sheet ready.',
      offsetWellCitation: 'Well 15/9-F-12 (200m offset, DDR p.2): 12 bbl pit gain at 2510m MD, shut in on annular BOP.',
    },
  },
  tight_hole_overpull: {
    name: 'Skagerrak Deep (Stuck Pipe Risk)',
    description: 'Deep shale/sand section. Offset well 15/9-F-11B experienced mechanical stuck pipe at 2810m.',
    telemetry: {
      measuredDepthM: 2802.0,
      trueVerticalDepthM: 2710.5,
      rop: 7.5,
      wob: 32.0,
      torque: 23.5,
      flowRate: 580,
      standpipePressure: 3450,
      mudWeightSg: 1.52,
      currentFormation: 'Skagerrak Formation',
      nextFormation: 'Base Total Depth',
      nextFormationDepthM: 3200.0,
    },
    risk: {
      riskLevel: 'medium',
      riskScore: 62,
      predictedHazard: 'Tight Hole Section & Mechanical Sticking Hazard at 2810m MD',
      immediateAction: 'Limit overpull to 25 klbs. Perform wiper trips every stand. Ensure hydraulic jars are energized.',
      offsetWellCitation: 'Well 15/9-F-11B (WCR p.5): 40 klbs overpull, stuck 6 hours, jarred free.',
    },
  },
};

export const useDrillStore = create<DrillStore>((set, get) => ({
  activeWellId: '15/9-F-11B',
  wellName: 'Volve 15/9-F-11B',
  field: 'Volve Field (PL 046)',
  operator: 'Statoil ASA',
  targetTotalDepthM: 3200.0,

  telemetry: SCENARIO_PRESETS.approaching_hugin_losses.telemetry,
  risk: SCENARIO_PRESETS.approaching_hugin_losses.risk,

  isSimulating: false,
  isStreaming10Hz: true,
  selectedScenario: 'approaching_hugin_losses',
  simulationTickCount: 0,

  setDepth: (md: number) =>
    set((state) => ({
      telemetry: {
        ...state.telemetry,
        measuredDepthM: md,
        trueVerticalDepthM: +(md * 0.978).toFixed(1),
      },
    })),

  setTelemetry: (data: Partial<TelemetryData>) =>
    set((state) => ({
      telemetry: { ...state.telemetry, ...data },
    })),

  setScenario: (scenarioKey: ScenarioType) => {
    const preset = SCENARIO_PRESETS[scenarioKey];
    if (!preset) return;
    set({
      selectedScenario: scenarioKey,
      telemetry: { ...preset.telemetry },
      risk: { ...preset.risk },
    });
  },

  toggleSimulation: () =>
    set((state) => ({
      isSimulating: !state.isSimulating,
    })),

  toggle10HzStream: () =>
    set((state) => ({
      isStreaming10Hz: !state.isStreaming10Hz,
    })),

  setActiveWell: (wellId: string) =>
    set({
      activeWellId: wellId,
      wellName: `Well ${wellId}`,
    }),

  stepSimulation: () => {
    const state = get();
    const currentMD = state.telemetry.measuredDepthM;
    const nextMD = +(currentMD + 0.15).toFixed(2);
    // Subtle jitter on telemetry to emulate real-time sensor fluctuation
    const ropJitter = +(Math.sin(Date.now() / 1000) * 0.4).toFixed(1);
    const torqueJitter = +(Math.cos(Date.now() / 800) * 0.3).toFixed(1);

    set({
      simulationTickCount: state.simulationTickCount + 1,
      telemetry: {
        ...state.telemetry,
        measuredDepthM: nextMD,
        trueVerticalDepthM: +(nextMD * 0.978).toFixed(1),
        rop: Math.max(1, +(state.telemetry.rop + ropJitter).toFixed(1)),
        torque: Math.max(1, +(state.telemetry.torque + torqueJitter).toFixed(1)),
      },
    });
  },
}));
