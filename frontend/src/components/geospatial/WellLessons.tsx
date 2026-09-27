'use client';

import React from 'react';
import { BookOpen, Lightbulb, ShieldCheck } from 'lucide-react';

interface WellLessonsProps {
  lessons: string[];
  wellName: string;
}

export const WellLessons: React.FC<WellLessonsProps> = ({ lessons, wellName }) => {
  if (!lessons || lessons.length === 0) {
    return (
      <div className="rounded-lg border border-slate-800 bg-slate-900/40 p-4 text-center">
        <ShieldCheck className="mx-auto h-6 w-6 text-cyan-400" />
        <p className="mt-2 text-xs font-semibold text-slate-200">
          Standard Geological Interval
        </p>
        <p className="mt-1 text-[11px] text-slate-400">
          No special operational mitigation measures were flagged for this offset trajectory.
        </p>
      </div>
    );
  }

  return (
    <div className="rounded-lg border border-cyan-800/40 bg-cyan-950/20 p-3.5">
      <div className="flex items-center gap-2 mb-2.5">
        <Lightbulb className="h-4 w-4 text-amber-400" />
        <h4 className="font-mono text-xs font-bold uppercase tracking-wider text-cyan-200">
          Mitigations & Lessons Learned ({wellName})
        </h4>
      </div>

      <ul className="space-y-2 text-xs text-slate-300">
        {lessons.map((lesson, idx) => (
          <li key={idx} className="flex items-start gap-2">
            <span className="mt-1 h-1.5 w-1.5 shrink-0 rounded-full bg-cyan-400" />
            <span className="leading-relaxed">{lesson}</span>
          </li>
        ))}
      </ul>
    </div>
  );
};
