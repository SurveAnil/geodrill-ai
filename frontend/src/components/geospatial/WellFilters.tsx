'use client';

import React from 'react';
import { Filter, RotateCcw } from 'lucide-react';
import { WellFiltersState } from './types';

interface WellFiltersProps {
  filters: WellFiltersState;
  onChange: (filters: WellFiltersState) => void;
  onReset: () => void;
  totalFiltered: number;
  totalAvailable: number;
}

export const WellFilters: React.FC<WellFiltersProps> = ({
  filters,
  onChange,
  onReset,
  totalFiltered,
  totalAvailable,
}) => {
  const isFiltered =
    filters.formation !== 'All' ||
    filters.riskLevel !== 'All' ||
    filters.eventType !== 'All' ||
    filters.wellStatus !== 'All';

  return (
    <div className="rounded-lg border border-slate-800 bg-[#090D16] p-2.5 space-y-2">
      <div className="flex items-center justify-between text-xs">
        <span className="flex items-center gap-1.5 font-medium text-slate-300">
          <Filter className="h-3 w-3 text-cyan-400" />
          Filter Criteria ({totalFiltered}/{totalAvailable})
        </span>

        {isFiltered && (
          <button
            onClick={onReset}
            className="flex items-center gap-1 text-[10px] text-cyan-400 hover:text-cyan-300"
          >
            <RotateCcw className="h-2.5 w-2.5" />
            Reset
          </button>
        )}
      </div>

      <div className="grid grid-cols-2 gap-2 text-xs">
        {/* Formation Dropdown */}
        <div>
          <label className="text-[10px] uppercase font-mono text-slate-400">Formation</label>
          <select
            value={filters.formation}
            onChange={(e) => onChange({ ...filters, formation: e.target.value })}
            className="mt-0.5 w-full rounded border border-slate-700 bg-slate-900 px-2 py-1 text-[11px] text-slate-200 focus:border-cyan-500 focus:outline-none"
          >
            <option value="All">All Formations</option>
            <option value="Northwind Sandstone">Northwind Sandstone</option>
            <option value="Barail Coal">Barail Coal</option>
            <option value="Tipam Formation">Tipam Formation</option>
            <option value="Girujan Clay">Girujan Clay</option>
          </select>
        </div>

        {/* Risk Level Dropdown */}
        <div>
          <label className="text-[10px] uppercase font-mono text-slate-400">Risk Level</label>
          <select
            value={filters.riskLevel}
            onChange={(e) => onChange({ ...filters, riskLevel: e.target.value })}
            className="mt-0.5 w-full rounded border border-slate-700 bg-slate-900 px-2 py-1 text-[11px] text-slate-200 focus:border-cyan-500 focus:outline-none"
          >
            <option value="All">All Risks</option>
            <option value="high">High Risk</option>
            <option value="medium">Medium Risk</option>
            <option value="low">Low Risk</option>
          </select>
        </div>

        {/* Event Type Dropdown */}
        <div>
          <label className="text-[10px] uppercase font-mono text-slate-400">Incident Event</label>
          <select
            value={filters.eventType}
            onChange={(e) => onChange({ ...filters, eventType: e.target.value })}
            className="mt-0.5 w-full rounded border border-slate-700 bg-slate-900 px-2 py-1 text-[11px] text-slate-200 focus:border-cyan-500 focus:outline-none"
          >
            <option value="All">All Events</option>
            <option value="Gas Kick">Gas Kick</option>
            <option value="Stuck Pipe">Stuck Pipe</option>
            <option value="Mud Loss">Mud Loss</option>
            <option value="High Torque">High Torque</option>
            <option value="Cementing">Cementing</option>
          </select>
        </div>

        {/* Well Status Dropdown */}
        <div>
          <label className="text-[10px] uppercase font-mono text-slate-400">Well Status</label>
          <select
            value={filters.wellStatus}
            onChange={(e) => onChange({ ...filters, wellStatus: e.target.value })}
            className="mt-0.5 w-full rounded border border-slate-700 bg-slate-900 px-2 py-1 text-[11px] text-slate-200 focus:border-cyan-500 focus:outline-none"
          >
            <option value="All">All Status</option>
            <option value="Completed">Completed</option>
            <option value="Drilling">Drilling</option>
            <option value="Abandoned">Abandoned</option>
          </select>
        </div>
      </div>
    </div>
  );
};
