'use client';

import React, { useRef, useState } from 'react';
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
type UploadStatus = 'idle' | 'uploading' | 'processing' | 'success' | 'error';

const API_ENDPOINT = `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/v1/ingest-document`;
const ALLOWED_EXTENSIONS = ['.pdf', '.docx', '.las', '.witsml'];

export const SmartIngestionStudio: React.FC = () => {
  const [pipelineStep, setPipelineStep] = useState<number>(0); // 0: idle, 1: upload, 2: OCR/NER, 3: KG
  const [uploadStatus, setUploadStatus] = useState<UploadStatus>('idle');
  const [selectedFileName, setSelectedFileName] = useState<string | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const isProcessing = uploadStatus === 'uploading' || uploadStatus === 'processing';

  const handleFileUpload = async (file: File) => {
    if (isProcessing) return;

    const extension = `.${file.name.split('.').pop()?.toLowerCase() || ''}`;
    if (!ALLOWED_EXTENSIONS.includes(extension)) {
      setUploadStatus('error');
      setErrorMessage('Unsupported file type. Please upload a PDF, DOCX, LAS, or WITSML file.');
      return;
    }

    setErrorMessage(null);
    setSelectedFileName(file.name);
    setPipelineStep(1);
    setUploadStatus('uploading');

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch(API_ENDPOINT, { method: 'POST', body: formData });
      if (!response.ok) {
        const body = await response.json().catch(() => null) as { detail?: string } | null;
        throw new Error(body?.detail || `Upload failed (${response.status}).`);
      }
      setPipelineStep(2);
      setUploadStatus('processing');
      const job = await response.json() as { job_id?: string; status?: string; error?: string };
      if (!job.job_id) throw new Error('Upload accepted without an ingestion job id.');
      // 202 means queued, not completed: poll the durable job before showing success.
      for (let attempt = 0; attempt < 60; attempt += 1) {
        await new Promise((resolve) => setTimeout(resolve, 500));
        const statusResponse = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/v1/ingestion-jobs/${encodeURIComponent(job.job_id)}`);
        if (!statusResponse.ok) throw new Error(`Unable to read ingestion status (${statusResponse.status}).`);
        const status = await statusResponse.json() as { status: string; error?: string };
        if (status.status === 'succeeded') {
          setPipelineStep(3);
          setUploadStatus('success');
          return;
        }
        if (status.status === 'failed') throw new Error(status.error || 'Document processing failed.');
      }
      throw new Error('Document processing timed out; check the ingestion job status in the backend.');
    } catch (error) {
      setUploadStatus('error');
      setErrorMessage(error instanceof Error ? error.message : 'Unable to upload the document.');
    }
  };

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) void handleFileUpload(file);
    event.target.value = '';
  };

  const handleDrop = (event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    const file = event.dataTransfer.files[0];
    if (file) void handleFileUpload(file);
  };

  const getStepStatus = (stepIndex: number): StepStatus => {
    if (uploadStatus === 'error') {
      return pipelineStep > stepIndex ? 'completed' : 'idle';
    }
    if (pipelineStep > stepIndex || (pipelineStep === 3 && uploadStatus === 'success')) return 'completed';
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
          onClick={() => fileInputRef.current?.click()}
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
              <span>Select Document</span>
            </>
          )}
        </button>
      </div>

      {/* Drag & Drop Zone */}
      <div
        onClick={() => fileInputRef.current?.click()}
        onDragOver={(event) => event.preventDefault()}
        onDrop={handleDrop}
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
        <input
          ref={fileInputRef}
          type="file"
          className="hidden"
          accept=".pdf,.docx,.las,.witsml"
          onChange={handleFileChange}
        />
        {selectedFileName && (
          <span className="mt-1 px-2 py-0.5 rounded bg-cyan-950/90 text-cyan-300 border border-cyan-800/70 text-[10px] font-mono">
            Active Doc: {selectedFileName}
          </span>
        )}
        {errorMessage && <p className="mt-1 text-[10px] text-rose-300">{errorMessage}</p>}
      </div>

      {/* Extraction Pipeline Stepper */}
      <div className="w-full bg-[#0A101D]/90 rounded-lg border border-slate-800/80 p-2.5">
        <div className="flex items-center justify-between text-[10px] font-mono text-slate-400 mb-2">
          <span>PIPELINE ORCHESTRATION</span>
          <span className="text-cyan-400">
            {uploadStatus === 'error'
              ? 'Error'
              : uploadStatus === 'success'
              ? 'Complete'
              : pipelineStep === 0
              ? 'Standby'
              : pipelineStep === 1
              ? 'Uploading'
              : pipelineStep === 2
              ? 'Processing OCR'
              : 'Success'}
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
