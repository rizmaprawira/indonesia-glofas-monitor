import type { Metric } from '../lib/types';
import { formatLeadTime, formatDischarge, getColorForValue } from '../lib/utils';
import appConfig from '../../config/app.config.json';

interface TopPointDisplay {
  id: string;
  lat: number;
  lon: number;
  name?: string;
  value: number;
}

interface SidebarProps {
  leadTimes: number[];
  metrics: Metric[];
  selectedLeadTime: number;
  selectedMetric: Metric;
  onLeadTimeChange: (lt: number) => void;
  onMetricChange: (m: Metric) => void;
  searchQuery: string;
  onSearchChange: (q: string) => void;
  topPoints: TopPointDisplay[];
  selectedPointId: string | null;
  onPointSelect: (id: string) => void;
  colorScale: { thresholds: number[]; colors: string[] };
}

export function Sidebar({
  leadTimes,
  metrics,
  selectedLeadTime,
  selectedMetric,
  onLeadTimeChange,
  onMetricChange,
  searchQuery,
  onSearchChange,
  topPoints,
  selectedPointId,
  onPointSelect,
  colorScale
}: SidebarProps) {
  return (
    <aside className="sidebar">
      <div className="control-panel">
        <div className="control-group">
          <label className="control-label">Lead Time</label>
          <select
            className="control-select"
            value={selectedLeadTime}
            onChange={e => onLeadTimeChange(Number(e.target.value))}
          >
            {leadTimes.map(lt => (
              <option key={lt} value={lt}>
                {formatLeadTime(lt)} ({lt}h)
              </option>
            ))}
          </select>
        </div>
        
        <div className="control-group">
          <label className="control-label">Metric</label>
          <select
            className="control-select"
            value={selectedMetric}
            onChange={e => onMetricChange(e.target.value as Metric)}
          >
            {metrics.map(m => (
              <option key={m} value={m}>
                {m === 'control' ? 'Control Forecast' : m.toUpperCase()}
              </option>
            ))}
          </select>
        </div>
        
        <div className="control-group">
          <label className="control-label">Search Points</label>
          <input
            type="text"
            className="search-input"
            placeholder="Search by ID or location..."
            value={searchQuery}
            onChange={e => onSearchChange(e.target.value)}
          />
        </div>
      </div>
      
      <div className="top-points-panel">
        <h3 className="panel-title">
          Top {topPoints.length} Points by {selectedMetric.toUpperCase()}
        </h3>
        
        {topPoints.length === 0 ? (
          <div className="empty-state">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <circle cx="11" cy="11" r="8" />
              <path d="m21 21-4.35-4.35" />
            </svg>
            <p>No points found</p>
          </div>
        ) : (
          <ul className="point-list">
            {topPoints.map((point, idx) => (
              <li
                key={point.id}
                className={`point-item ${selectedPointId === point.id ? 'active' : ''}`}
                onClick={() => onPointSelect(point.id)}
              >
                <span className="point-rank">{idx + 1}</span>
                <div className="point-info">
                  <div className="point-id">{point.name || point.id}</div>
                  <div className="point-value">
                    {formatDischarge(point.value)} m³/s
                  </div>
                </div>
                <div
                  style={{
                    width: 12,
                    height: 12,
                    borderRadius: '50%',
                    backgroundColor: getColorForValue(point.value, appConfig as any)
                  }}
                />
              </li>
            ))}
          </ul>
        )}
      </div>
      
      <div className="legend">
        <div className="legend-title">Discharge (m³/s)</div>
        <div className="legend-scale">
          {colorScale.colors.map((color, idx) => (
            <div
              key={idx}
              className="legend-segment"
              style={{ backgroundColor: color }}
            />
          ))}
        </div>
        <div className="legend-labels">
          {colorScale.thresholds.filter((_, i) => i % 2 === 0).map(t => (
            <span key={t}>{t}</span>
          ))}
        </div>
      </div>
    </aside>
  );
}
