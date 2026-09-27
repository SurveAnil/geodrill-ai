'use client';

import React from 'react';
import { Radar, Compass } from 'lucide-react';
import { OffsetWellFeature, WellFiltersState } from './types';
import { WellListItem } from './WellListItem';
import { WellFilters } from './WellFilters';
import { WellDetailPanel } from './WellDetailPanel';

interface NearbyWellsPanelProps {
  wells: OffsetWellFeature[];
  totalInRadius: number;
  selectedWell: OffsetWellFeature | null;
  onSelectWell: (well: OffsetWellFeature | null) => void;
  radiusKm: number;
  onRadiusChange: (radiusKm: number) => void;
  filters: WellFiltersState;
  onFiltersChange: (filters: WellFiltersState) => void;
  onResetFilters: () => void;
}

const RADIUS_OPTIONS = [1, 2, 5, 10, 25, 50];

export const NearbyWellsPanel: React.FC<NearbyWellsPanelProps> = ({
  wells,
  totalInRadius,
  selectedWell,
  onSelectWell,
  radiusKm,
  onRadiusChange,
  filters,
  onFiltersChange,
  onResetFilters,
}) => {
  return (
    <div className="flex h-full flex-col overflow-hidden rounded-xl border border-slate-800 bg-[#0F172A] shadow-xl">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-slate-800 bg-[#162032] p-3.5">
        <div className="flex items-center gap-2">
          <Radar className="h-4 w-4 text-cyan-400 animate-pulse" />
          <h3 className="font-semibold text-xs text-white">Nearby Offset Wells</h3>
        </div>
        <span className="rounded-full border border-cyan-500/30 bg-cyan-950/50 px-2 py-0.5 font-mono text-[10px] font-semibold text-cyan-300">
          {wells.length} Displayed • {totalInRadius} in Radius
        </span>
      </div>

      <div className="shrink-0 p-3 pb-0">
        {/* Radius Selector */}
        <div className="rounded-lg border border-slate-800 bg-[#090D16] p-2.5">
          <div className="flex items-center justify-between text-xs text-slate-300 mb-1.5">
            <span className="font-mono text-[10px] uppercase text-slate-400">Search Radius</span>
            <span className="font-mono text-cyan-400 font-bold">{radiusKm} km</span>
          </div>
          <div className="grid grid-cols-6 gap-1">
            {RADIUS_OPTIONS.map((r) => {
              const active = radiusKm === r;
              return (
                <button
                  key={r}
                  onClick={() => onRadiusChange(r)}
                  className={`rounded py-1 text-center font-mono text-[11px] font-semibold transition ${
                    active
                      ? 'border border-cyan-500 bg-cyan-500/20 text-cyan-300 shadow-sm'
                      : 'border border-slate-800 bg-slate-900 text-slate-400 hover:border-slate-700 hover:text-white'
                  }`}
                >
                  {r}k
                </button>
              );
            })}
          </div>
        </div>

        {/* Filters */}
        <WellFilters
          filters={filters}
          onChange={onFiltersChange}
          onReset={onResetFilters}
          totalFiltered={wells.length}
          totalAvailable={totalInRadius}
        />

      </div>

      <div data-offset-well-list className="min-h-0 flex-1 overflow-y-auto p-3 pt-2">
        {selectedWell ? (
          <WellDetailPanel
            well={selectedWell}
            onClose={() => onSelectWell(null)}
            embedded
          />
        ) : (
        <div className="space-y-2">
          <div className="flex items-center justify-between text-[11px] text-slate-400 font-mono">
            <span>OFFSET WELL IDENTIFIER</span>
            <span>PROXIMITY</span>
          </div>

          {wells.length === 0 ? (
            <div className="rounded-lg border border-dashed border-slate-800 p-6 text-center text-xs text-slate-400">
              <Compass className="mx-auto h-6 w-6 text-slate-600 mb-2" />
              <p className="font-semibold text-slate-300">No Wells Match Criteria</p>
              <p className="mt-1 text-[11px] text-slate-500">
                Try expanding the search radius or resetting the active filters.
              </p>
              <button
                onClick={() => {
                  onRadiusChange(10);
                  onResetFilters();
                }}
                className="mt-3 inline-block rounded bg-cyan-950 px-3 py-1 font-mono text-xs font-semibold text-cyan-300 border border-cyan-800/80 hover:bg-cyan-900/60"
              >
                Expand to 10 km & Reset
              </button>
            </div>
          ) : (
            wells.map((well) => (
              <WellListItem
                key={well.id}
                well={well}
                isSelected={false}
                onSelect={onSelectWell}
              />
            ))
          )}
        </div>
        )}
      </div>
    </div>
  );
};
