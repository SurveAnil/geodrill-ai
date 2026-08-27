'use client';

import React, { useRef, useEffect, useCallback, useState } from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Filler,
  Tooltip,
  Legend,
} from 'chart.js';
import { Line } from 'react-chartjs-2';
import type { ChartOptions, ChartData } from 'chart.js';
import { useDrillStore } from '@/store/useDrillStore';

/* ------------------------------------------------------------------ */
/*  Chart.js registration (once per module)                             */
/* ------------------------------------------------------------------ */
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Filler,
  Tooltip,
  Legend,
);

/* ------------------------------------------------------------------ */
/*  Constants                                                           */
/* ------------------------------------------------------------------ */
const HISTORY_LIMIT = 100;
const TICK_SAMPLE_RATE = 3; // sample every 3rd store tick → ~3.3 Hz chart updates

// Operating-window thresholds for background bands
const SPP_SAFE_LOW = 2500;
const SPP_SAFE_HIGH = 3600;
const SPP_FRAC_LIMIT = 4200;

/* ------------------------------------------------------------------ */
/*  Background-band plugin — renders horizontal safe/warning zones      */
/* ------------------------------------------------------------------ */
const bandPlugin = {
  id: 'operatingBands',
  beforeDraw(chart: ChartJS) {
    const { ctx, chartArea, scales } = chart;
    if (!chartArea || !scales['y-spp']) return;

    const ySpp = scales['y-spp'];
    const { left, right } = chartArea;

    // Safe operating window (green band)
    const safeTop = ySpp.getPixelForValue(SPP_SAFE_HIGH);
    const safeBottom = ySpp.getPixelForValue(SPP_SAFE_LOW);
    ctx.save();
    ctx.fillStyle = 'rgba(16, 185, 129, 0.04)';
    ctx.fillRect(left, safeTop, right - left, safeBottom - safeTop);
    ctx.restore();

    // Frac-limit danger band (red band above frac limit)
    const fracTop = ySpp.getPixelForValue(ySpp.max!);
    const fracBottom = ySpp.getPixelForValue(SPP_FRAC_LIMIT);
    if (fracBottom > fracTop) {
      ctx.save();
      ctx.fillStyle = 'rgba(239, 68, 68, 0.06)';
      ctx.fillRect(left, fracTop, right - left, fracBottom - fracTop);
      ctx.restore();
    }

    // Frac limit dashed line
    const fracY = ySpp.getPixelForValue(SPP_FRAC_LIMIT);
    ctx.save();
    ctx.strokeStyle = 'rgba(239, 68, 68, 0.35)';
    ctx.lineWidth = 1;
    ctx.setLineDash([6, 4]);
    ctx.beginPath();
    ctx.moveTo(left, fracY);
    ctx.lineTo(right, fracY);
    ctx.stroke();
    ctx.restore();
  },
};

ChartJS.register(bandPlugin);

/* ------------------------------------------------------------------ */
/*  Chart options — static, no animations                               */
/* ------------------------------------------------------------------ */
const chartOptions: ChartOptions<'line'> = {
  responsive: true,
  maintainAspectRatio: false,
  animation: false,
  interaction: {
    mode: 'index',
    intersect: false,
  },
  plugins: {
    legend: {
      display: true,
      position: 'top',
      align: 'end',
      labels: {
        color: '#64748B',
        font: { size: 10, family: 'ui-monospace, monospace' },
        boxWidth: 8,
        boxHeight: 8,
        padding: 8,
        usePointStyle: true,
        pointStyle: 'circle',
      },
    },
    tooltip: {
      backgroundColor: '#0F172A',
      borderColor: '#1E293B',
      borderWidth: 1,
      titleColor: '#94A3B8',
      bodyColor: '#E2E8F0',
      titleFont: { size: 10, family: 'ui-monospace, monospace' },
      bodyFont: { size: 11, family: 'ui-monospace, monospace' },
      padding: 8,
      displayColors: true,
    },
  },
  scales: {
    x: {
      display: true,
      grid: {
        color: 'rgba(30, 41, 59, 0.5)',
        lineWidth: 0.5,
      },
      ticks: {
        color: '#475569',
        font: { size: 9, family: 'ui-monospace, monospace' },
        maxTicksLimit: 6,
        maxRotation: 0,
      },
      border: { color: '#1E293B' },
    },
    'y-spp': {
      type: 'linear',
      display: true,
      position: 'left',
      title: {
        display: true,
        text: 'SPP (psi)',
        color: '#8B5CF6',
        font: { size: 10, family: 'ui-monospace, monospace' },
      },
      grid: {
        color: 'rgba(30, 41, 59, 0.4)',
        lineWidth: 0.5,
      },
      ticks: {
        color: '#7C3AED',
        font: { size: 9, family: 'ui-monospace, monospace' },
        maxTicksLimit: 5,
      },
      border: { color: '#1E293B' },
      min: 2000,
      max: 5000,
    },
    'y-rop': {
      type: 'linear',
      display: true,
      position: 'right',
      title: {
        display: true,
        text: 'ROP (m/hr)',
        color: '#10B981',
        font: { size: 10, family: 'ui-monospace, monospace' },
      },
      grid: { drawOnChartArea: false },
      ticks: {
        color: '#059669',
        font: { size: 9, family: 'ui-monospace, monospace' },
        maxTicksLimit: 5,
      },
      border: { color: '#1E293B' },
      min: 0,
      max: 60,
    },
  },
};

/* ================================================================== */
/*  TELEMETRY CHART — main export                                       */
/* ================================================================== */
interface HistoryPoint {
  label: string;
  spp: number;
  rop: number;
}

export const TelemetryChart: React.FC = React.memo(() => {
  const [history, setHistory] = useState<HistoryPoint[]>([]);
  const tickCounterRef = useRef(0);
  const chartRef = useRef<ChartJS<'line'>>(null);

  // Subscribe to store changes outside React render cycle for perf
  useEffect(() => {
    const unsub = useDrillStore.subscribe((state) => {
      tickCounterRef.current += 1;
      if (tickCounterRef.current % TICK_SAMPLE_RATE !== 0) return;

      const { telemetry } = state;
      const point: HistoryPoint = {
        label: `${telemetry.measuredDepthM.toFixed(1)}m`,
        spp: telemetry.standpipePressure + Math.round((Math.random() - 0.5) * 40),
        rop: telemetry.rop,
      };

      setHistory((prev) => {
        const next = [...prev, point];
        return next.length > HISTORY_LIMIT ? next.slice(-HISTORY_LIMIT) : next;
      });
    });

    return unsub;
  }, []);

  const chartData: ChartData<'line'> = {
    labels: history.map((h) => h.label),
    datasets: [
      {
        label: 'SPP',
        data: history.map((h) => h.spp),
        borderColor: '#8B5CF6',
        backgroundColor: 'rgba(139, 92, 246, 0.08)',
        borderWidth: 1.5,
        pointRadius: 0,
        pointHitRadius: 4,
        fill: true,
        tension: 0.3,
        yAxisID: 'y-spp',
      },
      {
        label: 'ROP',
        data: history.map((h) => h.rop),
        borderColor: '#10B981',
        backgroundColor: 'rgba(16, 185, 129, 0.06)',
        borderWidth: 1.5,
        pointRadius: 0,
        pointHitRadius: 4,
        fill: true,
        tension: 0.3,
        yAxisID: 'y-rop',
      },
    ],
  };

  return (
    <div className="w-full h-full min-h-[200px] relative">
      <Line ref={chartRef} data={chartData} options={chartOptions} />
    </div>
  );
});

TelemetryChart.displayName = 'TelemetryChart';
