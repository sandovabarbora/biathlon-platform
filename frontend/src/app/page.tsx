'use client';

import { useAthleteStore } from '@/lib/store/athlete-store';
import { Dashboard } from '@/components/dashboard/dashboard';
import { AthleteSelector } from '@/components/athlete/athlete-selector';

export default function HomePage() {
  const { selectedAthlete } = useAthleteStore();

  if (!selectedAthlete) {
    return (
      <div className="card" style={{ marginTop: '2rem', textAlign: 'center' }}>
        <h2 style={{ marginBottom: '1rem' }}>Welcome to Biathlon Digital Twin</h2>
        <p style={{ marginBottom: '2rem', color: 'var(--muted)' }}>
          Select an athlete to view their real-time performance dashboard
        </p>
        <AthleteSelector />
      </div>
    );
  }

  return <Dashboard athleteId={selectedAthlete.id} />;
}
