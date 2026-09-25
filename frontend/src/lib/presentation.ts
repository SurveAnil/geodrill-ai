export function formatHazardLabel(value?: string) {
  if (!value) return 'Historical event';
  return value
    .replace(/[_-]+/g, ' ')
    .replace(/\b\w/g, (letter) => letter.toUpperCase())
    .replace(/\b(At|And|Or|The)\b/g, (word) => word.toLowerCase())
    .replace(/(\d[\d,]*(?:\.\d+)?)\s+M\b/g, '$1 m');
}

export const DEMO_OFFSET_WELLS = [
  { id: 'OIL-NWIS-02', name: 'OIL-NWIS-02', distanceKm: 1.8, hazard: 'Kick at 3,118 m', status: 'critical' as const, lat: 58.421, lon: 1.854, current_depth_m: 3185, current_formation: 'Northwind Sandstone', total_depth_m: 3410 },
  { id: 'OIL-NWIS-03', name: 'OIL-NWIS-03', distanceKm: 3.1, hazard: 'Stuck Pipe at 3,096 m', status: 'warning' as const, lat: 58.396, lon: 1.831, current_depth_m: 3260, current_formation: 'Northwind Sandstone', total_depth_m: 3408 },
  { id: 'OIL-NWIS-04', name: 'OIL-NWIS-04', distanceKm: 4.7, hazard: 'Mud Loss at 3,172 m', status: 'warning' as const, lat: 58.438, lon: 1.816, current_depth_m: 3340, current_formation: 'Northwind Sandstone', total_depth_m: 3425 },
];

export const OFFSET_EVIDENCE = [
  { well: 'OIL-NWIS-02', incident: 'Kick / influx', depthM: 3118, detail: 'Pit gain and flow after pumps-off in Northwind Sandstone.' },
  { well: 'OIL-NWIS-03', incident: 'Stuck Pipe', depthM: 3096, detail: 'String stuck across a shale streak in the correlated interval.' },
];
