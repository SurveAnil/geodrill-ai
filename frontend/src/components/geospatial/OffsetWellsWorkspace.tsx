'use client';

import React, { useState, useMemo, useEffect, useRef } from 'react';
import { ChevronLeft, ChevronRight } from 'lucide-react';
import { useDrillStore } from '@/store/useDrillStore';
import { OffsetWellFeature, WellFiltersState } from './types';
import {
  ACTIVE_WELL_ANCHOR,
  SEEDED_OFFSET_WELLS,
  filterWells,
  isValidGeoCoordinate,
} from './offsetWellsData';
import { ActiveContextBar } from './ActiveContextBar';
import { OffsetWellsMap } from './OffsetWellsMap';
import { NearbyWellsPanel } from './NearbyWellsPanel';
import { NearbyWellsSummary } from './NearbyWellsSummary';
import { WellDetailPanel } from './WellDetailPanel';

export const OffsetWellsWorkspace: React.FC = () => {
  const {
    activeWellId,
    activeWellLocation,
    telemetry,
  } = useDrillStore();

  const [radiusKm, setRadiusKm] = useState<number>(5);
  const [selectedWell, setSelectedWell] = useState<OffsetWellFeature | null>(null);
  const [panelVisible, setPanelVisible] = useState(true);
  const selectedWellDialogRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!selectedWell) return;
    const closeOnEscape = (event: KeyboardEvent) => {
      if (event.key === 'Escape') setSelectedWell(null);
    };
    window.addEventListener('keydown', closeOnEscape);
    selectedWellDialogRef.current?.focus();
    return () => window.removeEventListener('keydown', closeOnEscape);
  }, [selectedWell]);

  useEffect(() => {
    const updatePanelForViewport = () => {
      if (window.innerWidth < 1100) setPanelVisible(false);
    };
    updatePanelForViewport();
    window.addEventListener('resize', updatePanelForViewport);
    return () => window.removeEventListener('resize', updatePanelForViewport);
  }, []);

  const [filters, setFilters] = useState<WellFiltersState>({
    formation: 'All',
    riskLevel: 'All',
    eventType: 'All',
    wellStatus: 'All',
  });

  const activeCoords = useMemo(() => {
    const lat = activeWellLocation?.latitude ?? ACTIVE_WELL_ANCHOR.lat;
    const lon = activeWellLocation?.longitude ?? ACTIVE_WELL_ANCHOR.lon;
    return isValidGeoCoordinate(lat, lon)
      ? { lat, lon }
      : { lat: ACTIVE_WELL_ANCHOR.lat, lon: ACTIVE_WELL_ANCHOR.lon };
  }, [activeWellLocation]);

  // Wells filtered by search radius and filter criteria
  const visibleWells = useMemo(() => {
    return filterWells(SEEDED_OFFSET_WELLS, filters, radiusKm, activeCoords);
  }, [filters, radiusKm, activeCoords]);

  // All wells inside radius (ignoring dropdown filters, for total count)
  const allInRadius = useMemo(() => {
    return filterWells(
      SEEDED_OFFSET_WELLS,
      { formation: 'All', riskLevel: 'All', eventType: 'All', wellStatus: 'All' },
      radiusKm,
      activeCoords
    );
  }, [radiusKm, activeCoords]);

  // Summary counts
  const relevantInFormationCount = useMemo(() => {
    const formation = telemetry?.currentFormation || 'Northwind Sandstone';
    return allInRadius.filter(
      (w) => w.formation.toLowerCase() === formation.toLowerCase()
    ).length;
  }, [allInRadius, telemetry?.currentFormation]);

  const totalEventsInRadius = useMemo(() => {
    return allInRadius.reduce((acc, w) => acc + w.historicalEvents.length, 0);
  }, [allInRadius]);

  const handleResetFilters = () => {
    setFilters({
      formation: 'All',
      riskLevel: 'All',
      eventType: 'All',
      wellStatus: 'All',
    });
  };

  return (
    <div className="flex h-full min-h-0 w-full flex-col gap-2">
      <ActiveContextBar />

      <div
        className={`relative grid min-h-0 flex-1 transition-[grid-template-columns,gap] duration-300 ease-out ${panelVisible ? 'gap-3' : 'gap-0'}`}
        style={{ gridTemplateColumns: panelVisible ? 'minmax(0, 1fr) clamp(17rem, 28vw, 22rem)' : 'minmax(0, 1fr) 0fr' }}
      >
        <div className="min-h-0 min-w-0">
          <OffsetWellsMap
            wells={visibleWells}
            selectedWell={selectedWell}
            onSelectWell={setSelectedWell}
            radiusKm={radiusKm}
            activeLocation={activeCoords}
            activeWellId={activeWellId || ACTIVE_WELL_ANCHOR.wellId}
            isExpanded={!panelVisible}
            onToggleExpanded={() => setPanelVisible((visible) => !visible)}
          />
        </div>

        <div aria-hidden={!panelVisible} inert={!panelVisible} className={`min-h-0 min-w-0 overflow-hidden transition-opacity duration-200 ${panelVisible ? 'opacity-100' : 'pointer-events-none opacity-0'}`}>
          <NearbyWellsPanel
            wells={visibleWells}
            totalInRadius={allInRadius.length}
            selectedWell={selectedWell}
            onSelectWell={setSelectedWell}
            radiusKm={radiusKm}
            onRadiusChange={(r) => {
              setRadiusKm(r);
              // If selected well is outside new radius, deselect it
              if (selectedWell && selectedWell.distanceKm > r) {
                setSelectedWell(null);
              }
            }}
            filters={filters}
            onFiltersChange={setFilters}
            onResetFilters={handleResetFilters}
          />
        </div>

        <button
          type="button"
          onClick={() => setPanelVisible((visible) => !visible)}
          aria-label={panelVisible ? 'Collapse nearby wells panel' : 'Restore nearby wells panel'}
          title={panelVisible ? 'Collapse nearby wells' : 'Restore nearby wells'}
          className="absolute top-1/2 z-30 -translate-y-1/2 rounded-md border border-slate-600 bg-[#0B1120]/95 p-1.5 text-slate-200 shadow-lg transition hover:border-cyan-500 hover:text-cyan-300"
          style={{ right: panelVisible ? 'calc(clamp(17rem, 28vw, 22rem) + 0.75rem)' : '0.5rem' }}
        >
          {panelVisible ? <ChevronRight className="h-4 w-4" /> : <ChevronLeft className="h-4 w-4" />}
        </button>
      </div>

      {selectedWell && (
        <div
          className="fixed inset-0 z-[80] flex items-center justify-center bg-slate-950/75 p-3 backdrop-blur-sm sm:p-6"
          onMouseDown={(event) => {
            if (event.target === event.currentTarget) setSelectedWell(null);
          }}
        >
          <div
            ref={selectedWellDialogRef}
            role="dialog"
            aria-modal="true"
            aria-label={`Details for ${selectedWell.name}`}
            tabIndex={-1}
            className="h-[min(82dvh,760px)] w-full max-w-4xl outline-none"
          >
            <WellDetailPanel well={selectedWell} onClose={() => setSelectedWell(null)} />
          </div>
        </div>
      )}

      <NearbyWellsSummary
        wellsFoundCount={allInRadius.length}
        relevantWellsCount={relevantInFormationCount}
        totalEventsCount={totalEventsInRadius}
        radiusKm={radiusKm}
        activeFormation={telemetry?.currentFormation || 'Northwind Sandstone'}
      />
    </div>
  );
};
