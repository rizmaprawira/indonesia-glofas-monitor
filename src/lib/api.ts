import type { Metadata, PointsIndex, PointTimeseries, TopPoints } from './types';

const DATA_BASE_URL = './data/latest';

export async function fetchMetadata(): Promise<Metadata> {
  const res = await fetch(`${DATA_BASE_URL}/metadata.json`);
  if (!res.ok) {
    throw new Error(`Failed to fetch metadata: ${res.status}`);
  }
  return res.json();
}

export async function fetchPointsIndex(): Promise<PointsIndex> {
  const res = await fetch(`${DATA_BASE_URL}/points-index.json`);
  if (!res.ok) {
    throw new Error(`Failed to fetch points index: ${res.status}`);
  }
  return res.json();
}

export async function fetchPointTimeseries(pointId: string): Promise<PointTimeseries> {
  const res = await fetch(`${DATA_BASE_URL}/timeseries/${pointId}.json`);
  if (!res.ok) {
    throw new Error(`Failed to fetch timeseries for ${pointId}: ${res.status}`);
  }
  return res.json();
}

export async function fetchTopPoints(leadTime: number, metric: string): Promise<TopPoints> {
  const res = await fetch(`${DATA_BASE_URL}/top-points-${leadTime}-${metric}.json`);
  if (!res.ok) {
    // Fall back to generic top points
    const fallbackRes = await fetch(`${DATA_BASE_URL}/top-points.json`);
    if (!fallbackRes.ok) {
      throw new Error(`Failed to fetch top points: ${res.status}`);
    }
    return fallbackRes.json();
  }
  return res.json();
}

export async function fetchAllPointValues(leadTime: number): Promise<Map<string, Record<string, number>>> {
  const res = await fetch(`${DATA_BASE_URL}/values-${leadTime}.json`);
  if (!res.ok) {
    throw new Error(`Failed to fetch values for lead time ${leadTime}: ${res.status}`);
  }
  const data = await res.json();
  return new Map(Object.entries(data));
}
