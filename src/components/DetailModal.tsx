import { useEffect, useState } from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Filler,
  Title,
  Tooltip,
  Legend
} from 'chart.js';
import { Line } from 'react-chartjs-2';
import { fetchPointTimeseries } from '../lib/api';
import { formatCoordinate, formatLeadTime, generateCSV, downloadCSV } from '../lib/utils';
import type { MonitoringPointSummary, PointTimeseries } from '../lib/types';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Filler,
  Title,
  Tooltip,
  Legend
);

interface DetailModalProps {
  pointId: string;
  points: MonitoringPointSummary[];
  leadTimes: number[];
  onClose: () => void;
}

export function DetailModal({ pointId, points, leadTimes: _leadTimes, onClose }: DetailModalProps) {
  const [timeseries, setTimeseries] = useState<PointTimeseries | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const point = points.find(p => p.id === pointId);

  useEffect(() => {
    setLoading(true);
    setError(null);
    
    fetchPointTimeseries(pointId)
      .then(setTimeseries)
      .catch(err => setError(err.message))
      .finally(() => setLoading(false));
  }, [pointId]);

  const handleDownload = () => {
    if (!timeseries) return;
    
    const data = timeseries.timeseries.map(t => ({
      leadTime: t.leadTime,
      control: t.control ?? '',
      min: t.min,
      max: t.max,
      mean: t.mean,
      p10: t.p10,
      p25: t.p25,
      p50: t.p50,
      p75: t.p75,
      p90: t.p90
    }));
    
    const csv = generateCSV(data, ['leadTime', 'control', 'min', 'max', 'mean', 'p10', 'p25', 'p50', 'p75', 'p90']);
    downloadCSV(csv, `glofas-${pointId}.csv`);
  };

  const chartData = timeseries ? {
    labels: timeseries.timeseries.map(t => formatLeadTime(t.leadTime)),
    datasets: [
      {
        label: 'P10-P90 Range',
        data: timeseries.timeseries.map(t => t.p90),
        fill: '+1',
        backgroundColor: 'rgba(33, 102, 172, 0.1)',
        borderColor: 'transparent',
        pointRadius: 0
      },
      {
        label: 'P10',
        data: timeseries.timeseries.map(t => t.p10),
        fill: false,
        borderColor: 'rgba(33, 102, 172, 0.3)',
        borderWidth: 1,
        pointRadius: 0
      },
      {
        label: 'P50 (Median)',
        data: timeseries.timeseries.map(t => t.p50),
        fill: false,
        borderColor: '#2166ac',
        borderWidth: 2,
        pointRadius: 3,
        pointBackgroundColor: '#2166ac'
      },
      {
        label: 'Control',
        data: timeseries.timeseries.map(t => t.control ?? null),
        fill: false,
        borderColor: '#d6604d',
        borderWidth: 2,
        borderDash: [5, 5],
        pointRadius: 2,
        pointBackgroundColor: '#d6604d'
      }
    ]
  } : null;

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top' as const,
        labels: {
          filter: (item: { text: string }) => !item.text.includes('P10')
        }
      },
      tooltip: {
        mode: 'index' as const,
        intersect: false
      }
    },
    scales: {
      x: {
        title: {
          display: true,
          text: 'Lead Time'
        }
      },
      y: {
        title: {
          display: true,
          text: 'Discharge (m³/s)'
        },
        beginAtZero: true
      }
    }
  };

  return (
    <div className="detail-modal" onClick={onClose}>
      <div className="detail-content" onClick={e => e.stopPropagation()}>
        <div className="detail-header">
          <h2>{point?.name || pointId}</h2>
          <button className="close-btn" onClick={onClose}>&times;</button>
        </div>
        
        <div className="detail-body">
          {loading && (
            <div className="loading-overlay" style={{ position: 'relative', height: 200 }}>
              <div className="loading-spinner" />
            </div>
          )}
          
          {error && (
            <div className="error-banner">{error}</div>
          )}
          
          {point && (
            <div className="detail-meta">
              <div className="meta-item">
                <div className="meta-label">Point ID</div>
                <div className="meta-value">{point.id}</div>
              </div>
              <div className="meta-item">
                <div className="meta-label">Latitude</div>
                <div className="meta-value">{formatCoordinate(point.lat, true)}</div>
              </div>
              <div className="meta-item">
                <div className="meta-label">Longitude</div>
                <div className="meta-value">{formatCoordinate(point.lon, false)}</div>
              </div>
              {timeseries && (
                <div className="meta-item">
                  <div className="meta-label">Current P50</div>
                  <div className="meta-value">
                    {timeseries.timeseries[0]?.p50.toFixed(1) ?? 'N/A'} m³/s
                  </div>
                </div>
              )}
            </div>
          )}
          
          {chartData && (
            <div className="chart-container">
              <Line data={chartData} options={chartOptions} />
            </div>
          )}
          
          {timeseries && (
            <button className="download-btn" onClick={handleDownload}>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
                <polyline points="7,10 12,15 17,10" />
                <line x1="12" y1="15" x2="12" y2="3" />
              </svg>
              Download CSV
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
