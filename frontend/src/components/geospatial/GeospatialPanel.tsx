'use client';

import React, { useEffect, useState } from 'react';
import dynamic from 'next/dynamic';
import { MapPin, Compass, Radio } from 'lucide-react';
import { OffsetRadarTable, OffsetWellItem } from './OffsetRadarTable';
import { apiClient, NearbyWell } from '@/lib/api';
import { useDrillStore } from '@/store/useDrillStore';

// Dynamically import WellMap to bypass SSR for Leaflet window dependencies
const DynamicWellMap = dynamic(
  () => import('./WellMap').then((mod) => mod.WellMap),
  {
    ssr: false,
    loading: () => (
      <div className="w-full h-full min-h-[260px] rounded-lg border border-slate-800 bg-[#090D16] flex flex-col items-center justify-center gap-2 text-slate-500 text-xs font-mono">
        <div className="h-6 w-6 rounded-full border-2 border-cyan-500 border-t-transparent animate-spin" />
        <span>Initializing GIS Radar Canvas...</span>
      </div>
    ),
  }
);

export const GeospatialPanel: React.FC = () => {
  const [selectedWell, setSelectedWell] = useState<OffsetWellItem | null>(null);
  const [wells, setWells] = useState<OffsetWellItem[]>([]);
  const [apiUnavailable, setApiUnavailable] = useState(false);
  const [radiusKm, setRadiusKm] = useState(10);
  const [loaded, setLoaded] = useState(false);
  const { activeWellId, activeWellLocation, setActiveWellContext } = useDrillStore();
  useEffect(() => {
    setLoaded(false);
    setApiUnavailable(false);
    apiClient.nearbyWells(activeWellLocation.latitude, activeWellLocation.longitude, radiusKm, activeWellId).then((items) => {
      const mapped = items.map((item: NearbyWell, index): OffsetWellItem => ({
        id: item.well_id || `well-${index}`, name: item.well_id || item.name || 'Unknown well',
        distanceKm: Number(item.distance_km), hazard: item.hazard || 'Historical events available',
        status: item.status === 'critical' ? 'critical' : ['high', 'warning', 'medium'].includes(item.status || '') ? 'warning' : 'safe',
        lat: Number(item.latitude), lon: Number(item.longitude),
        operator: item.operator,
        field_name: item.field_name,
        current_depth_m: item.current_depth_m,
        current_formation: item.current_formation,
        total_depth_m: item.total_depth_m,
      })).filter((item) => Number.isFinite(item.lat) && Number.isFinite(item.lon));
      setWells(mapped);
      setLoaded(true);
    }).catch(() => { setWells([]); setApiUnavailable(true); setLoaded(true); });
  }, [activeWellId, activeWellLocation.latitude, activeWellLocation.longitude, radiusKm]);
  const displayedWells = wells;

  return (
    <div className="flex flex-col h-full gap-3">
      {/* Panel Header */}
      <div className="flex items-center justify-between pb-2.5 border-b border-slate-800">
        <div className="flex items-center gap-2 text-xs font-semibold text-slate-200">
          <MapPin className="w-4 h-4 text-cyan-400" />
          <span>Geospatial Radar & GIS</span>
        </div>
        <div className="flex items-center gap-2 text-[10px] font-mono text-slate-400">
          <Compass className="w-3 h-3 text-cyan-500" />
          <span>{activeWellLocation.latitude.toFixed(3)}° N, {activeWellLocation.longitude.toFixed(3)}° E</span>
          <label className="flex items-center gap-1">
            Radius
            <select value={radiusKm} onChange={(event) => setRadiusKm(Number(event.target.value))} className="rounded bg-[#090D16] px-1 py-0.5 text-cyan-300">
              {[5, 10, 25, 50].map((value) => <option key={value} value={value}>{value} km</option>)}
            </select>
          </label>
        </div>
      </div>

      {/* Interactive GIS Map Container */}
      <div className="h-[260px] w-full shrink-0">
        <DynamicWellMap
          selectedWell={selectedWell}
          wells={displayedWells}
          activeCoordinates={[activeWellLocation.latitude, activeWellLocation.longitude]}
          activeWellId={activeWellId}
          radiusKm={radiusKm}
        />
      </div>

      {/* Offset Wells Radar Table */}
      <div className="mt-1">
        {!loaded ? <p className="rounded-lg border border-slate-800 p-4 text-xs text-slate-500">Loading nearby wells from backend…</p> :
          apiUnavailable ? <p className="rounded-lg border border-amber-800/60 bg-amber-950/20 p-4 text-xs text-amber-300">Nearby-well service unavailable. No operational offset values are shown.</p> :
          !displayedWells.length ? <p className="rounded-lg border border-slate-800 p-4 text-xs text-slate-500">No nearby wells returned for this active-well location.</p> :
          <OffsetRadarTable
            selectedWellId={selectedWell?.id}
            radiusKm={radiusKm}
            onSelectWell={(well) => {
              setSelectedWell((prev) => (prev?.id === well.id ? null : well));
              setActiveWellContext({
                well_id: well.id,
                latitude: well.lat,
                longitude: well.lon,
                current_depth_m: well.current_depth_m,
                current_formation: well.current_formation,
                operator: well.operator,
                field_name: well.field_name,
                total_depth_m: well.total_depth_m,
              });
            }}
            wells={displayedWells}
          />}
      </div>

      {/* Footer Meta */}
      <div className="text-[11px] text-slate-500 border-t border-slate-800/60 pt-2 font-mono flex items-center justify-between">
        <span className="flex items-center gap-1">
          <Radio className="w-3 h-3 text-cyan-400 animate-pulse" />
          <span>Haversine Spatial Index</span>
        </span>
         <span className={apiUnavailable ? 'text-amber-400' : 'text-cyan-400'}>{apiUnavailable ? 'Backend unavailable — no fallback data' : 'Backend canonical data'}</span>
      </div>
    </div>
  );
};
