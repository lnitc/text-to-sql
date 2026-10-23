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
  user_query: string;
}

export interface ErrorResponse {
  error: string;
  message: string;
  status_code: number;
  details?: string;
}

export async function sendQuery(query: string): Promise<AgentResponse> {
  try {
    const response = await apiClient.post<AgentResponse>('/api/chat', {
      user_query: query,
    } as ChatRequest);
    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error)) {
      const axiosError = error as AxiosError<ErrorResponse>;
      const errorData = axiosError.response?.data;
      
      // Try to extract message from error response
      let errorMessage = 'Failed to send query';
      if (errorData?.message) {
        errorMessage = errorData.message;
      } else if (errorData?.details) {
        errorMessage = errorData.details;
      } else if (axiosError.message) {
        errorMessage = axiosError.message;
      }
      
      throw new Error(errorMessage);
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
