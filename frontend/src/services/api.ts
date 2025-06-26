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
      timeout: 120000, // 2 minutes timeout for model evaluation
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

  // Transform camelCase to snake_case for backend
  private transformFormData(formData: RecommendationRequest): any {
    console.log('Original form data:', formData);

    const transformed = {
      email: formData.email,
      stress_level: formData.stressLevel,
      physical_symptoms: formData.physicalSymptoms || [],
      emotional_state: formData.emotionalState,
      sleep_goal: formData.sleepGoal,
      sound_preferences: formData.soundPreferences || [],
      rhythm_preference: formData.rhythmPreference,
      sound_sensitivities: formData.soundSensitivities || [],
      playback_mode: formData.playbackMode,
      guided_voice: formData.guidedVoice,
      sleep_theme: formData.sleepTheme,
      user_id: formData.user_id,
      session_id: formData.session_id,
    };

    console.log('Transformed form data:', transformed);

    // Check for missing required fields
    const requiredFields = ['email', 'stress_level', 'emotional_state', 'sleep_goal', 'sleep_theme'];
    const missingFields = requiredFields.filter(field => !(transformed as any)[field]);
    if (missingFields.length > 0) {
      console.error('Missing required fields in transformed data:', missingFields);
    }

    return transformed;
  }

  // Get music recommendations
  async getRecommendations(formData: RecommendationRequest): Promise<RecommendationResponse> {
    const transformedData = this.transformFormData(formData);
    console.log('Sending data to backend:', transformedData);
    const response = await this.client.post<RecommendationResponse>(
      '/api/recommendations/',
      transformedData,
      {
        timeout: 180000, // 3 minutes timeout for recommendation generation
      }
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

  // Start A/B test session (recalculates recommendations - SLOW)
  async startABTest(formData: RecommendationRequest): Promise<ABTestSession> {
    const transformedData = this.transformFormData(formData);
    const response = await this.client.post<ABTestSession>(
      '/api/experiment/ab-test/start',
      transformedData,
      {
        timeout: 180000, // 3 minutes timeout for A/B test setup
      }
    );
    return response.data;
  }

  // Start A/B test session with existing recommendations (FAST)
  async startABTestWithRecommendations(sessionId: string, formData: RecommendationRequest, recommendations: unknown[]): Promise<ABTestSession> {
    const transformedData = this.transformFormData(formData);
    const response = await this.client.post<ABTestSession>(
      '/api/experiment/ab-test/start-with-recommendations',
      {
        session_id: sessionId,
        form_data: transformedData,
        recommendations: recommendations,
      },
      {
        timeout: 30000, // Much faster since we're not recalculating
      }
    );
    return response.data;
  }

  // Submit A/B test results
  async submitABTestResults(submission: ABTestSubmissionRequest): Promise<ApiResponse> {
    const response = await this.client.post<ApiResponse>(
      '/api/experiment/ab-test/submit',
      submission
    );
    return response.data;
  }

  // Get experiment analytics
  async getExperimentAnalytics(sessionId?: string): Promise<any> {
    const url = sessionId
      ? `/api/experiment/analytics/${sessionId}`
      : '/api/experiment/analytics';
    const response = await this.client.get(url);
    return response.data;
  }

  // Get experiment status
  async getExperimentStatus(sessionId: string): Promise<any> {
    const response = await this.client.get(`/api/experiment/status/${sessionId}`);
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
