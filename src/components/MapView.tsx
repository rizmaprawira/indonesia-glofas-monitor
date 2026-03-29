import { useEffect, useRef } from 'react';
import L from 'leaflet';
import type { MonitoringPointSummary, Metric, AppConfig } from '../lib/types';
import { getColorForValue, getRadiusForValue, formatDischarge } from '../lib/utils';

// Indonesia outline (simplified)
const INDONESIA_BOUNDS: L.LatLngBoundsExpression = [
  [-12, 94],
  [8, 142]
];

interface MapViewProps {
  points: MonitoringPointSummary[];
  pointValues: Map<string, Record<string, number>>;
  selectedMetric: Metric;
  selectedPointId: string | null;
  onPointSelect: (id: string) => void;
  config: AppConfig;
}

export function MapView({
  points,
  pointValues,
  selectedMetric,
  selectedPointId,
  onPointSelect,
  config
}: MapViewProps) {
  const mapRef = useRef<L.Map | null>(null);
  const markersRef = useRef<L.CircleMarker[]>([]);
  const containerRef = useRef<HTMLDivElement>(null);

  // Initialize map
  useEffect(() => {
    if (!containerRef.current || mapRef.current) return;

    const map = L.map(containerRef.current, {
      center: config.mapDefaults.center as L.LatLngExpression,
      zoom: config.mapDefaults.zoom,
      minZoom: config.mapDefaults.minZoom,
      maxZoom: config.mapDefaults.maxZoom,
      maxBounds: INDONESIA_BOUNDS,
      maxBoundsViscosity: 0.8
    });

    L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', {
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OSM</a> &copy; <a href="https://carto.com/">CARTO</a>',
      subdomains: 'abcd',
      maxZoom: 19
    }).addTo(map);

    // Add Indonesia country outline (simplified rectangle for now)
    L.rectangle(INDONESIA_BOUNDS, {
      color: '#2166ac',
      weight: 2,
      fill: false,
      dashArray: '5, 5'
    }).addTo(map);

    mapRef.current = map;

    return () => {
      map.remove();
      mapRef.current = null;
    };
  }, [config]);

  // Update markers when data changes
  useEffect(() => {
    const map = mapRef.current;
    if (!map) return;

    // Clear existing markers
    markersRef.current.forEach(m => m.remove());
    markersRef.current = [];

    // Add new markers
    points.forEach(point => {
      const values = pointValues.get(point.id);
      const value = values?.[selectedMetric] ?? 0;
      const color = getColorForValue(value, config);
      const radius = getRadiusForValue(value);

      const marker = L.circleMarker([point.lat, point.lon], {
        radius,
        fillColor: color,
        color: selectedPointId === point.id ? '#000' : '#fff',
        weight: selectedPointId === point.id ? 3 : 1,
        fillOpacity: 0.8
      });

      marker.bindTooltip(`
        <div class="tooltip">
          <div class="tooltip-title">${point.name || point.id}</div>
          <div class="tooltip-row">
            <span class="tooltip-label">Discharge:</span>
            <span>${formatDischarge(value)} m³/s</span>
          </div>
          <div class="tooltip-row">
            <span class="tooltip-label">Location:</span>
            <span>${point.lat.toFixed(3)}, ${point.lon.toFixed(3)}</span>
          </div>
        </div>
      `, { className: '' });

      marker.on('click', () => onPointSelect(point.id));
      marker.addTo(map);
      markersRef.current.push(marker);
    });
  }, [points, pointValues, selectedMetric, selectedPointId, onPointSelect, config]);

  // Pan to selected point
  useEffect(() => {
    const map = mapRef.current;
    if (!map || !selectedPointId) return;

    const point = points.find(p => p.id === selectedPointId);
    if (point) {
      map.panTo([point.lat, point.lon]);
    }
  }, [selectedPointId, points]);

  return <div ref={containerRef} style={{ width: '100%', height: '100%' }} />;
}
