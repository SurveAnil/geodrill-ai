'use client';

import React, { useState } from 'react';
import { SmartIngestionStudio } from './SmartIngestionStudio';
import { GeminiChat } from './GeminiChat';
import { ChevronDown, Database } from 'lucide-react';

export const AIPanelContainer: React.FC = () => {
  const [knowledgeOpen, setKnowledgeOpen] = useState(false);
  return (
    <div className="flex flex-col h-full gap-4 p-4">
      <GeminiChat />
      <section className="rounded-xl border border-slate-700/70 bg-slate-900/40">
        <button onClick={() => setKnowledgeOpen(!knowledgeOpen)} aria-expanded={knowledgeOpen} aria-controls="knowledge-base-panel" className="flex w-full items-center justify-between gap-3 p-3 text-left">
          <span className="flex items-center gap-2"><Database className="h-4 w-4 text-cyan-400" /><span><span className="block text-xs font-semibold text-white">Manage Knowledge Base</span><span className="block text-[10px] text-slate-400">Upload and process WCR, DDR, mud log, LAS, or WITSML documents.</span></span></span>
          <ChevronDown className={`h-4 w-4 text-slate-400 transition-transform ${knowledgeOpen ? 'rotate-180' : ''}`} />
        </button>
        {knowledgeOpen && <div id="knowledge-base-panel" className="border-t border-slate-800 p-3"><SmartIngestionStudio /></div>}
      </section>
    </div>
  );
};
