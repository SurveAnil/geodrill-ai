'use client';

import { AppShell } from '@/components/layout/AppShell';
import { PageHeader } from '@/components/layout/PageHeader';
import { DashboardGrid } from '@/components/layout/DashboardGrid';
import { TriageHero } from '@/components/triage/TriageHero';
import { TelemetryPanel } from '@/components/telemetry/TelemetryPanel';
import { GeospatialPanel } from '@/components/geospatial/GeospatialPanel';
import { AIPanelContainer } from '@/components/ai/AIPanelContainer';
import { StratigraphicCorrelation } from '@/components/stratigraphy/StratigraphicCorrelation';
import { LessonsLearnedRepository } from '@/components/lessons/LessonsLearnedRepository';

export default function OverviewPage() {
  return <AppShell><PageHeader title="Operations overview" description="Live drilling context, risk triage, and offset-well intelligence." /><DashboardGrid heroSlot={<TriageHero />} leftSlot={<GeospatialPanel />} centerSlot={<AIPanelContainer />} rightSlot={<TelemetryPanel />} bottomLeftSlot={<StratigraphicCorrelation />} bottomRightSlot={<LessonsLearnedRepository />} /></AppShell>;
}
