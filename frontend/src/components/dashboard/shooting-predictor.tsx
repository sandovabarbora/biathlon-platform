'use client';

import { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { predictionsApi } from '@/lib/api/predictions';
import { useAthleteStore } from '@/lib/store/athlete-store';
import { motion, AnimatePresence } from 'framer-motion';
import toast from 'react-hot-toast';

interface Props {
  athleteId: number;
}

export function ShootingPredictor({ athleteId }: Props) {
  const { realtimeData } = useAthleteStore();
  const [position, setPosition] = useState<'prone' | 'standing'>('prone');
  const [boutNumber, setBoutNumber] = useState(1);
  const [prediction, setPrediction] = useState<any>(null);

  const predictMutation = useMutation({
    mutationFn: (data: any) => 
      predictionsApi.predictShooting(athleteId, data),
    onSuccess: (data) => {
      setPrediction(data);
      if (data.predicted_accuracy < 0.8) {
        toast.warning('Low accuracy predicted!');
      }
    },
  });

  const handlePredict = () => {
    if (!realtimeData) {
      toast.error('No real-time data available');
      return;
    }

    predictMutation.mutate({
      position,
      bout_number: boutNumber,
      current_heart_rate: realtimeData.heart_rate || 150,
      current_lactate: realtimeData.lactate_estimated,
      wind_speed: realtimeData.wind_speed || 0,
      wind_direction: realtimeData.wind_direction || 0,
      temperature: realtimeData.temperature || 0,
    });
  };

  return (
    <div className="card">
      <div className="card-header">
        <h3>Shooting Prediction</h3>
        <span className="badge badge-success">Ready</span>
      </div>

      <div style={{ marginBottom: '1.5rem' }}>
        <div style={{ marginBottom: '1rem' }}>
          <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.875rem' }}>
            Position
          </label>
          <div style={{ display: 'flex', gap: '0.5rem' }}>
            <button
              className={`btn ${position === 'prone' ? 'btn-primary' : 'btn-secondary'}`}
              onClick={() => setPosition('prone')}
            >
              Prone
            </button>
            <button
              className={`btn ${position === 'standing' ? 'btn-primary' : 'btn-secondary'}`}
              onClick={() => setPosition('standing')}
            >
              Standing
            </button>
          </div>
        </div>

        <div style={{ marginBottom: '1rem' }}>
          <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.875rem' }}>
            Bout Number
          </label>
          <select
            value={boutNumber}
            onChange={(e) => setBoutNumber(Number(e.target.value))}
            style={{
              width: '100%',
              padding: '0.5rem',
              border: '1px solid var(--border)',
              borderRadius: 'var(--radius)',
            }}
          >
            {[1, 2, 3, 4, 5].map((n) => (
              <option key={n} value={n}>
                Bout {n}
              </option>
            ))}
          </select>
        </div>

        <button
          className="btn btn-primary"
          onClick={handlePredict}
          disabled={predictMutation.isPending}
          style={{ width: '100%' }}
        >
          {predictMutation.isPending ? 'Predicting...' : 'Predict Performance'}
        </button>
      </div>

      <AnimatePresence>
        {prediction && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            style={{
              borderTop: '1px solid var(--border)',
              paddingTop: '1rem',
            }}
          >
            {/* Prediction Results */}
            <div style={{ marginBottom: '1rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span style={{ fontSize: '0.875rem', color: 'var(--muted)' }}>
                  Predicted Accuracy
                </span>
                <span style={{ fontSize: '2rem', fontWeight: 'bold' }}>
                  {(prediction.predicted_accuracy * 100).toFixed(1)}%
                </span>
              </div>
              
              <div style={{ 
                marginTop: '0.5rem',
                height: '8px',
                background: 'var(--border)',
                borderRadius: 'var(--radius)',
                overflow: 'hidden',
              }}>
                <div
                  style={{
                    width: `${prediction.predicted_accuracy * 100}%`,
                    height: '100%',
                    background: prediction.predicted_accuracy > 0.85 
                      ? 'var(--success)' 
                      : prediction.predicted_accuracy > 0.75 
                      ? 'var(--warning)' 
                      : 'var(--error)',
                    transition: 'width 0.5s ease',
                  }}
                />
              </div>
            </div>

            {/* Expected Hits */}
            <div style={{ marginBottom: '1rem' }}>
              <span style={{ fontSize: '0.875rem', color: 'var(--muted)' }}>
                Expected Hits
              </span>
              <div style={{ display: 'flex', gap: '0.25rem', marginTop: '0.5rem' }}>
                {[...Array(5)].map((_, i) => (
                  <div
                    key={i}
                    style={{
                      width: '30px',
                      height: '30px',
                      borderRadius: '50%',
                      background: i < prediction.expected_hits 
                        ? 'var(--success)' 
                        : 'var(--border)',
                      transition: 'background 0.3s ease',
                    }}
                  />
                ))}
              </div>
            </div>

            {/* Contributing Factors */}
            <div style={{ marginBottom: '1rem' }}>
              <span style={{ fontSize: '0.875rem', color: 'var(--muted)' }}>
                Contributing Factors
              </span>
              <div style={{ marginTop: '0.5rem' }}>
                {Object.entries(prediction.contributing_factors || {}).map(([factor, value]: [string, any]) => (
                  <div
                    key={factor}
                    style={{
                      display: 'flex',
                      justifyContent: 'space-between',
                      padding: '0.25rem 0',
                      fontSize: '0.875rem',
                    }}
                  >
                    <span style={{ textTransform: 'capitalize' }}>{factor}</span>
                    <span style={{
                      color: value > 0.95 ? 'var(--success)' : 
                             value > 0.9 ? 'var(--warning)' : 'var(--error)'
                    }}>
                      {(value * 100).toFixed(0)}%
                    </span>
                  </div>
                ))}
              </div>
            </div>

            {/* Recommendations */}
            {prediction.recommendations && prediction.recommendations.length > 0 && (
              <div>
                <span style={{ fontSize: '0.875rem', color: 'var(--muted)' }}>
                  Recommendations
                </span>
                <ul style={{ marginTop: '0.5rem', marginLeft: '1.5rem' }}>
                  {prediction.recommendations.map((rec: string, i: number) => (
                    <li key={i} style={{ fontSize: '0.875rem', marginBottom: '0.25rem' }}>
                      {rec}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
