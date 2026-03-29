import type { Metadata } from '../lib/types';
import { formatDate } from '../lib/utils';

interface HeaderProps {
  metadata: Metadata | null;
}

export function Header({ metadata }: HeaderProps) {
  return (
    <header className="header">
      <h1>
        <svg viewBox="0 0 100 100" fill="currentColor">
          <circle cx="50" cy="50" r="45" />
          <path d="M30 55 Q40 35 50 55 Q60 75 70 55" stroke="white" strokeWidth="4" fill="none" />
        </svg>
        Indonesia GloFAS Monitor
      </h1>
      
      <div className="header-meta">
        {metadata ? (
          <>
            <span>Forecast: {formatDate(metadata.forecastRunDate)}</span>
            <span>Updated: {formatDate(metadata.pipelineTimestamp)}</span>
            <span>{metadata.pointCount} monitoring points</span>
          </>
        ) : (
          <span>Loading...</span>
        )}
      </div>
    </header>
  );
}
