import axios from 'axios';
import type { EventLog, AnalysisResult } from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

export const api = {
  getHistory: async (): Promise<EventLog[]> => {
    const response = await axios.get(`${API_BASE_URL}/history`);
    return response.data;
  },
  
  analyze: async (labelId: number): Promise<AnalysisResult> => {
    const response = await axios.post(`${API_BASE_URL}/analyze/${labelId}`);
    return response.data;
  },
  
  startVoyage: async (): Promise<void> => {
    await axios.post(`${API_BASE_URL}/start-voyage`);
  },
  
  getFleet: async (): Promise<any[]> => {
    const response = await axios.get(`${API_BASE_URL.replace('/api', '')}/api/fleet`);
    return response.data;
  }
};

export const WS_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:8000/ws/stream';

