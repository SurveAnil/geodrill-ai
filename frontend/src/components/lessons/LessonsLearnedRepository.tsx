'use client';

import React, { useState, useMemo } from 'react';
import {
  BookOpen,
  Search,
  AlertOctagon,
  AlertTriangle,
  Flame,
  ShieldCheck,
  Lightbulb,
  Filter,
  CheckCircle2,
  ExternalLink,
} from 'lucide-react';

export type HazardCategory = 'all' | 'mud_loss' | 'stuck_pipe' | 'kick';

export interface LessonEvent {
  id: string;
  depthM: number;
  wellName: string;
  formation: string;
  hazardName: string;
  category: 'mud_loss' | 'stuck_pipe' | 'kick';
  severity: 'critical' | 'warning' | 'caution';
  incidentDescription: string;
  mitigation: string;
  keyLesson: string;
  sourceDoc: string;
  date: string;
}

export const LESSON_EVENTS: LessonEvent[] = [
  {
    id: 'evt-1',
    depthM: 3180,
    wellName: 'ONGC-KG-07-ALOK',
    formation: 'Krishna Sand-B / Hugin',
    hazardName: 'Severe Mud Loss',
    category: 'mud_loss',
    severity: 'critical',
    incidentDescription:
      'Sudden drop in SPP (450 psi drop) and total loss of returns (65 bbl/hr) encountered while drilling through permeable high-porosity sandstone.',
    mitigation: 'Spotted 40 bbl LCM pill (medium/coarse CaCO3 blend) and reduced annular pump rate.',
    keyLesson: 'Do not exceed ECD of 11.1 ppg (1.33 SG) in this horizon. Stage 50 bbl LCM on surface prior to bit entry.',
    sourceDoc: 'WCR ONGC-KG-07, Section 4.2 (p. 18)',
    date: 'March 2021',
  },
  {
    id: 'evt-2',
    depthM: 3240,
    wellName: 'ONGC-KG-09-CHARLIE',
    formation: 'Lower Krishna Siltstone',
    hazardName: 'Differential Sticking',
    category: 'stuck_pipe',
    severity: 'warning',
    incidentDescription:
      'Drill string became mechanically stuck after remaining stationary for 10 minutes during a drill pipe connection.',
    mitigation: 'Spaced out tool joint, activated hydraulic drilling jars with 35 klbs upward jarring force, worked string free in 4 hours.',
    keyLesson: 'Minimize connection times to < 3 minutes in overbalanced zones; maintain continuous string rotation and reciprocation.',
    sourceDoc: 'DDR ONGC-KG-09, Shift Report Day 22',
    date: 'August 2022',
  },
  {
    id: 'evt-3',
    depthM: 3310,
    wellName: 'ONGC-KG-12-BRAVO',
    formation: 'Upper Overpressured Sand',
    hazardName: 'Gas Kick & Influx',
    category: 'kick',
    severity: 'warning',
    incidentDescription:
      'Rapid 15 bbl pit volume gain observed with flow check confirming positive flow with mud pumps turned off.',
    mitigation: 'Hard shut-in on annular preventer, recorded 380 psi SIDPP and 450 psi SICP. Circulated kick out using Driller\'s Method.',
    keyLesson: 'Increase active Mud Weight to 12.2 ppg (1.46 SG) before penetrating 3,300m depth horizon.',
    sourceDoc: 'Incident Report KG-12 (2008), Event #14',
    date: 'November 2023',
  },
];

const SEVERITY_CONFIG = {
  critical: {
    badge: 'bg-red-950/80 text-red-300 border-red-800/80',
    nodeColor: 'bg-red-500 ring-red-500/30',
    lineColor: 'border-red-800/60',
    icon: <AlertOctagon className="w-3.5 h-3.5 text-red-400" />,
  },
  warning: {
    badge: 'bg-orange-950/80 text-orange-300 border-orange-800/80',
    nodeColor: 'bg-orange-500 ring-orange-500/30',
    lineColor: 'border-orange-800/60',
    icon: <AlertTriangle className="w-3.5 h-3.5 text-orange-400" />,
  },
  caution: {
    badge: 'bg-amber-950/80 text-amber-300 border-amber-800/80',
    nodeColor: 'bg-amber-500 ring-amber-500/30',
    lineColor: 'border-amber-800/60',
    icon: <Flame className="w-3.5 h-3.5 text-amber-400" />,
  },
};

