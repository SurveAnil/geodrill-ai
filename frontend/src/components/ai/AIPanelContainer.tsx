'use client';

import React from 'react';
import { SmartIngestionStudio } from './SmartIngestionStudio';
import { GeminiChat } from './GeminiChat';

export const AIPanelContainer: React.FC = () => {
  return (
    <div className="flex flex-col h-full gap-3.5">
      {/* Top: Smart Ingestion Studio (Layer 1) */}
      <SmartIngestionStudio />

      {/* Bottom: Gemini Cognitive Assistant (Layer 2) */}
      <GeminiChat />
    </div>
  );
};
