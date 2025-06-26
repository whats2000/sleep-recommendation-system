/**
 * API service for communicating with the Symphony AI backend
 */

import axios from 'axios';
import type { AxiosInstance, AxiosResponse } from 'axios';
import type {
  ApiResponse,
  HealthResponse,
  StatusResponse,
  RecommendationRequest,
  RecommendationResponse,
  PipelineStatusResponse,
  ABTestSession,
  ABTestSubmissionRequest,
} from '../types/api';

class ApiService {
  private client: AxiosInstance;
  private baseURL: string;

  constructor() {
    this.baseURL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000';
    
    this.client = axios.create({
      baseURL: this.baseURL,
      timeout: 30000, // 30 seconds timeout
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Request interceptor for logging
    this.client.interceptors.request.use(
      (config) => {
        console.log(`API Request: ${config.method?.toUpperCase()} ${config.url}`);
        return config;
      },
      (error) => {
        console.error('API Request Error:', error);
        return Promise.reject(error);
      }
    );

    // Response interceptor for error handling
    this.client.interceptors.response.use(
      (response: AxiosResponse) => {
        console.log(`API Response: ${response.status} ${response.config.url}`);
        return response;
      },
      (error) => {
        console.error('API Response Error:', error);
        
        // Handle common error scenarios
        if (error.response) {
          // Server responded with error status
          const { status, data } = error.response;
          console.error(`API Error ${status}:`, data);
        } else if (error.request) {
          // Request was made but no response received
          console.error('No response received:', error.request);
        } else {
          // Something else happened
          console.error('Request setup error:', error.message);
        }
        
        return Promise.reject(error);
      }
    );
  }

  // Health check endpoint
  async healthCheck(): Promise<HealthResponse> {
    const response = await this.client.get<HealthResponse>('/health');
    return response.data;
  }

  // Service status endpoint
  async getStatus(): Promise<StatusResponse> {
    const response = await this.client.get<StatusResponse>('/status');
    return response.data;
  }

  // Get music recommendations
  async getRecommendations(formData: RecommendationRequest): Promise<RecommendationResponse> {
    const response = await this.client.post<RecommendationResponse>(
      '/api/recommendations',
      formData
    );
    return response.data;
  }

  // Get pipeline status
  async getPipelineStatus(sessionId: string): Promise<PipelineStatusResponse> {
    const response = await this.client.get<PipelineStatusResponse>(
      `/api/pipeline/status/${sessionId}`
    );
    return response.data;
  }

  // Start A/B test session
  async startABTest(formData: RecommendationRequest): Promise<ABTestSession> {
    const response = await this.client.post<ABTestSession>(
      '/api/ab-test/start',
      formData
    );
    return response.data;
  }

  // Submit A/B test results
  async submitABTestResults(submission: ABTestSubmissionRequest): Promise<ApiResponse> {
    const response = await this.client.post<ApiResponse>(
      '/api/ab-test/submit',
      submission
    );
    return response.data;
  }

  // Get audio file URL
  getAudioUrl(filePath: string): string {
    // Remove leading slash if present
    const cleanPath = filePath.startsWith('/') ? filePath.slice(1) : filePath;
    return `${this.baseURL}/${cleanPath}`;
  }

  // Download audio file (for caching)
  async downloadAudio(filePath: string): Promise<Blob> {
    const response = await this.client.get(this.getAudioUrl(filePath), {
      responseType: 'blob',
    });
    return response.data;
  }



  // Utility method to check if backend is available
  async isBackendAvailable(): Promise<boolean> {
    try {
      await this.healthCheck();
      return true;
    } catch {
      return false;
    }
  }

  // Utility method to wait for backend to be ready
  async waitForBackend(maxAttempts: number = 10, delayMs: number = 1000): Promise<boolean> {
    for (let attempt = 1; attempt <= maxAttempts; attempt++) {
      try {
        await this.healthCheck();
        return true;
      } catch {
        if (attempt === maxAttempts) {
          return false;
        }
        await new Promise(resolve => setTimeout(resolve, delayMs));
      }
    }
    return false;
  }
}

// Create and export a singleton instance
export const apiService = new ApiService();
export default apiService;
