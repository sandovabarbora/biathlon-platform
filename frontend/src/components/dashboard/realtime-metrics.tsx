'use client';

import { useAthleteStore } from '@/lib/store/athlete-store';
import { motion } from 'framer-motion';

export function RealtimeMetrics() {
  const { realtimeData } = useAthleteStore();

  const metrics = [
    {
      label: 'Heart Rate',
      value: realtimeData?.heart_rate?.toFixed(0) || '--',
      unit: 'bpm',
      color: getHeartRateColor(realtimeData?.heart_rate),
    },
    {
      label: 'Lactate',
      value: realtimeData?.lactate_estimated?.toFixed(1) || '--',
      unit: 'mmol/L',
      color: getLactateColor(realtimeData?.lactate_estimated),
    },
    {
      label: 'Speed',
      value: realtimeData?.speed?.toFixed(1) || '--',
      unit: 'km/h',
      color: 'var(--primary)',
    },
    {
      label: 'Fatigue',
      value: realtimeData?.fatigue_index 
        ? `${(realtimeData.fatigue_index * 100).toFixed(0)}%`
        : '--',
      unit: '',
      color: getFatigueColor(realtimeData?.fatigue_index),
    },
  ];

  return (
    <>
      {metrics.map((metric, index) => (
        <motion.div
          key={metric.label}
          className="card"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: index * 0.1 }}
        >
          <div className="metric">
            <span className="metric-label">{metric.label}</span>
            <div style={{ display: 'flex', alignItems: 'baseline' }}>
              <span 
                className="metric-value" 
                style={{ color: metric.color }}
              >
                {metric.value}
              </span>
              {metric.unit && (
                <span className="metric-unit">{metric.unit}</span>
              )}
            </div>
          </div>
        </motion.div>
      ))}
    </>
  );
}

function getHeartRateColor(hr?: number): string {
  if (!hr) return 'var(--muted)';
  if (hr < 120) return 'var(--success)';
  if (hr < 160) return 'var(--primary)';
  if (hr < 180) return 'var(--warning)';
  return 'var(--error)';
}

function getLactateColor(lactate?: number): string {
  if (!lactate) return 'var(--muted)';
  if (lactate < 2) return 'var(--success)';
  if (lactate < 4) return 'var(--warning)';
  return 'var(--error)';
}

function getFatigueColor(fatigue?: number): string {
  if (!fatigue) return 'var(--muted)';
  if (fatigue < 0.3) return 'var(--success)';
  if (fatigue < 0.7) return 'var(--warning)';
  return 'var(--error)';
}
