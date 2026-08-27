'use client';

import React, { useState } from 'react';
import dynamic from 'next/dynamic';
import { MapPin, Compass, Radio } from 'lucide-react';
import { OffsetRadarTable, OffsetWellItem } from './OffsetRadarTable';

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
          <span>16.245° N, 82.352° E</span>
        </div>
      </div>

      {/* Interactive GIS Map Container */}
      <div className="flex-1 min-h-[260px] max-h-[340px]">
        <DynamicWellMap selectedWell={selectedWell} />
      </div>

      {/* Offset Wells Radar Table */}
      <div className="mt-1">
        <OffsetRadarTable
          selectedWellId={selectedWell?.id}
          onSelectWell={(well) => setSelectedWell((prev) => (prev?.id === well.id ? null : well))}
        />
      </div>

      {/* Footer Meta */}
      <div className="text-[11px] text-slate-500 border-t border-slate-800/60 pt-2 font-mono flex items-center justify-between">
        <span className="flex items-center gap-1">
          <Radio className="w-3 h-3 text-cyan-400 animate-pulse" />
          <span>Haversine Spatial Index</span>
        </span>
        <span className="text-cyan-400 font-semibold">Layer 4 Knowledge Store</span>
      </div>
    </div>
  );
};
