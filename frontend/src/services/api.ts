import axios from 'axios';
import type { EventLog, AnalysisResult } from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

export const api = {
  getHistory: async (): Promise<EventLog[]> => {
    const response = await axios.get(`${API_BASE_URL}/history`);
    return response.data;
  },

  assessVoyage: async (formData: any): Promise<any> => {
    const response = await axios.post(`${API_BASE_URL}/assess-voyage`, formData);
    return response.data;
  },
  
  analyze: async (labelId: number): Promise<AnalysisResult> => {
    const response = await axios.post(`${API_BASE_URL}/analyze/${labelId}`);
    return response.data;
  },
  
  startVoyage: async (voyageId: string): Promise<void> => {
    await axios.post(`${API_BASE_URL}/start-voyage?voyage_id=${voyageId}`);
  }
};

export const getWebSocketUrl = (voyageId: string | null): string => {
  const base = import.meta.env.VITE_WS_URL || 'ws://localhost:8000/ws/stream';
  return voyageId ? `${base}?voyage_id=${voyageId}` : base;
};
