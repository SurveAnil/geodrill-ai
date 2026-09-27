'use client';

import React, { useEffect, useRef, useState, useCallback } from 'react';
import 'maplibre-gl/dist/maplibre-gl.css';
import type { GeoJSONSource, Map as MapLibreMap, MapLayerMouseEvent, StyleSpecification } from 'maplibre-gl';
import {
  Plus,
  Minus,
  Crosshair,
  Maximize2,
  Minimize2,
  Compass,
} from 'lucide-react';
import { OffsetWellFeature, MapStyleType } from './types';
import {
  ACTIVE_WELL_ANCHOR,
  createGeodesicRadiusGeoJSON,
  isValidGeoCoordinate,
  wellsToGeoJSON,
} from './offsetWellsData';

interface OffsetWellsMapProps {
  wells: OffsetWellFeature[];
  selectedWell: OffsetWellFeature | null;
  onSelectWell: (well: OffsetWellFeature | null) => void;
  radiusKm: number;
  activeLocation?: { lat: number; lon: number };
  activeWellId?: string;
  isExpanded: boolean;
  onToggleExpanded: () => void;
}

export const OffsetWellsMap: React.FC<OffsetWellsMapProps> = ({
  wells,
  selectedWell,
  onSelectWell,
  radiusKm,
  activeLocation = { lat: ACTIVE_WELL_ANCHOR.lat, lon: ACTIVE_WELL_ANCHOR.lon },
  activeWellId = ACTIVE_WELL_ANCHOR.wellId,
  isExpanded,
  onToggleExpanded,
}) => {
  const mapContainerRef = useRef<HTMLDivElement>(null);
  const mapRef = useRef<MapLibreMap | null>(null);
  const [mapLoaded, setMapLoaded] = useState(false);
  const [mapStyle, setMapStyle] = useState<MapStyleType>('dark');
  const [webglSupported, setWebglSupported] = useState<boolean>(true);
  const cartoApiKey = process.env.NEXT_PUBLIC_CARTO_API_KEY?.trim();
  const latestDataRef = useRef({ wells, selectedWell, radiusKm, activeLocation, activeWellId, onSelectWell });
  latestDataRef.current = { wells, selectedWell, radiusKm, activeLocation, activeWellId, onSelectWell };

  // Fallback SVG pan/zoom state
  const [fallbackZoom, setFallbackZoom] = useState(1);
  const [fallbackPan, setFallbackPan] = useState({ x: 0, y: 0 });
  const isDraggingRef = useRef(false);
  const dragStartRef = useRef({ x: 0, y: 0 });

  // Style Tile URL definitions
  const getStyleDefinition = useCallback((styleType: MapStyleType): StyleSpecification => {
    if (styleType === 'satellite') {
      return {
        version: 8,
        glyphs: 'https://fonts.openmaptiles.org/{fontstack}/{range}.pbf',
        sources: {
          'satellite-tiles': {
            type: 'raster',
            tiles: [
              'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
            ],
            tileSize: 256,
            attribution: 'Esri World Imagery',
          },
        },
        layers: [
          {
            id: 'satellite-layer',
            type: 'raster',
            source: 'satellite-tiles',
            minzoom: 0,
            maxzoom: 19,
          },
        ],
      };
    }

    if (styleType === 'terrain') {
      return {
        version: 8,
        glyphs: 'https://fonts.openmaptiles.org/{fontstack}/{range}.pbf',
        sources: {
          'terrain-tiles': {
            type: 'raster',
            tiles: [
              'https://server.arcgisonline.com/ArcGIS/rest/services/World_Topo_Map/MapServer/tile/{z}/{y}/{x}',
            ],
            tileSize: 256,
            attribution: 'Esri World Topo',
          },
        },
        layers: [
          {
            id: 'terrain-layer',
            type: 'raster',
            source: 'terrain-tiles',
            minzoom: 0,
            maxzoom: 19,
          },
        ],
      };
    }

    // Default: Dark Carto / Tactical Dark Mode
    return {
      version: 8,
      glyphs: 'https://fonts.openmaptiles.org/{fontstack}/{range}.pbf',
      sources: {
        'carto-dark-tiles': {
          type: 'raster',
          tiles: [
            'https://a.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}.png',
            'https://b.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}.png',
            'https://c.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}.png',
          ].map((tileUrl) => cartoApiKey
            ? `${tileUrl}?key=${encodeURIComponent(cartoApiKey)}`
            : tileUrl),
          tileSize: 256,
          attribution: 'CARTO / OpenStreetMap',
        },
      },
      layers: [
        {
          id: 'background',
          type: 'background',
          paint: { 'background-color': '#090D16' },
        },
        {
          id: 'carto-dark-layer',
          type: 'raster',
          source: 'carto-dark-tiles',
          minzoom: 0,
          maxzoom: 19,
        },
      ],
    };
  }, [cartoApiKey]);

  // Initialize MapLibre
  useEffect(() => {
    let isCancelled = false;
    let interactionsBound = false;
    let resizeObserver: ResizeObserver | null = null;

    async function initMap() {
      if (!mapContainerRef.current) return;

      try {
        const maplibregl = await import('maplibre-gl');
        maplibregl.setWorkerUrl('/maplibre-gl-worker.mjs');

        // Check WebGL availability
        const canvas = document.createElement('canvas');
        const gl =
          canvas.getContext('webgl') || canvas.getContext('experimental-webgl');
        if (!gl) {
          setWebglSupported(false);
          return;
        }

        if (isCancelled) return;

        const initialLocation = latestDataRef.current.activeLocation;
        const activeMap = new maplibregl.Map({
          container: mapContainerRef.current,
          style: getStyleDefinition('dark'),
          center: [initialLocation.lon, initialLocation.lat],
          zoom: 10,
          attributionControl: false,
        });
        mapRef.current = activeMap;

        activeMap.on('style.load', () => {
          if (isCancelled) return;
          const current = latestDataRef.current;
          setMapLoaded(true);

          // 1. Add Search Radius Polygon Layer
          activeMap.addSource('radius-source', {
            type: 'geojson',
            data: createGeodesicRadiusGeoJSON(
              current.activeLocation.lon,
              current.activeLocation.lat,
              current.radiusKm
            ),
          });

          activeMap.addLayer({
            id: 'radius-fill',
            type: 'fill',
            source: 'radius-source',
            paint: {
              'fill-color': '#06B6D4',
              'fill-opacity': 0.08,
            },
          });

          activeMap.addLayer({
            id: 'radius-outline',
            type: 'line',
            source: 'radius-source',
            paint: {
              'line-color': '#06B6D4',
              'line-width': 1.5,
              'line-dasharray': [3, 2],
            },
          });

          // 2. Add Active Well Source & Layers
          activeMap.addSource('active-well-source', {
            type: 'geojson',
            data: {
              type: 'FeatureCollection',
              features: [
                {
                  type: 'Feature',
                  geometry: {
                    type: 'Point',
                    coordinates: [current.activeLocation.lon, current.activeLocation.lat],
                  },
                  properties: { wellId: current.activeWellId },
                },
              ],
            },
          });

          // Active well outer pulse ring
          activeMap.addLayer({
            id: 'active-well-pulse',
            type: 'circle',
            source: 'active-well-source',
            paint: {
              'circle-radius': 16,
              'circle-color': '#0284C7',
              'circle-opacity': 0.25,
              'circle-stroke-width': 1.5,
              'circle-stroke-color': '#38BDF8',
            },
          });

          // Active well core marker
          activeMap.addLayer({
            id: 'active-well-core',
            type: 'circle',
            source: 'active-well-source',
            paint: {
              'circle-radius': 7,
              'circle-color': '#0EA5E9',
              'circle-stroke-width': 2.5,
              'circle-stroke-color': '#FFFFFF',
            },
          });
          activeMap.addLayer({
            id: 'active-well-label',
            type: 'symbol',
            source: 'active-well-source',
            layout: {
              'text-field': ['concat', 'ACTIVE  ', ['get', 'wellId']],
              'text-font': ['Open Sans Semibold'],
              'text-size': 12,
              'text-offset': [0, 2],
              'text-anchor': 'top',
              'text-allow-overlap': true,
            },
            paint: { 'text-color': '#BAF3FF', 'text-halo-color': '#07111E', 'text-halo-width': 2 },
          });

          // 3. Add Offset Wells Source & Layers
          activeMap.addSource('offset-wells-source', {
            type: 'geojson',
            data: wellsToGeoJSON(current.wells),
          });

          // Offset wells circles
          activeMap.addLayer({
            id: 'offset-wells-points',
            type: 'circle',
            source: 'offset-wells-source',
            paint: {
              'circle-radius': [
                'case',
                ['==', ['get', 'id'], current.selectedWell?.id || ''],
                11,
                8,
              ],
              'circle-color': [
                'match',
                ['get', 'riskLevel'],
                'high',
                '#EF4444',
                'medium',
                '#F59E0B',
                '#10B981',
              ],
              'circle-stroke-width': [
                'case',
                ['==', ['get', 'id'], current.selectedWell?.id || ''],
                3.5,
                1.5,
              ],
              'circle-stroke-color': ['case', ['==', ['get', 'id'], current.selectedWell?.id || ''], '#67E8F9', '#FFFFFF'],
              'circle-opacity': 1,
            },
          });

          activeMap.addLayer({
            id: 'offset-wells-labels',
            type: 'symbol',
            source: 'offset-wells-source',
            layout: {
              'text-field': ['get', 'name'],
              'text-font': ['Open Sans Semibold'],
              'text-size': 11,
              'text-offset': [0, 1.25],
              'text-anchor': 'top',
              'text-optional': true,
            },
            paint: { 'text-color': '#FFFFFF', 'text-halo-color': '#07111E', 'text-halo-width': 2 },
          });
          activeMap.moveLayer('active-well-pulse');
          activeMap.moveLayer('active-well-core');
          activeMap.moveLayer('active-well-label');

          // Click handling on offset wells
          if (!interactionsBound) {
            interactionsBound = true;
            activeMap.on('click', 'offset-wells-points', (e: MapLayerMouseEvent) => {
              if (e.features?.[0]) {
                const clickedId = e.features[0].properties.id;
                const latest = latestDataRef.current;
                const found = latest.wells.find((well) => well.id === clickedId);
                if (found) {
                  latest.onSelectWell(found);
                  activeMap.flyTo({ center: [found.lon, found.lat], zoom: 12.5, duration: 500, essential: true });
                }
              }
            });

            activeMap.on('mouseenter', 'offset-wells-points', () => {
              activeMap.getCanvas().style.cursor = 'pointer';
            });
            activeMap.on('mouseleave', 'offset-wells-points', () => {
              activeMap.getCanvas().style.cursor = '';
            });
          }

          activeMap.resize();
          const deltaLat = (current.radiusKm * 1.2) / 111;
          const deltaLon = (current.radiusKm * 1.2) / (111 * Math.cos((current.activeLocation.lat * Math.PI) / 180));
          activeMap.fitBounds([
            [current.activeLocation.lon - deltaLon, current.activeLocation.lat - deltaLat],
            [current.activeLocation.lon + deltaLon, current.activeLocation.lat + deltaLat],
          ], { padding: { top: 60, right: 48, bottom: 84, left: 48 }, maxZoom: 14, duration: 0 });
        });

        resizeObserver = new ResizeObserver(() => requestAnimationFrame(() => activeMap.resize()));
        resizeObserver.observe(mapContainerRef.current);
      } catch (err) {
        console.warn('MapLibre initialization failed; using the local vector map:', err);
        setWebglSupported(false);
      }
    }

    initMap();

    return () => {
      isCancelled = true;
      resizeObserver?.disconnect();
      if (mapRef.current) {
        mapRef.current.remove();
        mapRef.current = null;
      }
    };
  }, [getStyleDefinition]);

  useEffect(() => {
    if (!mapRef.current || !mapLoaded) return;
    const map = mapRef.current;

    (map.getSource('offset-wells-source') as GeoJSONSource | undefined)?.setData(wellsToGeoJSON(wells));

    if (map.getLayer('offset-wells-points')) {
      map.setPaintProperty('offset-wells-points', 'circle-radius', [
        'case',
        ['==', ['get', 'id'], selectedWell?.id || ''],
        11,
        8,
      ]);
      map.setPaintProperty('offset-wells-points', 'circle-stroke-width', [
        'case',
        ['==', ['get', 'id'], selectedWell?.id || ''],
        3.5,
        2,
      ]);
      map.setPaintProperty('offset-wells-points', 'circle-stroke-color', [
        'case', ['==', ['get', 'id'], selectedWell?.id || ''], '#67E8F9', '#FFFFFF',
      ]);
    }
  }, [wells, selectedWell, mapLoaded]);

  useEffect(() => {
    if (!mapRef.current || !mapLoaded) return;
    const map = mapRef.current;
    (map.getSource('radius-source') as GeoJSONSource | undefined)?.setData(
      createGeodesicRadiusGeoJSON(activeLocation.lon, activeLocation.lat, radiusKm)
    );
    (map.getSource('active-well-source') as GeoJSONSource | undefined)?.setData({
        type: 'FeatureCollection',
        features: [{
          type: 'Feature',
          geometry: { type: 'Point', coordinates: [activeLocation.lon, activeLocation.lat] },
          properties: { wellId: activeWellId },
        }],
      });
    const deltaLat = (radiusKm * 1.2) / 111;
    const deltaLon = (radiusKm * 1.2) / (111 * Math.cos((activeLocation.lat * Math.PI) / 180));
    map.fitBounds([
      [activeLocation.lon - deltaLon, activeLocation.lat - deltaLat],
      [activeLocation.lon + deltaLon, activeLocation.lat + deltaLat],
    ], { padding: { top: 60, right: 48, bottom: 84, left: 48 }, maxZoom: 14, duration: 450 });
  }, [radiusKm, activeLocation.lat, activeLocation.lon, activeWellId, mapLoaded]);

  // Handle Style Changes
  const handleStyleChange = (newStyle: MapStyleType) => {
    setMapStyle(newStyle);
    if (mapRef.current && mapLoaded) {
      try {
        mapRef.current.setStyle(getStyleDefinition(newStyle));
      } catch (e) {
        console.warn('Failed to switch MapLibre style:', e);
      }
    }
  };

  // Map Controls
  const handleZoomIn = () => {
    if (mapRef.current) {
      mapRef.current.zoomIn();
    } else {
      setFallbackZoom((prev) => Math.min(prev + 0.25, 3));
    }
  };

  const handleZoomOut = () => {
    if (mapRef.current) {
      mapRef.current.zoomOut();
    } else {
      setFallbackZoom((prev) => Math.max(prev - 0.25, 0.5));
    }
  };

  const handleCenterActiveWell = () => {
    if (!isValidGeoCoordinate(activeLocation.lat, activeLocation.lon)) return;
    if (mapRef.current) {
      mapRef.current.flyTo({
        center: [activeLocation.lon, activeLocation.lat],
        zoom: mapRef.current.getZoom(),
        duration: 500,
        essential: true,
      });
    } else {
      setFallbackPan({ x: 0, y: 0 });
      setFallbackZoom(1);
    }
  };

  // Convert GPS Coordinates to Local Metric Offsets for SVG Fallback
  const kmPerLat = 111.0;
  const kmPerLon = 111.0 * Math.cos((activeLocation.lat * Math.PI) / 180);
  const svgViewBoxKm = Math.max(radiusKm * 2.5, 12);
  const pxPerKm = 360 / svgViewBoxKm;

  return (
    <div className="relative h-full min-h-0 w-full overflow-hidden rounded-xl border border-slate-800 bg-[#090D16] shadow-2xl">
      {/* MapLibre WebGL Mount Container */}
      <div
        ref={mapContainerRef}
        className={`h-full w-full ${!webglSupported ? 'hidden' : 'block'}`}
      />

      {/* Deterministic Vector GIS Canvas (Always available & 100% stable fallback) */}
      {!webglSupported && (
        <div
          className="absolute inset-0 cursor-grab select-none active:cursor-grabbing"
          onMouseDown={(e) => {
            isDraggingRef.current = true;
            dragStartRef.current = { x: e.clientX - fallbackPan.x, y: e.clientY - fallbackPan.y };
          }}
          onMouseMove={(e) => {
            if (!isDraggingRef.current) return;
            setFallbackPan({
              x: e.clientX - dragStartRef.current.x,
              y: e.clientY - dragStartRef.current.y,
            });
          }}
          onMouseUp={() => {
            isDraggingRef.current = false;
          }}
          onMouseLeave={() => {
            isDraggingRef.current = false;
          }}
        >
          {/* Tactical Dark Grid Overlay */}
          <div className="absolute inset-0 bg-[linear-gradient(to_right,#1e293b22_1px,transparent_1px),linear-gradient(to_bottom,#1e293b22_1px,transparent_1px)] bg-[size:40px_40px]" />

          {/* SVG Map Scene */}
          <svg
            className="h-full w-full"
            viewBox="-250 -250 500 500"
            style={{
              transform: `translate(${fallbackPan.x}px, ${fallbackPan.y}px) scale(${fallbackZoom})`,
              transformOrigin: 'center center',
            }}
          >
            {/* Search Radius Circle */}
            <circle
              cx="0"
              cy="0"
              r={radiusKm * pxPerKm}
              fill="#06B6D4"
              fillOpacity="0.08"
              stroke="#06B6D4"
              strokeWidth="2"
              strokeDasharray="6, 4"
            />

            {/* Radar concentric reference rings */}
            <circle cx="0" cy="0" r={(radiusKm / 2) * pxPerKm} fill="none" stroke="#1e293b" strokeWidth="1" strokeDasharray="3, 3" />
            <line x1="-240" y1="0" x2="240" y2="0" stroke="#1e293b" strokeWidth="1" />
            <line x1="0" y1="-240" x2="0" y2="240" stroke="#1e293b" strokeWidth="1" />

            {/* Active Well Pulsing Marker */}
            <g transform="translate(0, 0)">
              <circle cx="0" cy="0" r="18" fill="#0284C7" fillOpacity="0.25" stroke="#38BDF8" strokeWidth="1.5" className="animate-ping" />
              <circle cx="0" cy="0" r="8" fill="#0EA5E9" stroke="#FFFFFF" strokeWidth="2.5" />
              <text x="0" y="-14" textAnchor="middle" fill="#38BDF8" fontSize="11" fontWeight="bold" fontFamily="monospace">
                ACTIVE • {activeWellId}
              </text>
            </g>

            {/* Offset Wells */}
            {wells.map((well) => {
              const dxKm = (well.lon - activeLocation.lon) * kmPerLon;
              const dyKm = (activeLocation.lat - well.lat) * kmPerLat;
              const cx = dxKm * pxPerKm;
              const cy = dyKm * pxPerKm;
              const isSelected = selectedWell?.id === well.id;

              const color =
                well.riskLevel === 'high'
                  ? '#EF4444'
                  : well.riskLevel === 'medium'
                  ? '#F59E0B'
                  : '#10B981';

              return (
                <g
                  key={well.id}
                  transform={`translate(${cx}, ${cy})`}
                  className="cursor-pointer transition-transform hover:scale-125"
                  onClick={() => onSelectWell(well)}
                >
                  {isSelected && (
                    <circle cx="0" cy="0" r="16" fill="none" stroke="#FFFFFF" strokeWidth="2" strokeDasharray="4, 2" />
                  )}
                  <circle
                    cx="0"
                    cy="0"
                    r={isSelected ? 10 : 7}
                    fill={color}
                    stroke="#FFFFFF"
                    strokeWidth={isSelected ? 3 : 1.5}
                  />
                  <text
                    x="0"
                    y="18"
                    textAnchor="middle"
                    fill="#FFFFFF"
                    fontSize="10"
                    fontWeight="bold"
                    fontFamily="monospace"
                  >
                    {well.name}
                  </text>
                  <text
                    x="0"
                    y="28"
                    textAnchor="middle"
                    fill="#94A3B8"
                    fontSize="8"
                    fontFamily="monospace"
                  >
                    {well.distanceKm} km
                  </text>
                </g>
              );
            })}
          </svg>
        </div>
      )}

      {/* Top Left: Map Style Switcher (MAP, SATELLITE, TERRAIN) */}
      <div className="absolute top-3 left-3 z-20 flex items-center rounded-lg border border-slate-700/80 bg-[#0B1120]/90 p-1 shadow-lg backdrop-blur-md">
        <button
          onClick={() => handleStyleChange('dark')}
          className={`rounded px-2.5 py-1 text-xs font-mono font-semibold transition ${
            mapStyle === 'dark'
              ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/40'
              : 'text-slate-400 hover:text-white'
          }`}
        >
          MAP
        </button>
        <button
          onClick={() => handleStyleChange('satellite')}
          className={`rounded px-2.5 py-1 text-xs font-mono font-semibold transition ${
            mapStyle === 'satellite'
              ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/40'
              : 'text-slate-400 hover:text-white'
          }`}
        >
          SATELLITE
        </button>
        <button
          onClick={() => handleStyleChange('terrain')}
          className={`rounded px-2.5 py-1 text-xs font-mono font-semibold transition ${
            mapStyle === 'terrain'
              ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/40'
              : 'text-slate-400 hover:text-white'
          }`}
        >
          TERRAIN
        </button>
      </div>

      <div className="absolute bottom-3 left-3 z-30 flex flex-col gap-2">
        <div className="flex flex-col overflow-hidden rounded-md border border-slate-300 bg-white shadow-md">
          <button
            onClick={handleZoomIn}
            aria-label="Zoom in"
            title="Zoom in"
            className="border-b border-slate-200 p-2 text-slate-800 transition hover:bg-slate-100"
          >
            <Plus className="h-4 w-4" />
          </button>
          <button
            onClick={handleZoomOut}
            aria-label="Zoom out"
            title="Zoom out"
            className="p-2 text-slate-800 transition hover:bg-slate-100"
          >
            <Minus className="h-4 w-4" />
          </button>
        </div>

        <button
          onClick={handleCenterActiveWell}
          title="Center on Active Well"
          aria-label="Center on Active Well"
          className="flex h-9 w-9 items-center justify-center rounded-md border border-slate-300 bg-white text-slate-800 shadow-md transition hover:bg-slate-100"
        >
          <Crosshair className="h-4 w-4" />
        </button>

        <button
          onClick={onToggleExpanded}
          title={isExpanded ? 'Restore split map' : 'Expand map'}
          aria-label={isExpanded ? 'Restore split map' : 'Expand map'}
          className="flex h-9 w-9 items-center justify-center rounded-md border border-slate-300 bg-white text-slate-800 shadow-md transition hover:bg-slate-100"
        >
          {isExpanded ? <Minimize2 className="h-4 w-4" /> : <Maximize2 className="h-4 w-4" />}
        </button>
      </div>

      {/* Bottom Left: Map Legend */}
      <div className="absolute bottom-3 left-14 z-20 flex max-w-[calc(100%-4.5rem)] flex-wrap items-center gap-x-3 gap-y-1 rounded-lg border border-slate-800/90 bg-[#0B1120]/90 px-3 py-1.5 font-mono text-[10px] text-slate-300 shadow-xl backdrop-blur-md">
        <span className="flex items-center gap-1.5 text-cyan-300 font-bold">
          <span className="h-2.5 w-2.5 rounded-full bg-cyan-400 ring-2 ring-cyan-500/40" />
          Active Rig
        </span>
        <span className="flex items-center gap-1.5 text-red-300">
          <span className="h-2.5 w-2.5 rounded-full bg-red-500" />
          High Risk
        </span>
        <span className="flex items-center gap-1.5 text-amber-300">
          <span className="h-2.5 w-2.5 rounded-full bg-amber-500" />
          Medium Risk
        </span>
        <span className="flex items-center gap-1.5 text-emerald-300">
          <span className="h-2.5 w-2.5 rounded-full bg-emerald-500" />
          Low Risk
        </span>
        <span className="flex items-center gap-1.5 text-cyan-400">
          <span className="h-2 w-2 rounded-full border border-dashed border-cyan-400" />
          {radiusKm} km Radius
        </span>
      </div>

      {/* Bottom Right: Spatial Metadata & North Arrow */}
      <div className="absolute bottom-3 right-3 z-20 flex items-center gap-2 rounded-lg border border-slate-800/90 bg-[#0B1120]/90 px-2.5 py-1 font-mono text-[10px] text-slate-400 shadow-lg backdrop-blur-md">
        <Compass className="h-3.5 w-3.5 text-cyan-400 animate-spin-slow" />
        <span>N 0°</span>
        <span className="text-slate-600">|</span>
        <span>WGS84 EPSG:4326</span>
        <span className="text-slate-600">|</span>
        <span className="text-cyan-400">MapLibre GL</span>
      </div>
    </div>
  );
};
