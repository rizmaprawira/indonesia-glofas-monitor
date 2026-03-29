export interface Metadata {
  forecastRunDate: string;
  pipelineTimestamp: string;
  dataVersion: string;
  leadTimes: number[];
  metrics: string[];
  pointCount: number;
  boundingBox: BoundingBox;
}

export interface BoundingBox {
  north: number;
  south: number;
  east: number;
  west: number;
}

export interface MonitoringPoint {
  id: string;
  lat: number;
  lon: number;
  name?: string;
  values: Record<number, PointValues>;  // leadTime -> values
}

export interface PointValues {
  control?: number;
  min: number;
  max: number;
  mean: number;
  p10: number;
  p25: number;
  p50: number;
  p75: number;
  p90: number;
}

export interface PointsIndex {
  points: MonitoringPointSummary[];
}

export interface MonitoringPointSummary {
  id: string;
  lat: number;
  lon: number;
  name?: string;
}

export interface TopPoints {
  leadTime: number;
  metric: string;
  points: TopPointEntry[];
}

export interface TopPointEntry {
  id: string;
  lat: number;
  lon: number;
  value: number;
  rank: number;
}

export interface PointTimeseries {
  id: string;
  lat: number;
  lon: number;
  name?: string;
  timeseries: TimeseriesEntry[];
}

export interface TimeseriesEntry {
  leadTime: number;
  control?: number;
  min: number;
  max: number;
  mean: number;
  p10: number;
  p25: number;
  p50: number;
  p75: number;
  p90: number;
}

export type Metric = 'control' | 'min' | 'max' | 'mean' | 'p10' | 'p25' | 'p50' | 'p75' | 'p90';

export interface AppConfig {
  appName: string;
  description: string;
  version: string;
  mapDefaults: {
    center: [number, number];
    zoom: number;
    minZoom: number;
    maxZoom: number;
  };
  leadTimes: number[];
  defaultLeadTime: number;
  defaultMetric: Metric;
  metrics: Metric[];
  topPointsCount: number;
  colorScale: {
    thresholds: number[];
    colors: string[];
  };
  refreshIntervalMs: number;
}
