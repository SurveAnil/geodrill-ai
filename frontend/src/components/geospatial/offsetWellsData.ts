import { OffsetWellFeature, HistoricalEvent, WellFiltersState } from './types';
import { DEMO_WELL_FIELD_NAME, DEMO_WELL_LOCATIONS } from '@/lib/demoWellLocations';

// Active Well Anchor: OIL-NWIS-01
export const ACTIVE_WELL_ANCHOR = {
  wellId: 'OIL-NWIS-01',
  name: 'OIL-NWIS-01',
  lat: DEMO_WELL_LOCATIONS['OIL-NWIS-01'].lat,
  lon: DEMO_WELL_LOCATIONS['OIL-NWIS-01'].lon,
  measuredDepthM: 3108.0,
  trueVerticalDepthM: 3032.0,
  formation: 'Northwind Sandstone',
  status: 'DRILLING / DEMO' as const,
  field: DEMO_WELL_FIELD_NAME,
  operator: 'Orion Inlet Limited',
};

export function isValidGeoCoordinate(lat: number, lon: number): boolean {
  return Number.isFinite(lat) && Number.isFinite(lon) && lat >= -90 && lat <= 90 && lon >= -180 && lon <= 180;
}

// 10 Seeding Demo Offset Wells distributed across 1 to 10 km around active rig
export const SEEDED_OFFSET_WELLS: OffsetWellFeature[] = [
  {
    id: 'OIL-NWIS-02',
    wellId: 'OIL-NWIS-02',
    name: 'OIL-NWIS-02',
    lat: DEMO_WELL_LOCATIONS['OIL-NWIS-02'].lat,
    lon: DEMO_WELL_LOCATIONS['OIL-NWIS-02'].lon,
    distanceKm: 0.8,
    direction: '0.8 km NE',
    formation: 'Northwind Sandstone',
    status: 'Completed',
    riskLevel: 'high',
    totalDepthM: 3684,
    spudDate: '12 Apr 2020',
    completionDate: '28 Aug 2020',
    reservoir: 'NW Field',
    trajectory: 'Directional',
    nptHours: 42.5,
    hazardSummary: 'Gas Kick at 3,142m & High Torque',
    historicalEvents: [
      {
        id: 'ev-02-1',
        type: 'Gas Kick',
        depthInterval: '3,142–3,156 m',
        severity: 'high',
        description: 'Increase in gas, pit gain 14 bbl, well control shut-in applied, influx circulated out via choke manifold.',
        nptHours: 18.0,
      },
      {
        id: 'ev-02-2',
        type: 'High Torque',
        depthInterval: '3,165–3,320 m',
        severity: 'medium',
        description: 'Severe torque fluctuation (>24 kft-lb) while rotating through abrasive sandstone streaks. ROP reduced to 4 m/hr.',
        nptHours: 6.5,
      },
      {
        id: 'ev-02-3',
        type: 'Stuck Pipe',
        depthInterval: '3,300–3,342 m',
        severity: 'high',
        description: 'Differential sticking across depleted permeable sand streak. 42 hrs NPT total. Resolved with acid spot and jar firing.',
        nptHours: 18.0,
      },
    ],
    lessonsLearned: [
      'Pre-weight mud to 1.42 SG before entering Northwind Sandstone at 3,120 m.',
      'Keep drill string moving continuously; limit static connection times to under 3 minutes across permeable sands.',
      'Monitor background gas trends; perform flow check on every drill break.',
    ],
    operator: 'Orion Inlet Limited',
    field_name: DEMO_WELL_FIELD_NAME,
    current_depth_m: 3684,
    current_formation: 'Northwind Sandstone',
    total_depth_m: 3684,
  },
  {
    id: 'OIL-NWIS-03',
    wellId: 'OIL-NWIS-03',
    name: 'OIL-NWIS-03',
    lat: DEMO_WELL_LOCATIONS['OIL-NWIS-03'].lat,
    lon: DEMO_WELL_LOCATIONS['OIL-NWIS-03'].lon,
    distanceKm: 1.8,
    direction: '1.8 km SW',
    formation: 'Northwind Sandstone',
    status: 'Completed',
    riskLevel: 'high',
    totalDepthM: 3408,
    spudDate: '18 Jun 2019',
    completionDate: '05 Nov 2019',
    reservoir: 'NW Field',
    trajectory: 'Directional',
    nptHours: 36.0,
    hazardSummary: 'Stuck Pipe at 3,096m & Mud Loss',
    historicalEvents: [
      {
        id: 'ev-03-1',
        type: 'Stuck Pipe',
        depthInterval: '3,096–3,120 m',
        severity: 'high',
        description: 'Mechanical pipe sticking across interbedded shale streak. Jars fired 140 times to free string.',
        nptHours: 26.0,
      },
      {
        id: 'ev-03-2',
        type: 'Mud Loss',
        depthInterval: '3,210–3,245 m',
        severity: 'medium',
        description: 'Partial mud losses of 35 bbl/hr in micro-fractured zone. LCM pill pumped.',
        nptHours: 10.0,
      },
    ],
    lessonsLearned: [
      'Perform short wiper trips every 90 m through reactive shale intervals.',
      'Maintain LCM inventory on surface when drilling below 3,050 m.',
    ],
    operator: 'Orion Inlet Limited',
    field_name: DEMO_WELL_FIELD_NAME,
    current_depth_m: 3408,
    current_formation: 'Northwind Sandstone',
    total_depth_m: 3408,
  },
  {
    id: 'OIL-NWIS-04',
    wellId: 'OIL-NWIS-04',
    name: 'OIL-NWIS-04',
    lat: DEMO_WELL_LOCATIONS['OIL-NWIS-04'].lat,
    lon: DEMO_WELL_LOCATIONS['OIL-NWIS-04'].lon,
    distanceKm: 3.3,
    direction: '3.3 km N',
    formation: 'Barail Coal',
    status: 'Completed',
    riskLevel: 'medium',
    totalDepthM: 3425,
    spudDate: '04 Jan 2021',
    completionDate: '19 May 2021',
    reservoir: 'Central Block',
    trajectory: 'Vertical',
    nptHours: 14.0,
    hazardSummary: 'Mud Loss at 3,172m (Cleat Fractures)',
    historicalEvents: [
      {
        id: 'ev-04-1',
        type: 'Mud Loss',
        depthInterval: '3,172–3,190 m',
        severity: 'medium',
        description: 'Seepage losses (20 bbl/hr) across fractured coal cleat network.',
        nptHours: 8.0,
      },
      {
        id: 'ev-04-2',
        type: 'High Torque',
        depthInterval: '2,980–3,050 m',
        severity: 'low',
        description: 'Elevated drag on trips; hole cleaning sweeps optimized with high-vis pills.',
        nptHours: 6.0,
      },
    ],
    lessonsLearned: [
      'Optimize flow rates to 800 GPM for effective hole cleaning in coal intervals.',
      'Treat mud system with graphite LCM prior to drilling coal seams.',
    ],
    operator: 'Orion Inlet Limited',
    field_name: DEMO_WELL_FIELD_NAME,
    current_depth_m: 3425,
    current_formation: 'Barail Coal',
    total_depth_m: 3425,
  },
  {
    id: 'OIL-NWIS-05',
    wellId: 'OIL-NWIS-05',
    name: 'OIL-NWIS-05',
    lat: DEMO_WELL_LOCATIONS['OIL-NWIS-05'].lat,
    lon: DEMO_WELL_LOCATIONS['OIL-NWIS-05'].lon,
    distanceKm: 4.7,
    direction: '4.7 km W',
    formation: 'Tipam Formation',
    status: 'Completed',
    riskLevel: 'low',
    totalDepthM: 3250,
    spudDate: '14 Sep 2021',
    completionDate: '22 Dec 2021',
    reservoir: 'West Flank',
    trajectory: 'S-Type',
    nptHours: 4.0,
    hazardSummary: 'Minor Stick-Slip at 2,750m',
    historicalEvents: [
      {
        id: 'ev-05-1',
        type: 'High Torque',
        depthInterval: '2,750–2,810 m',
        severity: 'low',
        description: 'Minor stick-slip mitigated by adjusting RPM from 110 to 135.',
        nptHours: 4.0,
      },
    ],
    lessonsLearned: [
      'Maintain steady RPM and drill with positive pulse MWD tools.',
    ],
    operator: 'Orion Inlet Limited',
    field_name: DEMO_WELL_FIELD_NAME,
    current_depth_m: 3250,
    current_formation: 'Tipam Formation',
    total_depth_m: 3250,
  },
  {
    id: 'OIL-NWIS-06',
    wellId: 'OIL-NWIS-06',
    name: 'OIL-NWIS-06',
    lat: DEMO_WELL_LOCATIONS['OIL-NWIS-06'].lat,
    lon: DEMO_WELL_LOCATIONS['OIL-NWIS-06'].lon,
    distanceKm: 6.4,
    direction: '6.4 km NE',
    formation: 'Northwind Sandstone',
    status: 'Completed',
    riskLevel: 'high',
    totalDepthM: 3590,
    spudDate: '02 Mar 2022',
    completionDate: '15 Jul 2022',
    reservoir: 'NW Field',
    trajectory: 'Directional',
    nptHours: 28.5,
    hazardSummary: 'Gas Kick at 3,130m & Squeeze Cement',
    historicalEvents: [
      {
        id: 'ev-06-1',
        type: 'Gas Kick',
        depthInterval: '3,130–3,148 m',
        severity: 'high',
        description: '10 bbl influx detected via automated PVT trip tank alarm. Circulated out safely.',
        nptHours: 19.5,
      },
      {
        id: 'ev-06-2',
        type: 'Cementing',
        depthInterval: '3,590 m',
        severity: 'medium',
        description: 'Poor bond log across gas cap zone required remedial squeeze cementing.',
        nptHours: 9.0,
      },
    ],
    lessonsLearned: [
      'Use expandable gas-tight cement slurry across hydrocarbon pay zone.',
      'Calibrate automated kick detection sensors before entering target sand.',
    ],
    operator: 'Orion Inlet Limited',
    field_name: DEMO_WELL_FIELD_NAME,
    current_depth_m: 3590,
    current_formation: 'Northwind Sandstone',
    total_depth_m: 3590,
  },
  {
    id: 'OIL-NWIS-07',
    wellId: 'OIL-NWIS-07',
    name: 'OIL-NWIS-07',
    lat: DEMO_WELL_LOCATIONS['OIL-NWIS-07'].lat,
    lon: DEMO_WELL_LOCATIONS['OIL-NWIS-07'].lon,
    distanceKm: 9.2,
    direction: '9.2 km S',
    formation: 'Girujan Clay',
    status: 'Drilling',
    riskLevel: 'medium',
    totalDepthM: 3150,
    spudDate: '10 Aug 2024',
    completionDate: 'Active Operations',
    reservoir: 'South Extension',
    trajectory: 'Vertical',
    nptHours: 12.0,
    hazardSummary: 'Fault Loss (60 bbl) at 2,640m',
    historicalEvents: [
      {
        id: 'ev-07-1',
        type: 'Mud Loss',
        depthInterval: '2,640–2,680 m',
        severity: 'medium',
        description: 'Loss of circulation (60 bbl total) into natural fault plane.',
        nptHours: 12.0,
      },
    ],
    lessonsLearned: [
      'Reduce pump rate to 500 GPM when approaching seismic fault hazard planes.',
    ],
    operator: 'Orion Inlet Limited',
    field_name: DEMO_WELL_FIELD_NAME,
    current_depth_m: 2980,
    current_formation: 'Girujan Clay',
    total_depth_m: 3150,
  },
  {
    id: 'OIL-NWIS-08',
    wellId: 'OIL-NWIS-08',
    name: 'OIL-NWIS-08',
    lat: DEMO_WELL_LOCATIONS['OIL-NWIS-08'].lat,
    lon: DEMO_WELL_LOCATIONS['OIL-NWIS-08'].lon,
    distanceKm: 14.0,
    direction: '14.0 km NNW',
    formation: 'Northwind Sandstone',
    status: 'Completed',
    riskLevel: 'high',
    totalDepthM: 3720,
    spudDate: '15 Oct 2018',
    completionDate: '28 Feb 2019',
    reservoir: 'North Dome',
    trajectory: 'Directional',
    nptHours: 52.0,
    hazardSummary: 'Major Kick (22 bbl) & Stuck Logging',
    historicalEvents: [
      {
        id: 'ev-08-1',
        type: 'Gas Kick',
        depthInterval: '3,150–3,168 m',
        severity: 'high',
        description: 'Major gas kick (22 bbl gain) with 450 psi SICP. Driller method kill performed.',
        nptHours: 38.0,
      },
      {
        id: 'ev-08-2',
        type: 'Stuck Pipe',
        depthInterval: '3,410–3,450 m',
        severity: 'medium',
        description: 'Differential pressure sticking during logging run. Wireline severed and fished.',
        nptHours: 14.0,
      },
    ],
    lessonsLearned: [
      'Maintain weighted mud reserve of 1,200 bbl ready in active pits.',
      'Apply pipe wiper lubrication before running wireline in over-gauge sections.',
    ],
    operator: 'Orion Inlet Limited',
    field_name: DEMO_WELL_FIELD_NAME,
    current_depth_m: 3720,
    current_formation: 'Northwind Sandstone',
    total_depth_m: 3720,
  },
  {
    id: 'OIL-NWIS-09',
    wellId: 'OIL-NWIS-09',
    name: 'OIL-NWIS-09',
    lat: DEMO_WELL_LOCATIONS['OIL-NWIS-09'].lat,
    lon: DEMO_WELL_LOCATIONS['OIL-NWIS-09'].lon,
    distanceKm: 27.0,
    direction: '27.0 km SSW',
    formation: 'Tipam Formation',
    status: 'Abandoned',
    riskLevel: 'low',
    totalDepthM: 2980,
    spudDate: '05 May 2017',
    completionDate: '12 Aug 2017',
    reservoir: 'South Flank',
    trajectory: 'Vertical',
    nptHours: 0.0,
    hazardSummary: 'Dry well, plugged & abandoned smoothly',
    historicalEvents: [],
    lessonsLearned: [
      'Standard drilling operations conducted without non-productive time.',
    ],
    operator: 'Orion Inlet Limited',
    field_name: DEMO_WELL_FIELD_NAME,
    current_depth_m: 2980,
    current_formation: 'Tipam Formation',
    total_depth_m: 2980,
  },
  {
    id: 'OIL-NWIS-10',
    wellId: 'OIL-NWIS-10',
    name: 'OIL-NWIS-10',
    lat: DEMO_WELL_LOCATIONS['OIL-NWIS-10'].lat,
    lon: DEMO_WELL_LOCATIONS['OIL-NWIS-10'].lon,
    distanceKm: 42.0,
    direction: '42.0 km E',
    formation: 'Barail Coal',
    status: 'Completed',
    riskLevel: 'medium',
    totalDepthM: 3510,
    spudDate: '11 Nov 2022',
    completionDate: '20 Mar 2023',
    reservoir: 'East Ridge',
    trajectory: 'Directional',
    nptHours: 16.5,
    hazardSummary: 'Keyseating & Dogleg Drag at 3,110m',
    historicalEvents: [
      {
        id: 'ev-10-1',
        type: 'High Torque',
        depthInterval: '3,110–3,200 m',
        severity: 'medium',
        description: 'Severe keyseating in dogleg interval caused high drag and drill string stalls.',
        nptHours: 16.5,
      },
    ],
    lessonsLearned: [
      'Control dogleg severity to <3.0 deg/30m when steering towards East Ridge targets.',
    ],
    operator: 'Orion Inlet Limited',
    field_name: DEMO_WELL_FIELD_NAME,
    current_depth_m: 3510,
    current_formation: 'Barail Coal',
    total_depth_m: 3510,
  },
];

