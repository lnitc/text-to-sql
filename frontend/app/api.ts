import axios, { AxiosError } from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 60000,
  headers: {
    'Content-Type': 'application/json',
  },
});

export interface ChartData {
  chart_type: 'bar' | 'line' | 'pie' | 'table';
  data: Record<string, unknown>[];
  x_axis_key: string;
  y_axis_key: string;
}

export interface AgentResponse {
  thought_process: string;
  sql_query: string;
  chart: ChartData;
}

export interface ChatRequest {
  query: string;
}

export async function sendQuery(query: string): Promise<AgentResponse> {
  try {
    const response = await apiClient.post<AgentResponse>('/api/chat', {
      query,
    } as ChatRequest);
    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error)) {
      const axiosError = error as AxiosError<{ detail: string }>;
      throw new Error(
        axiosError.response?.data?.detail ||
          axiosError.message ||
          'Failed to send query'
      );
    }
    throw error;
  }
}

export async function checkHealth(): Promise<boolean> {
  try {
    const response = await apiClient.get('/health');
    return response.status === 200;
  } catch {
    return false;
  }
}
