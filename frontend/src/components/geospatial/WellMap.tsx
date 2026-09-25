'use client';

import React, { useEffect } from 'react';
import { MapContainer, TileLayer, Circle, CircleMarker, Tooltip, Popup, useMap } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import { OffsetWellItem } from './OffsetRadarTable';

interface WellMapProps {
  selectedWell?: OffsetWellItem | null;
  wells?: OffsetWellItem[];
  activeCoordinates?: [number, number];
  activeWellId?: string;
  radiusKm?: number;
}

const MapSizeSynchronizer: React.FC = () => {
  const map = useMap();

  useEffect(() => {
    const invalidate = () => map.invalidateSize({ pan: false });
    const frame = window.requestAnimationFrame(invalidate);
    const container = map.getContainer();
    const observer = new ResizeObserver(invalidate);
    observer.observe(container);

    return () => {
      window.cancelAnimationFrame(frame);
      observer.disconnect();
    };
  }, [map]);

  return null;
};

export const WellMap: React.FC<WellMapProps> = ({
  selectedWell,
  wells = [],
  activeCoordinates = [58.4121, 1.8422],
  activeWellId = 'OIL-NWIS-01',
  radiusKm = 10,
}) => {
  const cartoApiKey = process.env.NEXT_PUBLIC_CARTO_API_KEY?.trim();
  const cartoTileUrl = cartoApiKey
    ? `https://basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}.png?key=${encodeURIComponent(cartoApiKey)}`
    : undefined;

  return (
    <div className="w-full h-full min-h-[260px] relative rounded-lg overflow-hidden border border-slate-800 bg-[#090D16]">
      <MapContainer
        center={activeCoordinates}
        zoom={11}
        scrollWheelZoom={false}
        className="w-full h-full z-10"
        style={{ background: '#090D16' }}
      >
        <MapSizeSynchronizer />
        {cartoTileUrl && (
          <TileLayer
            attribution='&copy; <a href="https://carto.com/">CARTO</a>'
            url={cartoTileUrl}
            maxZoom={19}
          />
        )}

        {/* Radius Safe/Correlation Zone */}
        <Circle
          center={activeCoordinates}
          radius={radiusKm * 1000}
          pathOptions={{
            color: '#06B6D4',
            fillColor: '#0891B2',
            fillOpacity: 0.07,
            weight: 1.5,
            dashArray: '6, 6',
          }}
        >
          <Tooltip direction="top" opacity={0.9} permanent={false}>
            <span className="text-xs font-mono">{radiusKm.toFixed(1)} km Correlation Radius</span>
          </Tooltip>
        </Circle>

        {/* Active Rig: Pulsating Core & Outer Ring */}
        <CircleMarker
          center={activeCoordinates}
          radius={14}
          pathOptions={{
            color: '#38BDF8',
            fillColor: '#0284C7',
            fillOpacity: 0.25,
            weight: 1,
          }}
        />
        <CircleMarker
          center={activeCoordinates}
          radius={7}
          pathOptions={{
            color: '#FFFFFF',
            fillColor: '#0EA5E9',
            fillOpacity: 1,
            weight: 2,
          }}
        >
          <Tooltip direction="top" offset={[0, -10]} opacity={0.95} permanent>
            <div className="bg-[#0B1120] text-slate-100 p-1 rounded border border-cyan-500/80 font-mono text-[11px] font-bold shadow-lg">
              🎯 ACTIVE WELL ({activeWellId})
            </div>
          </Tooltip>
        </CircleMarker>

        {/* Offset Wells */}
        {wells.map((well) => {
          const isSelected = selectedWell?.id === well.id;
          const color =
            well.status === 'critical'
              ? '#EF4444'
              : well.status === 'warning'
              ? '#F59E0B'
              : '#10B981';

          return (
            <CircleMarker
              key={well.id}
              center={[well.lat, well.lon]}
              radius={isSelected ? 10 : 7}
              pathOptions={{
                color: isSelected ? '#FFFFFF' : color,
                fillColor: color,
                fillOpacity: 0.9,
                weight: isSelected ? 3 : 1.5,
              }}
            >
              <Tooltip direction="top" offset={[0, -8]} opacity={0.95}>
                <div className="bg-[#0F172A] text-slate-100 p-1.5 rounded border border-slate-700 shadow-xl font-sans text-xs min-w-[140px]">
                  <div className="font-bold text-white font-mono flex items-center justify-between">
                    <span>{well.name}</span>
                    <span className="text-[10px] text-cyan-400 font-normal">{well.distanceKm} km</span>
                  </div>
                  <div className="text-[10px] text-slate-300 mt-0.5">{well.hazard}</div>
                </div>
              </Tooltip>
              <Popup>
                <div className="p-1 text-slate-900 text-xs font-sans">
                  <strong>{well.name}</strong>
                  <br />
                  Distance: {well.distanceKm} km
                  <br />
                  Hazard: {well.hazard}
                </div>
              </Popup>
            </CircleMarker>
          );
        })}
      </MapContainer>

      {!cartoTileUrl && <div className="absolute bottom-9 right-2 z-[400] rounded border border-amber-700/70 bg-[#0B1120]/95 px-2 py-1 text-[10px] text-amber-200 shadow-md">Basemap unavailable — demo mode</div>}

      {/* Map Legend Overlay */}
      <div className="absolute bottom-2 left-2 z-[400] bg-[#0B1120]/90 border border-slate-800/90 rounded px-2 py-1 text-[10px] font-mono text-slate-400 flex items-center gap-3 backdrop-blur-sm shadow-md">
        <span className="flex items-center gap-1 text-cyan-300">
          <span className="h-2 w-2 rounded-full bg-cyan-400" /> Active Rig
        </span>
        <span className="flex items-center gap-1 text-red-400">
          <span className="h-2 w-2 rounded-full bg-red-500" /> Critical
        </span>
        <span className="flex items-center gap-1 text-amber-400">
          <span className="h-2 w-2 rounded-full bg-amber-500" /> Warning
        </span>
        <span className="flex items-center gap-1 text-emerald-400">
          <span className="h-2 w-2 rounded-full bg-emerald-500" /> Safe
        </span>
      </div>
    </div>
  );
};
