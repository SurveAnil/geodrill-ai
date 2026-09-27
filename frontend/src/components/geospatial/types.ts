export type RiskLevel = 'high' | 'medium' | 'low';
export type WellStatus = 'Completed' | 'Drilling' | 'Abandoned';
export type TrajectoryType = 'Directional' | 'Vertical' | 'S-Type' | 'Horizontal';

export interface HistoricalEvent {
  id: string;
  type: 'Gas Kick' | 'Mud Loss' | 'Stuck Pipe' | 'High Torque' | 'Cementing' | 'NPT' | string;
  depthInterval: string;
  severity: RiskLevel;
  description: string;
  nptHours: number;
}

export interface OffsetWellFeature {
  id: string;
  name: string;
  wellId: string;
  lat: number;
  lon: number;
  distanceKm: number;
  direction: string;
  formation: string;
  status: WellStatus;
  riskLevel: RiskLevel;
  totalDepthM: number;
  spudDate: string;
  completionDate: string;
  reservoir: string;
  trajectory: TrajectoryType;
  nptHours: number;
  hazardSummary: string;
  historicalEvents: HistoricalEvent[];
  lessonsLearned: string[];
  operator?: string;
  field_name?: string;
  current_depth_m?: number;
  current_formation?: string;
  total_depth_m?: number;
}

export interface WellFiltersState {
  formation: string;
  riskLevel: string;
  eventType: string;
  wellStatus: string;
}

export type MapStyleType = 'dark' | 'satellite' | 'terrain';
