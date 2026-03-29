import { useState, useEffect, useCallback } from 'react';
import { Header } from './components/Header';
import { Sidebar } from './components/Sidebar';
import { MapView } from './components/MapView';
import { DetailModal } from './components/DetailModal';
import { fetchMetadata, fetchPointsIndex, fetchAllPointValues } from './lib/api';
import type { Metadata, MonitoringPointSummary, Metric, AppConfig } from './lib/types';
import appConfigJson from '../config/app.config.json';

// Cast config to proper type
const appConfig = appConfigJson as unknown as AppConfig;

export default function App() {
  const [metadata, setMetadata] = useState<Metadata | null>(null);
  const [points, setPoints] = useState<MonitoringPointSummary[]>([]);
  const [pointValues, setPointValues] = useState<Map<string, Record<string, number>>>(new Map());
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  const [selectedLeadTime, setSelectedLeadTime] = useState(appConfig.defaultLeadTime);
  const [selectedMetric, setSelectedMetric] = useState<Metric>(appConfig.defaultMetric as Metric);
  const [selectedPointId, setSelectedPointId] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');

  const loadData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      
      const [meta, pointsData] = await Promise.all([
        fetchMetadata(),
        fetchPointsIndex()
      ]);
      
      setMetadata(meta);
      setPoints(pointsData.points);
      
      // Load values for current lead time
      const values = await fetchAllPointValues(selectedLeadTime);
      setPointValues(values);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load data');
    } finally {
      setLoading(false);
    }
  }, [selectedLeadTime]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  useEffect(() => {
    // Reload values when lead time changes
    if (metadata) {
      fetchAllPointValues(selectedLeadTime)
        .then(setPointValues)
        .catch(err => console.error('Failed to load values:', err));
    }
  }, [selectedLeadTime, metadata]);

  const filteredPoints = points.filter(p => {
    if (!searchQuery) return true;
    const query = searchQuery.toLowerCase();
    return (
      p.id.toLowerCase().includes(query) ||
      p.name?.toLowerCase().includes(query) ||
      `${p.lat.toFixed(2)}, ${p.lon.toFixed(2)}`.includes(query)
    );
  });

  const topPoints = [...filteredPoints]
    .map(p => ({
      ...p,
      value: pointValues.get(p.id)?.[selectedMetric] ?? 0
    }))
    .sort((a, b) => b.value - a.value)
    .slice(0, appConfig.topPointsCount);

  return (
    <div className="app-container">
      <Header metadata={metadata} />
      
      <main className="main-content">
        <Sidebar
          leadTimes={appConfig.leadTimes}
          metrics={appConfig.metrics as Metric[]}
          selectedLeadTime={selectedLeadTime}
          selectedMetric={selectedMetric}
          onLeadTimeChange={setSelectedLeadTime}
          onMetricChange={setSelectedMetric}
          searchQuery={searchQuery}
          onSearchChange={setSearchQuery}
          topPoints={topPoints}
          selectedPointId={selectedPointId}
          onPointSelect={setSelectedPointId}
          colorScale={appConfig.colorScale}
        />
        
        <div className="map-container">
          {loading && (
            <div className="loading-overlay">
              <div className="loading-spinner" />
            </div>
          )}
          
          {error && (
            <div className="error-banner">
              {error}. <button onClick={loadData}>Retry</button>
            </div>
          )}
          
          <MapView
            points={filteredPoints}
            pointValues={pointValues}
            selectedMetric={selectedMetric}
            selectedPointId={selectedPointId}
            onPointSelect={setSelectedPointId}
            config={appConfig}
          />
        </div>
      </main>
      
      {selectedPointId && (
        <DetailModal
          pointId={selectedPointId}
          points={points}
          leadTimes={appConfig.leadTimes}
          onClose={() => setSelectedPointId(null)}
        />
      )}
    </div>
  );
}