export function calculateHaversineKm(
  fromLat: number,
  fromLon: number,
  toLat: number,
  toLon: number
): number {
  const earthRadiusKm = 6371;
  const dLat = ((toLat - fromLat) * Math.PI) / 180;
  const dLon = ((toLon - fromLon) * Math.PI) / 180;
  const lat1 = (fromLat * Math.PI) / 180;
  const lat2 = (toLat * Math.PI) / 180;
  const a =
    Math.sin(dLat / 2) ** 2 +
    Math.cos(lat1) * Math.cos(lat2) * Math.sin(dLon / 2) ** 2;
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
  return Math.round(earthRadiusKm * c * 10) / 10;
}

export function filterWells(
  wells: OffsetWellFeature[],
  filters: WellFiltersState,
  radiusKm: number,
  activeLocation = { lat: ACTIVE_WELL_ANCHOR.lat, lon: ACTIVE_WELL_ANCHOR.lon }
): OffsetWellFeature[] {
  return wells
    .filter((well) => isValidGeoCoordinate(well.lat, well.lon))
    .map((well) => {
      const liveDistance = calculateHaversineKm(
        activeLocation.lat,
        activeLocation.lon,
        well.lat,
        well.lon
      );
      return {
        ...well,
        distanceKm: liveDistance > 0 ? liveDistance : well.distanceKm,
      };
    })
    .filter((well) => {
      // Radius constraint
      if (well.distanceKm > radiusKm) return false;

      // Formation constraint
      if (filters.formation && filters.formation !== 'All' && filters.formation !== 'All Formations') {
        if (well.formation.toLowerCase() !== filters.formation.toLowerCase()) return false;
      }

      // Risk level constraint
      if (filters.riskLevel && filters.riskLevel !== 'All' && filters.riskLevel !== 'All Risk Levels') {
        if (well.riskLevel.toLowerCase() !== filters.riskLevel.toLowerCase()) return false;
      }

      // Event type constraint
      if (filters.eventType && filters.eventType !== 'All' && filters.eventType !== 'All Events') {
        const matchesEvent = well.historicalEvents.some((ev) =>
          ev.type.toLowerCase().includes(filters.eventType.toLowerCase())
        );
        if (!matchesEvent) return false;
      }

      // Well status constraint
      if (filters.wellStatus && filters.wellStatus !== 'All' && filters.wellStatus !== 'All Status') {
        if (well.status.toLowerCase() !== filters.wellStatus.toLowerCase()) return false;
      }

      return true;
    });
}