export const LessonsLearnedRepository: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<HazardCategory>('all');

  const filteredEvents = useMemo(() => {
    return LESSON_EVENTS.filter((evt) => {
      const matchesCategory =
        selectedCategory === 'all' || evt.category === selectedCategory;
      const q = searchQuery.toLowerCase().trim();
      const matchesQuery =
        !q ||
        evt.wellName.toLowerCase().includes(q) ||
        evt.hazardName.toLowerCase().includes(q) ||
        evt.formation.toLowerCase().includes(q) ||
        evt.incidentDescription.toLowerCase().includes(q) ||
        evt.keyLesson.toLowerCase().includes(q) ||
        evt.depthM.toString().includes(q);

      return matchesCategory && matchesQuery;
    });
  }, [searchQuery, selectedCategory]);

  return (
    <div className="flex flex-col h-full justify-between">
      {/* Header */}
      <div className="flex items-center justify-between pb-2.5 border-b border-slate-800">
        <div className="flex items-center gap-2">
          <div className="p-1.5 rounded-lg bg-cyan-950/60 border border-cyan-800/50 text-cyan-400">
            <BookOpen className="w-4 h-4" />
          </div>
          <div>
            <h3 className="text-xs font-bold text-white tracking-wide uppercase">
              Historical Offset Incidents & Lessons Learned
            </h3>
            <span className="text-[10px] text-slate-400 font-mono">
              Depth-Indexed Traceable Knowledge Base
            </span>
          </div>
        </div>
        <span className="px-2 py-0.5 rounded text-[10px] font-mono font-semibold bg-[#0A101D] text-slate-400 border border-slate-800">
          {filteredEvents.length} Events Logged
        </span>
      </div>

      {/* Search & Filter Controls */}
      <div className="my-2.5 space-y-2">
        {/* Search Input Bar */}
        <div className="relative flex items-center">
          <Search className="w-3.5 h-3.5 absolute left-3 text-slate-400 pointer-events-none" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search by hazard, formation, well, depth (e.g. 3180, mud loss, KG-07)..."
            className="w-full bg-[#0A101D] border border-slate-700/80 rounded-lg pl-8 pr-3 py-1.5 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500 shadow-inner"
          />
        </div>

        {/* Filter Chips */}
        <div className="flex items-center gap-1.5 overflow-x-auto no-scrollbar">
          <span className="text-[9.5px] font-mono text-slate-500 uppercase flex items-center gap-1 mr-1">
            <Filter className="w-3 h-3" /> Filter:
          </span>
          {(
            [
              { key: 'all', label: 'All Events' },
              { key: 'mud_loss', label: 'Mud Loss' },
              { key: 'stuck_pipe', label: 'Stuck Pipe' },
              { key: 'kick', label: 'Gas Kicks' },
            ] as const
          ).map((filter) => (
            <button
              key={filter.key}
              onClick={() => setSelectedCategory(filter.key)}
              className={`px-2.5 py-0.5 rounded-full text-[10px] font-mono font-medium transition-all ${
                selectedCategory === filter.key
                  ? 'bg-cyan-500 text-slate-950 font-bold shadow-sm'
                  : 'bg-[#0E1626] text-slate-400 hover:text-white border border-slate-800'
              }`}
            >
              {filter.label}
            </button>
          ))}
        </div>
      </div>

      {/* Depth-Indexed Timeline Scroll Area */}
      <div className="flex-1 overflow-y-auto pr-1 space-y-3 min-h-[220px] max-h-[260px]">
        {filteredEvents.length === 0 ? (
          <div className="h-32 flex flex-col items-center justify-center text-xs text-slate-500 font-mono">
            <span>No historical incidents matched query.</span>
          </div>
        ) : (
          filteredEvents.map((evt, idx) => {
            const sev = SEVERITY_CONFIG[evt.severity];
            return (
              <div key={evt.id} className="relative pl-6 group">
                {/* Vertical Timeline Stem */}
                {idx !== filteredEvents.length - 1 && (
                  <div className="absolute left-2.5 top-3 bottom-0 w-px bg-slate-800 group-hover:bg-slate-700 transition-colors" />
                )}

                {/* Timeline Severity Node */}
                <div
                  className={`absolute left-1 top-1.5 h-3.5 w-3.5 rounded-full ${sev.nodeColor} ring-4 ring-slate-900 flex items-center justify-center`}
                />

                {/* Event Card */}
                <div className="bg-[#0A101D] border border-slate-800/90 rounded-xl p-3 shadow-md hover:border-slate-700 transition-all">
                  {/* Card Header */}
                  <div className="flex items-start justify-between gap-2 mb-1.5">
                    <div>
                      <div className="flex items-center gap-2">
                        <span
                          className="text-xs font-bold font-mono text-cyan-300"
                          style={{ fontVariantNumeric: 'tabular-nums' }}
                        >
                          {evt.depthM.toLocaleString()}m MD
                        </span>
                        <span className="text-slate-500">•</span>
                        <span className="text-xs font-semibold text-white font-mono">
                          {evt.wellName}
                        </span>
                      </div>
                      <span className="text-[10px] text-slate-400 font-mono">
                        Formation: {evt.formation} ({evt.date})
                      </span>
                    </div>

                    {/* Hazard Severity Badge */}
                    <span
                      className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-mono font-bold uppercase border ${sev.badge}`}
                    >
                      {sev.icon}
                      <span>{evt.hazardName}</span>
                    </span>
                  </div>

                  {/* Incident Description */}
                  <p className="text-[11px] text-slate-300 leading-relaxed mb-2 font-sans">
                    {evt.incidentDescription}
                  </p>

                  {/* Distinctive Actionable Takeaway / Lesson Panel */}
                  <div className="rounded-lg bg-[#0F1D2C] border border-cyan-800/40 p-2.5 space-y-1">
                    <div className="flex items-center gap-1.5 text-[10px] font-mono font-bold text-emerald-400 uppercase">
                      <ShieldCheck className="w-3.5 h-3.5 text-emerald-400 flex-shrink-0" />
                      <span>Mitigation Applied & Key Lesson Learned</span>
                    </div>
                    <p className="text-[11px] text-slate-200 leading-relaxed font-sans">
                      <strong className="text-cyan-300">Action: </strong>
                      {evt.mitigation}
                    </p>
                    <p className="text-[11px] text-emerald-200 font-medium leading-relaxed font-sans">
                      <strong className="text-emerald-400">Lesson: </strong>
                      {evt.keyLesson}
                    </p>
                  </div>

                  {/* Source Document Citation */}
                  <div className="mt-2 flex items-center justify-between text-[9.5px] text-slate-500 font-mono pt-1 border-t border-slate-800/60">
                    <span className="flex items-center gap-1">
                      <CheckCircle2 className="w-3 h-3 text-cyan-500" /> Verified Extraction
                    </span>
                    <span className="flex items-center gap-1 text-slate-400 hover:text-cyan-300 cursor-pointer">
                      <span>{evt.sourceDoc}</span>
                      <ExternalLink className="w-2.5 h-2.5" />
                    </span>
                  </div>
                </div>
              </div>
            );
          })
        )}
      </div>

      {/* Footer */}
      <div className="text-[11px] text-slate-500 border-t border-slate-800/60 pt-2 font-mono flex items-center justify-between">
        <span className="flex items-center gap-1 text-slate-400">
          <Lightbulb className="w-3.5 h-3.5 text-amber-400" />
          <span>Operational Best Practices Auto-Linked</span>
        </span>
        <span className="text-cyan-400 font-semibold">Layer 4 Incident Store</span>
      </div>
    </div>
  );
};
