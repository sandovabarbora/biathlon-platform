import { apiClient } from './client';
import { Athlete, AthleteCreate, AthleteUpdate } from '@/types';

export const athletesApi = {
  getAll: async (activeOnly = true) => {
    const { data } = await apiClient.get('/athletes', {
      params: { active_only: activeOnly }
    });
    return data;
  },

  getById: async (id: number) => {
    const { data } = await apiClient.get<Athlete>(`/athletes/${id}`);
    return data;
  },

  create: async (athlete: AthleteCreate) => {
    const { data } = await apiClient.post<Athlete>('/athletes', athlete);
    return data;
  },

  update: async (id: number, updates: AthleteUpdate) => {
    const { data } = await apiClient.patch<Athlete>(`/athletes/${id}`, updates);
    return data;
  },

  calibrate: async (id: number, calibrationData: any) => {
    const { data } = await apiClient.post<Athlete>(
      `/athletes/${id}/calibrate`,
      calibrationData
    );
    return data;
  },

  delete: async (id: number) => {
    await apiClient.delete(`/athletes/${id}`);
  },
};
