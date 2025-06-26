/**
 * API response types for the Symphony AI backend
 */
import type { FormData } from './form';

// API Response wrapper
export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}

// Health check response
export interface HealthResponse {
  status: string;
  timestamp: string;
  version: string;
}

// Service status response
export interface ServiceStatus {
  service: string;
  status: 'healthy' | 'unhealthy' | 'loading';
  details?: string;
}

export interface StatusResponse {
  overall_status: 'healthy' | 'degraded' | 'unhealthy';
  services: ServiceStatus[];
  timestamp: string;
}

// Music recommendation types
export interface MusicTrack {
  id: string;
  title: string;
  artist?: string;
  duration: number;
  file_path: string;
  similarity_score?: number;
  metadata?: {
    genre?: string;
    tempo?: string;
    mood?: string;
    instruments?: string[];
  };
}

export interface RecommendationResponse {
  session_id: string;
  recommendations: MusicTrack[];
  generated_prompt?: string;
  processing_time: number;
  timestamp: string;
}

// Pipeline status types
export type PipelineStatus = 
  | 'pending'
  | 'processing'
  | 'completed'
  | 'failed';

export interface PipelineStep {
  name: string;
  status: PipelineStatus;
  start_time?: string;
  end_time?: string;
  duration?: number;
  error?: string;
}

export interface PipelineStatusResponse {
  session_id: string;
  overall_status: PipelineStatus;
  steps: PipelineStep[];
  progress_percentage: number;
  estimated_completion?: string;
  timestamp: string;
}

// A/B Testing types
export interface ABTestPair {
  id: string;
  track_a: MusicTrack;
  track_b: MusicTrack;
  position_randomized: boolean;
}

export interface ABTestSession {
  session_id: string;
  user_id?: string;
  form_data: FormData;
  test_pairs: ABTestPair[];
  current_pair_index: number;
  total_pairs: number;
  start_time: string;
  recommendation_metadata?: {
    reused_existing?: boolean;
    recommendations_count?: number;
    local_session?: boolean;
    [key: string]: unknown;
  };
}

export interface ABTestChoice {
  pair_id: string;
  chosen_track: 'A' | 'B';
  decision_time_ms: number;
  play_count_a: number;
  play_count_b: number;
  total_listen_time_a: number;
  total_listen_time_b: number;
}

export interface ABTestResult {
  session_id: string;
  choices: ABTestChoice[];
  completion_time: string;
  total_duration_ms: number;
}

// Error types
export interface ApiError {
  code: string;
  message: string;
  details?: any;
  timestamp: string;
}

// Request types
export interface RecommendationRequest extends FormData {
  user_id?: string;
  session_id?: string;
}

export interface ABTestSubmissionRequest {
  session_id: string;
  results: ABTestResult;
}

// Audio playback types
export interface AudioPlaybackState {
  isPlaying: boolean;
  currentTime: number;
  duration: number;
  volume: number;
  isLoading: boolean;
  error?: string;
}

export interface AudioControls {
  play: () => Promise<void>;
  pause: () => void;
  stop: () => void;
  seek: (time: number) => void;
  setVolume: (volume: number) => void;
  replay: () => Promise<void>;
}

// Analytics types
export interface UserInteraction {
  type: 'form_submit' | 'audio_play' | 'audio_pause' | 'choice_made' | 'page_view';
  timestamp: string;
  data?: any;
}

export interface SessionAnalytics {
  session_id: string;
  user_id?: string;
  start_time: string;
  end_time?: string;
  interactions: UserInteraction[];
  form_completion_time?: number;
  recommendation_satisfaction?: number;
}
