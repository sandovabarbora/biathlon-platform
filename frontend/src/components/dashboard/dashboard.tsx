'use client';

import { useQuery } from '@tanstack/react-query';
import { useWebSocket } from '@/hooks/use-websocket';
import { sensorsApi } from '@/lib/api/sensors';
import { RealtimeMetrics } from './realtime-metrics';
import { ShootingPredictor } from './shooting-predictor';
import { HeartRateChart } from './heart-rate-chart';
import { ApproachOptimizer } from './approach-optimizer';
import { FatigueMonitor } from './fatigue-monitor';
import { ActivityMap } from './activity-map';

interface DashboardProps {
  athleteId: number;
}

export function Dashboard({ athleteId }: DashboardProps) {
  const { isConnected } = useWebSocket(athleteId);

  // Fetch historical data
  const { data: historicalData } = useQuery({
    queryKey: ['sensorData', athleteId],
    queryFn: () => sensorsApi.getLast24Hours(athleteId),
    refetchInterval: 60000, // 1 minute
  });

  return (
    <div style={{ marginTop: '2rem' }}>
      {/* Connection Status */}
      <div style={{ marginBottom: '1rem', display: 'flex', alignItems: 'center' }}>
        <span className={`status-indicator ${isConnected ? 'status-online' : 'status-offline'}`} />
        <span style={{ fontSize: '0.875rem', color: 'var(--muted)' }}>
          {isConnected ? 'Live Data' : 'Disconnected'}
        </span>
      </div>

      {/* Metrics Grid */}
      <div className="grid grid-4" style={{ marginBottom: '2rem' }}>
        <RealtimeMetrics />
      </div>

      {/* Main Content */}
      <div className="grid grid-2" style={{ marginBottom: '2rem' }}>
        <ShootingPredictor athleteId={athleteId} />
        <ApproachOptimizer athleteId={athleteId} />
      </div>

      {/* Charts */}
      <div className="grid grid-2" style={{ marginBottom: '2rem' }}>
        <HeartRateChart data={historicalData} />
        <FatigueMonitor athleteId={athleteId} />
      </div>

      {/* Activity Map */}
      <ActivityMap athleteId={athleteId} />
    </div>
  );
}
