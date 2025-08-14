'use client';

import { useMemo } from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ReferenceLine,
} from 'recharts';
import { format } from 'date-fns';

interface Props {
  data: any;
}

export function HeartRateChart({ data }: Props) {
  const chartData = useMemo(() => {
    if (!data?.sensor_data) return [];
    
    return data.sensor_data.map((d: any) => ({
      time: new Date(d.timestamp),
      hr: d.heart_rate,
      lactate: d.lactate_estimated,
      zone: getHRZone(d.heart_rate),
    }));
  }, [data]);

  const zones = [
    { name: 'Recovery', min: 0, max: 120, color: '#16a34a20' },
    { name: 'Aerobic', min: 120, max: 150, color: '#3b82f620' },
    { name: 'Threshold', min: 150, max: 170, color: '#f59e0b20' },
    { name: 'VO2 Max', min: 170, max: 190, color: '#dc262620' },
  ];

  return (
    <div className="card">
      <div className="card-header">
        <h3>Heart Rate & Lactate</h3>
        <span className="badge badge-success">Live</span>
      </div>

      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={chartData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
          
          {/* HR Zones */}
          {zones.map((zone) => (
            <ReferenceLine
              key={zone.name}
              y={zone.max}
              stroke="transparent"
              fill={zone.color}
              fillOpacity={0.5}
            />
          ))}

          <XAxis
            dataKey="time"
            tickFormatter={(time) => format(new Date(time), 'HH:mm')}
            stroke="var(--muted)"
          />
          
          <YAxis
            yAxisId="hr"
            domain={[60, 200]}
            stroke="var(--primary)"
            label={{ value: 'Heart Rate (bpm)', angle: -90, position: 'insideLeft' }}
          />
          
          <YAxis
            yAxisId="lactate"
            orientation="right"
            domain={[0, 10]}
            stroke="var(--secondary)"
            label={{ value: 'Lactate (mmol/L)', angle: 90, position: 'insideRight' }}
          />

          <Tooltip
            contentStyle={{
              background: 'var(--background)',
              border: '1px solid var(--border)',
              borderRadius: 'var(--radius)',
            }}
            labelFormatter={(time) => format(new Date(time), 'HH:mm:ss')}
          />
          
          <Legend />
          
          <Line
            yAxisId="hr"
            type="monotone"
            dataKey="hr"
            stroke="var(--primary)"
            strokeWidth={2}
            dot={false}
            name="Heart Rate"
          />
          
          <Line
            yAxisId="lactate"
            type="monotone"
            dataKey="lactate"
            stroke="var(--secondary)"
            strokeWidth={2}
            dot={false}
            name="Lactate"
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}

function getHRZone(hr: number): string {
  if (hr < 120) return 'Recovery';
  if (hr < 150) return 'Aerobic';
  if (hr < 170) return 'Threshold';
  return 'VO2 Max';
}
