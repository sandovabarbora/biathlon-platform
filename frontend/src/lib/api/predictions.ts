import { apiClient } from './client';
import {
  ShootingPredictionRequest,
  ShootingPredictionResponse,
  ApproachOptimizationRequest,
  ApproachOptimizationResponse,
} from '@/types';

export const predictionsApi = {
  predictShooting: async (
    athleteId: number,
    request: ShootingPredictionRequest
  ) => {
    const { data } = await apiClient.post<ShootingPredictionResponse>(
      `/predictions/${athleteId}/shooting`,
      request
    );
    return data;
  },

  optimizeApproach: async (
    athleteId: number,
    request: ApproachOptimizationRequest
  ) => {
    const { data } = await apiClient.post<ApproachOptimizationResponse>(
      `/predictions/${athleteId}/approach`,
      request
    );
    return data;
  },

  getFatigueAssessment: async (athleteId: number) => {
    const { data } = await apiClient.get(
      `/predictions/${athleteId}/fatigue`
    );
    return data;
  },

  getHistory: async (athleteId: number, limit = 50) => {
    const { data } = await apiClient.get(
      `/predictions/${athleteId}/history`,
      { params: { limit } }
    );
    return data;
  },
};
