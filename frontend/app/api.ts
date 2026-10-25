import axios, { AxiosError } from 'axios';

export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  // SQL generation can be retried by the backend after a BigQuery error, so
  // allow for a few LLM round-trips plus query execution.
  timeout: 120000,
  headers: {
    'Content-Type': 'application/json',
  },
});

export interface ChartData {
  chart_type: 'bar' | 'line' | 'pie' | 'table';
  data: Record<string, unknown>[];
  x_axis_key: string;
  y_axis_key: string;
  title?: string;
}

export type PipelineName = 'simple' | 'crew';

export interface AgentResponse {
  thought_process: string;
  sql_query: string;
  chart: ChartData;
  execution_time_ms?: number;
  pipeline?: PipelineName;
  insights?: string[];
  follow_up_questions?: string[];
}

export interface ChatRequest {
  user_query: string;
  pipeline?: PipelineName;
}

export interface ErrorResponse {
  error: string;
  message: string;
  status_code: number;
  details?: string;
}

export interface HealthStatus {
  reachable: boolean;
  status?: 'ok' | 'degraded' | 'error';
  message?: string;
  default_pipeline?: PipelineName;
}

export async function sendQuery(query: string, pipeline?: PipelineName): Promise<AgentResponse> {
  try {
    const response = await apiClient.post<AgentResponse>('/api/chat', {
      user_query: query,
      pipeline,
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
      } else if (axiosError.code === 'ECONNABORTED') {
        errorMessage = 'Request timeout: the backend took too long to respond';
      } else if (!axiosError.response) {
        // Wording matters: parseErrorMessage keys off "connection"/"timeout"
        errorMessage = `Network connection error: unable to reach the backend at ${API_BASE_URL}`;
      } else if (axiosError.message) {
        errorMessage = axiosError.message;
      }

      throw new Error(errorMessage);
    }
    throw error;
  }
}

export async function checkHealth(): Promise<HealthStatus> {
  try {
    const response = await apiClient.get<Omit<HealthStatus, 'reachable'>>('/health', {
      timeout: 5000,
    });
    return { reachable: true, ...response.data };
  } catch {
    return { reachable: false };
  }
}
