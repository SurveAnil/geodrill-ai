'use client';

import React from 'react';
import { MapContainer, TileLayer, Circle, CircleMarker, Tooltip, Popup } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import { OFFSET_WELLS, OffsetWellItem } from './OffsetRadarTable';

const ACTIVE_RIG_COORDS: [number, number] = [16.245, 82.352];

interface WellMapProps {
  selectedWell?: OffsetWellItem | null;
  wells?: OffsetWellItem[];
}

export const WellMap: React.FC<WellMapProps> = ({ selectedWell, wells = OFFSET_WELLS }) => {
  return (
    <div className="w-full h-full min-h-[260px] relative rounded-lg overflow-hidden border border-slate-800 bg-[#090D16]">
      <MapContainer
        center={ACTIVE_RIG_COORDS}
        zoom={11}
        scrollWheelZoom={false}
        className="w-full h-full z-10"
        style={{ background: '#090D16' }}
      >
        {/* CartoDB Dark Matter Tile Layer */}
        <TileLayer
          attribution='&copy; <a href="https://carto.com/">CARTO</a>'
          url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
          maxZoom={19}
        />

        {/* 10 km Radius Safe/Correlation Zone */}
        <Circle
          center={ACTIVE_RIG_COORDS}
          radius={10000}
          pathOptions={{
            color: '#06B6D4',
            fillColor: '#0891B2',
            fillOpacity: 0.07,
            weight: 1.5,
            dashArray: '6, 6',
          }}
        >
          <Tooltip direction="top" opacity={0.9} permanent={false}>
            <span className="text-xs font-mono">10.0 km Correlation Radius</span>
          </Tooltip>
        </Circle>

        {/* Active Rig: Pulsating Core & Outer Ring */}
        <CircleMarker
          center={ACTIVE_RIG_COORDS}
          radius={14}
          pathOptions={{
            color: '#38BDF8',
            fillColor: '#0284C7',
            fillOpacity: 0.25,
            weight: 1,
          }}
        />
        <CircleMarker
          center={ACTIVE_RIG_COORDS}
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
              🎯 ACTIVE RIG (15/9-F-11B)
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
