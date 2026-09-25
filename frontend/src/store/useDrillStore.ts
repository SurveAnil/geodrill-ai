import { create } from 'zustand';

export type RiskLevel = 'low' | 'medium' | 'high' | 'critical';

export type ScenarioType =
  | 'normal_drilling'
  | 'approaching_northwind_losses'
  | 'northwind_gas_influx'
  | 'northwind_tight_hole';

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
  alertId?: string;
}

interface DrillStore {
  // Well Header Info
  activeWellId: string;
  wellName: string;
  field: string;
  operator: string;
  targetTotalDepthM: number;
  activeWellLocation: { latitude: number; longitude: number };
  operatingMode: 'DEMO' | 'LIVE' | 'SIMULATED';
  alertCount: number;
  acknowledgedAt?: string;
  acknowledgedRiskIdentity?: string;

  // Real-time Telemetry (10Hz stream state)
  telemetry: TelemetryData;
  risk: RiskState;

  // Simulator Controls
  isSimulating: boolean;
  isStreaming10Hz: boolean;
  selectedScenario: ScenarioType;
  simulationTickCount: number;
  backendStatus: 'demo' | 'online' | 'unavailable';

  // Actions
  setDepth: (md: number) => void;
  setTelemetry: (data: Partial<TelemetryData>) => void;
  setScenario: (scenario: ScenarioType) => void;
  toggleSimulation: () => void;
  toggle10HzStream: () => void;
  setActiveWell: (wellId: string) => void;
  setActiveWellContext: (well: {
    well_id: string;
    operator?: string;
    field_name?: string;
    latitude?: number;
    longitude?: number;
    total_depth_m?: number;
    current_depth_m?: number;
    current_formation?: string;
  }) => void;
  setActiveWellLocation: (location: { latitude: number; longitude: number }) => void;
  stepSimulation: () => void;
  setRisk: (risk: RiskState) => void;
  setBackendStatus: (status: DrillStore['backendStatus']) => void;
  acknowledgeCurrentRisk: () => void;
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
    name: 'Normal Drilling (Harbour Shale)',
    description: 'Drilling through Harbour Shale with nominal Northwind Field parameters.',
    telemetry: {
      measuredDepthM: 1850.0,
      trueVerticalDepthM: 1820.0,
      rop: 24.5,
      wob: 22.0,
      torque: 11.2,
      flowRate: 750,
      standpipePressure: 2850,
      mudWeightSg: 1.35,
      currentFormation: 'Harbour Shale',
      nextFormation: 'Northwind Sandstone',
      nextFormationDepthM: 3025.0,
    },
    risk: {
      riskLevel: 'low',
      riskScore: 8,
      predictedHazard: 'No immediate geological anomalies detected ahead in next 100m.',
      immediateAction: 'Continue rotary drilling with standard surveillance. Maintain 1.35 SG mud weight.',
      offsetWellCitation: 'Northwind offset wells show stable drilling through Harbour Shale.',
    },
  },
  approaching_northwind_losses: {
    name: 'Northwind Reservoir (Offset Risk)',
    description: 'Entering Northwind Sandstone. Offset wells recorded kick, losses, stuck pipe, and torque issues near 3,100 m.',
    telemetry: {
      measuredDepthM: 3108.0,
      trueVerticalDepthM: 3032.0,
      rop: 16.2,
      wob: 28.5,
      torque: 21.4,
      flowRate: 640,
      standpipePressure: 13100,
      mudWeightSg: 1.35,
      currentFormation: 'Northwind Sandstone',
      nextFormation: 'Northwind Sandstone base',
      nextFormationDepthM: 3415.0,
    },
    risk: {
      riskLevel: 'high',
      riskScore: 78,
      predictedHazard: 'Comparable offset incident zone ahead near 3,118m MD / Northwind Sandstone',
      immediateAction: 'Verify flow and pit volume, hold WOB, and prepare the approved kick/loss response while drilling through the offset evidence window.',
      offsetWellCitation: 'OIL-NWIS-02 and OIL-NWIS-03: kick, mud loss, and stuck-pipe events between 3,096m and 3,172m.',
    },
  },
  northwind_gas_influx: {
    name: 'Northwind Gas Influx (Kick Risk)',
    description: 'Reservoir warning. OIL-NWIS-02 recorded an 8 bbl kick near 3118m.',
    telemetry: {
      measuredDepthM: 2505.0,
      trueVerticalDepthM: 2440.0,
      rop: 28.0,
      wob: 18.0,
      torque: 18.9,
      flowRate: 680,
      standpipePressure: 3350,
      mudWeightSg: 1.48,
      currentFormation: 'Northwind Sandstone',
      nextFormation: 'Northwind Sandstone base',
      nextFormationDepthM: 3415.0,
    },
    risk: {
      riskLevel: 'critical',
      riskScore: 92,
      predictedHazard: 'Gas Influx / Overpressured Reservoir Pocket Ahead at 2510m MD',
      immediateAction: 'Perform flow check. Space out and prepare annular preventer. Have Driller Method circulation sheet ready.',
      offsetWellCitation: 'OIL-NWIS-02 source report p.12: 8 bbl pit gain near 3118m, BOP closed.',
    },
  },
  northwind_tight_hole: {
    name: 'Northwind Tight Hole (Stuck Pipe Risk)',
    description: 'Reservoir section. OIL-NWIS-03 recorded stuck pipe near 3096m.',
    telemetry: {
      measuredDepthM: 2802.0,
      trueVerticalDepthM: 2710.5,
      rop: 7.5,
      wob: 32.0,
      torque: 23.5,
      flowRate: 580,
      standpipePressure: 3450,
      mudWeightSg: 1.52,
      currentFormation: 'Northwind Sandstone',
      nextFormation: 'Northwind Sandstone base',
      nextFormationDepthM: 3415.0,
    },
    risk: {
      riskLevel: 'medium',
      riskScore: 62,
      predictedHazard: 'Tight Hole Section & Mechanical Sticking Hazard at 2810m MD',
      immediateAction: 'Limit overpull to 25 klbs. Perform wiper trips every stand. Ensure hydraulic jars are energized.',
      offsetWellCitation: 'OIL-NWIS-03 source report p.8: string stuck near 3096m across a shale streak.',
    },
  },
};

