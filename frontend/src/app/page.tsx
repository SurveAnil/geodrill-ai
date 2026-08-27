'use client';

import React from 'react';
import { TopNav } from '@/components/layout/TopNav';
import { DashboardGrid } from '@/components/layout/DashboardGrid';
import { TriageHero } from '@/components/triage/TriageHero';
import { TelemetryPanel } from '@/components/telemetry/TelemetryPanel';
import { GeospatialPanel } from '@/components/geospatial/GeospatialPanel';
import { AIPanelContainer } from '@/components/ai/AIPanelContainer';
import { StratigraphicCorrelation } from '@/components/stratigraphy/StratigraphicCorrelation';
import { LessonsLearnedRepository } from '@/components/lessons/LessonsLearnedRepository';

export default function DashboardPage() {
  return (
    <div className="flex flex-col min-h-screen bg-[#090D16] text-slate-100">
      <TopNav />
      <DashboardGrid
        heroSlot={<TriageHero />}
        leftSlot={<GeospatialPanel />}
        centerSlot={<AIPanelContainer />}
        rightSlot={<TelemetryPanel />}
        bottomLeftSlot={<StratigraphicCorrelation />}
        bottomRightSlot={<LessonsLearnedRepository />}
      />
    </div>
  );
}




