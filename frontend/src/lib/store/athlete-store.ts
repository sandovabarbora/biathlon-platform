import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';
import { Athlete, SensorData } from '@/types';

interface AthleteStore {
  // State
  selectedAthlete: Athlete | null;
  realtimeData: SensorData | null;
  isConnected: boolean;
  lastUpdate: Date | null;
  
  // Actions
  setSelectedAthlete: (athlete: Athlete | null) => void;
  updateRealtimeData: (data: SensorData) => void;
  setConnected: (connected: boolean) => void;
  reset: () => void;
}

export const useAthleteStore = create<AthleteStore>()(
  devtools(
    persist(
      (set) => ({
        selectedAthlete: null,
        realtimeData: null,
        isConnected: false,
        lastUpdate: null,

        setSelectedAthlete: (athlete) =>
          set({ selectedAthlete: athlete, realtimeData: null }),

        updateRealtimeData: (data) =>
          set({ realtimeData: data, lastUpdate: new Date() }),

        setConnected: (connected) =>
          set({ isConnected: connected }),

        reset: () =>
          set({
            selectedAthlete: null,
            realtimeData: null,
            isConnected: false,
            lastUpdate: null,
          }),
      }),
      {
        name: 'athlete-store',
        partialize: (state) => ({
          selectedAthlete: state.selectedAthlete,
        }),
      }
    )
  )
);