const getRiskIdentity = (risk: RiskState) => risk.alertId || `${risk.riskLevel}:${risk.predictedHazard}`;

export const useDrillStore = create<DrillStore>((set, get) => ({
  activeWellId: 'OIL-NWIS-01',
  wellName: 'OIL-NWIS-01',
  field: 'Northwind Field',
  operator: 'Orion Inlet Limited',
  targetTotalDepthM: 3415.0,
  activeWellLocation: { latitude: 58.4121, longitude: 1.8422 },
  operatingMode: 'DEMO',
  alertCount: 1,

  telemetry: SCENARIO_PRESETS.approaching_northwind_losses.telemetry,
  risk: SCENARIO_PRESETS.approaching_northwind_losses.risk,

  isSimulating: false,
  isStreaming10Hz: true,
  selectedScenario: 'approaching_northwind_losses',
  simulationTickCount: 0,
  backendStatus: 'demo',

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
    set((state) => {
      const identityChanged = getRiskIdentity(state.risk) !== getRiskIdentity(preset.risk);
      return {
        selectedScenario: scenarioKey,
        telemetry: { ...preset.telemetry },
        risk: { ...preset.risk },
        acknowledgedAt: identityChanged ? undefined : state.acknowledgedAt,
        acknowledgedRiskIdentity: identityChanged ? undefined : state.acknowledgedRiskIdentity,
        alertCount: identityChanged && ['high', 'critical'].includes(preset.risk.riskLevel) ? 1 : state.alertCount,
      };
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

  setActiveWellContext: (well) =>
    set((state) => {
      if (typeof window !== 'undefined') {
        window.localStorage.setItem('geodrill.activeWellId', well.well_id);
      }
      return {
        activeWellId: well.well_id,
        wellName: well.well_id,
        operator: well.operator || state.operator,
        field: well.field_name || state.field,
        targetTotalDepthM: well.total_depth_m || state.targetTotalDepthM,
        activeWellLocation: {
          latitude: well.latitude ?? state.activeWellLocation.latitude,
          longitude: well.longitude ?? state.activeWellLocation.longitude,
        },
        telemetry: {
          ...state.telemetry,
          measuredDepthM: well.current_depth_m ?? state.telemetry.measuredDepthM,
          trueVerticalDepthM: well.current_depth_m
            ? +(well.current_depth_m * 0.975).toFixed(1)
            : state.telemetry.trueVerticalDepthM,
          currentFormation: well.current_formation || state.telemetry.currentFormation,
        },
      };
    }),

  setActiveWellLocation: (activeWellLocation) => set({ activeWellLocation }),

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
  setRisk: (risk) => set((state) => {
    const identityChanged = getRiskIdentity(state.risk) !== getRiskIdentity(risk);
    return {
      risk,
      acknowledgedAt: identityChanged ? undefined : state.acknowledgedAt,
      acknowledgedRiskIdentity: identityChanged ? undefined : state.acknowledgedRiskIdentity,
      alertCount: identityChanged && ['high', 'critical'].includes(risk.riskLevel) ? 1 : state.alertCount,
    };
  }),
  setBackendStatus: (backendStatus) => set({ backendStatus }),
  acknowledgeCurrentRisk: () => set((state) => ({
    alertCount: 0,
    acknowledgedAt: new Date().toISOString(),
    acknowledgedRiskIdentity: getRiskIdentity(state.risk),
  })),
}));
