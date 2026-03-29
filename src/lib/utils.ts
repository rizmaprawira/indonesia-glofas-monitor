import type { AppConfig } from './types';

export function getColorForValue(value: number, config: AppConfig): string {
  const { thresholds, colors } = config.colorScale;
  
  for (let i = thresholds.length - 1; i >= 0; i--) {
    if (value >= thresholds[i]) {
      return colors[Math.min(i, colors.length - 1)];
    }
  }
  
  return colors[0];
}

export function getRadiusForValue(value: number): number {
  if (value < 50) return 4;
  if (value < 100) return 5;
  if (value < 500) return 6;
  if (value < 1000) return 7;
  if (value < 5000) return 8;
  return 10;
}

export function formatDischarge(value: number | undefined): string {
  if (value === undefined || value === null) return 'N/A';
  if (value < 1) return value.toFixed(2);
  if (value < 10) return value.toFixed(1);
  if (value < 1000) return Math.round(value).toString();
  return value.toLocaleString('en-US', { maximumFractionDigits: 0 });
}

export function formatLeadTime(hours: number): string {
  const days = Math.floor(hours / 24);
  if (days === 1) return '1 day';
  return `${days} days`;
}

export function formatDate(dateStr: string): string {
  try {
    const date = new Date(dateStr);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  } catch {
    return dateStr;
  }
}

export function formatCoordinate(value: number, isLat: boolean): string {
  const dir = isLat 
    ? (value >= 0 ? 'N' : 'S')
    : (value >= 0 ? 'E' : 'W');
  return `${Math.abs(value).toFixed(4)}° ${dir}`;
}

export function generateCSV(data: Array<Record<string, unknown>>, columns: string[]): string {
  const header = columns.join(',');
  const rows = data.map(row => 
    columns.map(col => {
      const val = row[col];
      if (typeof val === 'string' && val.includes(',')) {
        return `"${val}"`;
      }
      return val ?? '';
    }).join(',')
  );
  return [header, ...rows].join('\n');
}

export function downloadCSV(content: string, filename: string): void {
  const blob = new Blob([content], { type: 'text/csv;charset=utf-8;' });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  link.click();
  URL.revokeObjectURL(url);
}
