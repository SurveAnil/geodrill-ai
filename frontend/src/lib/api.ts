const API_URL = (process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000').replace(/\/$/, '');

export interface TelemetryPoint {
  timestamp: string;
  well_id: string;
  measured_depth_m: number;
  true_vertical_depth_m: number;
  rop: number;
  wob: number;
  torque: number;
  flow_rate: number;
  standpipe_pressure: number;
  mud_weight_sg: number;
}

export interface PredictiveRiskResponse {
  model_version: string;
  well_id: string;
  measured_depth_m: number;
  hazards: Record<string, { probability: number; risk_level: string; evidence?: Array<{ source_doc?: string; source_snippet?: string }> }>;
}

export interface AlertEvaluationResponse {
  alerts: Array<{ alert_id: string; severity: string; hazard: string; probability: number; recommendations?: Array<{ action: string }> }>;
  recommendations: Array<{ action: string; rationale: string; priority: string }>;
  evidence_found: boolean;
}
export interface NearbyWell { well_id?: string; name?: string; distance_km?: number; latitude?: number; longitude?: number; hazard?: string; status?: string }
export interface IncidentEvent { event_id?: number; well_id?: string; depth_m?: number; formation?: string; event_type?: string; severity?: string; description?: string; source_snippet?: string; mitigation?: string; key_lesson?: string; source_doc?: string; date?: string }
export interface CopilotResponse { query: string; normalized_query: string; answer: string; sources: Array<{ source_doc?: string; source_page?: number; well_id?: string; snippet?: string }> }
export interface FormationCorrelationResponse { correlations: Array<Record<string, unknown>>; explanation: string }
export interface TrajectoryResponse { stations: Array<Record<string, number>>; method: string; explanation: string }

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_URL}${path}`, { ...init, headers: { 'Content-Type': 'application/json', ...(init?.headers || {}) } });
  if (!response.ok) {
    const body = await response.json().catch(() => null) as { detail?: string } | null;
    throw new Error(body?.detail || `API request failed (${response.status})`);
  }
  return response.json() as Promise<T>;
}

export const apiClient = {
  ingestTelemetry(points: TelemetryPoint[]) {
    return request<{ accepted: number }>('/api/v1/telemetry', { method: 'POST', body: JSON.stringify({ points }) });
  },
  predictRisk(current: TelemetryPoint, formation?: string) {
    return request<PredictiveRiskResponse>('/api/v1/predictive-risk', {
      method: 'POST',
      body: JSON.stringify({ current_telemetry: current, formation, window_m: 100 }),
    });
  },
  evaluateAlerts(current: TelemetryPoint, formation?: string) {
    return request<AlertEvaluationResponse>('/api/v1/alerts', {
      method: 'POST',
      body: JSON.stringify({ current_telemetry: current, formation, window_m: 100 }),
    });
  },
  acknowledgeAlert(alertId: string) {
    return request<{ alert_id: string; status: string; acknowledged_at: string }>(`/api/v1/alerts/${encodeURIComponent(alertId)}/acknowledge`, { method: 'POST' });
  },
  copilotSearch(query: string, formation?: string) {
    return request<CopilotResponse>('/api/v1/copilot/search', { method: 'POST', body: JSON.stringify({ query, formation, top_k: 5 }) });
  },
  nearbyWells(lat: number, lon: number, radiusKm = 10, excludeWellId?: string) {
    const params = new URLSearchParams({ lat: String(lat), lon: String(lon), radius_km: String(radiusKm) });
    if (excludeWellId) params.set('exclude_well_id', excludeWellId);
    return request<NearbyWell[]>(`/api/v1/wells/nearby?${params}`);
  },
  correlateIncidents(wellId: string, depthM: number, formation?: string) {
    const params = new URLSearchParams({ well_id: wellId, depth_m: String(depthM), window_m: '100' });
    if (formation) params.set('formation', formation);
    return request<IncidentEvent[]>(`/api/v1/incidents/correlate-near?${params}`);
  },
  correlateFormations(stations: Array<{ md: number; inclination: number; azimuth: number }>, formationTops: Array<Record<string, unknown>>) {
    return request<FormationCorrelationResponse>('/api/v1/trajectory/correlate-formations', { method: 'POST', body: JSON.stringify({ stations, formation_tops: formationTops }) });
  },
};

export function toTelemetryPoint(wellId: string, telemetry: {
  measuredDepthM: number; trueVerticalDepthM: number; rop: number; wob: number;
  torque: number; flowRate: number; standpipePressure: number; mudWeightSg: number;
}): TelemetryPoint {
  return {
    timestamp: new Date().toISOString(), well_id: wellId,
    measured_depth_m: telemetry.measuredDepthM, true_vertical_depth_m: telemetry.trueVerticalDepthM,
    rop: telemetry.rop, wob: telemetry.wob, torque: telemetry.torque,
    flow_rate: telemetry.flowRate, standpipe_pressure: telemetry.standpipePressure,
    mud_weight_sg: telemetry.mudWeightSg,
  };
}