// Generates a smooth geodesic polygon for the search radius
export function createGeodesicRadiusGeoJSON(
  centerLon: number,
  centerLat: number,
  radiusKm: number,
  points = 64
) {
  const coords: [number, number][] = [];
  const distanceRadians = radiusKm / 6371;
  const centerLatRad = (centerLat * Math.PI) / 180;
  const centerLonRad = (centerLon * Math.PI) / 180;

  for (let i = 0; i <= points; i++) {
    const angle = (i * 2 * Math.PI) / points;
    const latRad = Math.asin(
      Math.sin(centerLatRad) * Math.cos(distanceRadians) +
        Math.cos(centerLatRad) * Math.sin(distanceRadians) * Math.cos(angle)
    );
    const lonRad =
      centerLonRad +
      Math.atan2(
        Math.sin(angle) * Math.sin(distanceRadians) * Math.cos(centerLatRad),
        Math.cos(distanceRadians) - Math.sin(centerLatRad) * Math.sin(latRad)
      );
    coords.push([(lonRad * 180) / Math.PI, (latRad * 180) / Math.PI]);
  }

  return {
    type: 'FeatureCollection' as const,
    features: [
      {
        type: 'Feature' as const,
        geometry: {
          type: 'Polygon' as const,
          coordinates: [coords],
        },
        properties: { radiusKm },
      },
    ],
  };
}

// Converts well features into a standard GeoJSON FeatureCollection
export function wellsToGeoJSON(wells: OffsetWellFeature[]) {
  return {
    type: 'FeatureCollection' as const,
    features: wells.filter((well) => isValidGeoCoordinate(well.lat, well.lon)).map((well) => ({
      type: 'Feature' as const,
      id: well.id,
      geometry: {
        type: 'Point' as const,
        coordinates: [well.lon, well.lat] as [number, number],
      },
      properties: {
        id: well.id,
        wellId: well.wellId,
        name: well.name,
        distanceKm: well.distanceKm,
        direction: well.direction,
        formation: well.formation,
        status: well.status,
        riskLevel: well.riskLevel,
        hazardSummary: well.hazardSummary,
        eventCount: well.historicalEvents.length,
      },
    })),
  };
}
