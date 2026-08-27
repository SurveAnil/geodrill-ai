'use client';

import React, { useState } from 'react';
import {
  UploadCloud,
  FileText,
  CheckCircle2,
  Loader2,
  Sparkles,
  Layers,
  Database,
  ArrowRight,
} from 'lucide-react';

type StepStatus = 'idle' | 'running' | 'completed';

export const SmartIngestionStudio: React.FC = () => {
  const [pipelineStep, setPipelineStep] = useState<number>(0); // 0: idle, 1: upload, 2: OCR/NER, 3: KG
  const [isProcessing, setIsProcessing] = useState<boolean>(false);
  const [selectedFileName, setSelectedFileName] = useState<string | null>(null);

  const simulateIngestion = (fileName = 'wcr_volve_15_9_f11b.pdf') => {
    if (isProcessing) return;
    setIsProcessing(true);
    setSelectedFileName(fileName);
    setPipelineStep(1);

    // Step 1: Upload (0.8s)
    setTimeout(() => {
      setPipelineStep(2);
      // Step 2: OCR & NER Extraction (1.2s)
      setTimeout(() => {
        setPipelineStep(3);
        // Step 3: Knowledge Graph Ingestion (1.0s)
        setTimeout(() => {
          setIsProcessing(false);
        }, 1000);
      }, 1200);
    }, 800);
  };

  const getStepStatus = (stepIndex: number): StepStatus => {
    if (pipelineStep > stepIndex || (pipelineStep === 3 && !isProcessing)) return 'completed';
    if (pipelineStep === stepIndex && isProcessing) return 'running';
    return 'idle';
  };

  return (
    <div className="w-full rounded-xl bg-slate-800/40 backdrop-blur-md border border-slate-700/50 p-3.5 shadow-md flex flex-col gap-3">
      {/* Studio Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="p-1.5 rounded-lg bg-cyan-950/80 border border-cyan-800/60 text-cyan-400">
            <FileText className="w-4 h-4" />
          </div>
          <div>
            <h3 className="text-xs font-bold text-white tracking-wide uppercase">
              Smart WCR / DDR Ingestion Studio
            </h3>
            <span className="text-[10px] text-slate-400 font-mono">Layer 1 • Document Intelligence</span>
          </div>
        </div>

        <button
          onClick={() => simulateIngestion()}
          disabled={isProcessing}
          className={`flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-xs font-semibold font-mono transition-all ${
            isProcessing
              ? 'bg-slate-800 text-slate-500 cursor-not-allowed border border-slate-700'
              : 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 hover:bg-cyan-500/30 hover:border-cyan-400 shadow-sm'
          }`}
        >
          {isProcessing ? (
            <>
              <Loader2 className="w-3 h-3 animate-spin text-cyan-400" />
              <span>Extracting...</span>
            </>
          ) : (
            <>
              <Sparkles className="w-3 h-3 text-cyan-300" />
              <span>Run Sample Data</span>
            </>
          )}
        </button>
      </div>

      {/* Drag & Drop Zone */}
      <div
        onClick={() => simulateIngestion()}
        className="group relative border-2 border-dashed border-slate-700 hover:border-cyan-500/80 rounded-xl p-3.5 bg-[#0A101D]/70 hover:bg-[#0E1626]/80 transition-all cursor-pointer text-center flex flex-col items-center justify-center gap-1.5"
      >
        <div className="h-8 w-8 rounded-full bg-slate-800/80 border border-slate-700 flex items-center justify-center text-cyan-400 group-hover:scale-110 group-hover:bg-cyan-950/80 transition-all">
          <UploadCloud className="w-4 h-4" />
        </div>
        <p className="text-xs font-medium text-slate-200">
          Drag & Drop <span className="text-cyan-300 font-semibold">WCR, DDR</span>, or Mud Logs here
        </p>
        <p className="text-[10px] font-mono text-slate-400">
          Accepts PDF, DOCX, LAS, WITSML • Auto Digital / OCR Parsing
        </p>
        {selectedFileName && (
          <span className="mt-1 px-2 py-0.5 rounded bg-cyan-950/90 text-cyan-300 border border-cyan-800/70 text-[10px] font-mono">
            Active Doc: {selectedFileName}
          </span>
        )}
      </div>

      {/* Extraction Pipeline Stepper */}
      <div className="w-full bg-[#0A101D]/90 rounded-lg border border-slate-800/80 p-2.5">
        <div className="flex items-center justify-between text-[10px] font-mono text-slate-400 mb-2">
          <span>PIPELINE ORCHESTRATION</span>
          <span className="text-cyan-400">
            {pipelineStep === 0
              ? 'Standby'
              : pipelineStep === 1
              ? 'Stage 1/3: Document Ingestion'
              : pipelineStep === 2
              ? 'Stage 2/3: LLM Entity Extraction'
              : 'Stage 3/3: Graph Store Complete'}
          </span>
        </div>

        <div className="grid grid-cols-3 gap-2">
          {/* Step 1 */}
          <div
            className={`p-2 rounded-lg border flex items-center gap-2 transition-all ${
              getStepStatus(1) === 'completed'
                ? 'bg-emerald-950/20 border-emerald-800/60 text-emerald-300'
                : getStepStatus(1) === 'running'
                ? 'bg-cyan-950/30 border-cyan-500/80 text-cyan-300 shadow-sm shadow-cyan-900/30'
                : 'bg-[#0E1626] border-slate-800 text-slate-500'
            }`}
          >
            {getStepStatus(1) === 'completed' ? (
              <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 flex-shrink-0" />
            ) : getStepStatus(1) === 'running' ? (
              <Loader2 className="w-3.5 h-3.5 text-cyan-400 animate-spin flex-shrink-0" />
            ) : (
              <span className="w-3.5 h-3.5 rounded-full border border-slate-700 text-[9px] flex items-center justify-center flex-shrink-0">
                1
              </span>
            )}
            <div className="leading-tight truncate">
              <div className="text-[11px] font-semibold">Upload</div>
              <div className="text-[9px] opacity-75 font-mono">Parse PDF</div>
            </div>
          </div>

          {/* Step 2 */}
          <div
            className={`p-2 rounded-lg border flex items-center gap-2 transition-all ${
              getStepStatus(2) === 'completed'
                ? 'bg-emerald-950/20 border-emerald-800/60 text-emerald-300'
                : getStepStatus(2) === 'running'
                ? 'bg-cyan-950/30 border-cyan-500/80 text-cyan-300 shadow-sm shadow-cyan-900/30'
                : 'bg-[#0E1626] border-slate-800 text-slate-500'
            }`}
          >
            {getStepStatus(2) === 'completed' ? (
              <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 flex-shrink-0" />
            ) : getStepStatus(2) === 'running' ? (
              <Loader2 className="w-3.5 h-3.5 text-cyan-400 animate-spin flex-shrink-0" />
            ) : (
              <span className="w-3.5 h-3.5 rounded-full border border-slate-700 text-[9px] flex items-center justify-center flex-shrink-0">
                2
              </span>
            )}
            <div className="leading-tight truncate">
              <div className="text-[11px] font-semibold">OCR & NER</div>
              <div className="text-[9px] opacity-75 font-mono">Gemini Extract</div>
            </div>
          </div>

          {/* Step 3 */}
          <div
            className={`p-2 rounded-lg border flex items-center gap-2 transition-all ${
              getStepStatus(3) === 'completed'
                ? 'bg-emerald-950/20 border-emerald-800/60 text-emerald-300'
                : getStepStatus(3) === 'running'
                ? 'bg-cyan-950/30 border-cyan-500/80 text-cyan-300 shadow-sm shadow-cyan-900/30'
                : 'bg-[#0E1626] border-slate-800 text-slate-500'
            }`}
          >
            {getStepStatus(3) === 'completed' ? (
              <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 flex-shrink-0" />
            ) : getStepStatus(3) === 'running' ? (
              <Loader2 className="w-3.5 h-3.5 text-cyan-400 animate-spin flex-shrink-0" />
            ) : (
              <span className="w-3.5 h-3.5 rounded-full border border-slate-700 text-[9px] flex items-center justify-center flex-shrink-0">
                3
              </span>
            )}
            <div className="leading-tight truncate">
              <div className="text-[11px] font-semibold">Graph Store</div>
              <div className="text-[9px] opacity-75 font-mono">ChromaDB + DB</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
