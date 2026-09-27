'use client';

import React from 'react';
import { AppShell } from '@/components/layout/AppShell';
import { PageHeader } from '@/components/layout/PageHeader';
import { OffsetWellsWorkspace } from '@/components/geospatial/OffsetWellsWorkspace';

export default function OffsetWellsPage() {
  return (
    <AppShell>
      <div className="flex h-full min-h-0 flex-col gap-3">
      <PageHeader
        title="Offset Wells"
        description="Compare nearby wells and their historical evidence against the active drilling context."
        className="mb-0 shrink-0"
      />
      <div className="flex min-h-0 flex-1">
        <OffsetWellsWorkspace />
      </div>
      </div>
    </AppShell>
  );
}
