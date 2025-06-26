/**
 * Audio service using Web Audio API for music playback
 */

import type { AudioPlaybackState, AudioControls } from '../types/api';

export class AudioService {
  private audioContext: AudioContext | null = null;
  private audioBuffer: AudioBuffer | null = null;
  private source: AudioBufferSourceNode | null = null;
  private gainNode: GainNode | null = null;
  private startTime: number = 0;
  private pauseTime: number = 0;
  private isPlaying: boolean = false;
  private duration: number = 0;
  private volume: number = 1.0;
  private onStateChange?: (state: AudioPlaybackState) => void;
  private userInteractionRequired: boolean = true;

  constructor(onStateChange?: (state: AudioPlaybackState) => void) {
    this.onStateChange = onStateChange;
  }

  // Check if audio is ready to play
  isAudioReady(): boolean {
    return !!(this.audioContext && this.audioBuffer);
  }

  // Enable audio after user interaction
  async enableAudio(): Promise<void> {
    if (this.userInteractionRequired) {
      await this.initAudioContext();
      this.userInteractionRequired = false;
    }
  }

  // Initialize audio context
  private async initAudioContext(): Promise<void> {
    if (!this.audioContext) {
      try {
        // Check if AudioContext is supported
        const AudioContextClass = window.AudioContext || (window as any).webkitAudioContext;
        if (!AudioContextClass) {
          throw new Error('Web Audio API is not supported in this browser');
        }

        this.audioContext = new AudioContextClass();

        // Verify the context was created successfully
        if (!this.audioContext) {
          throw new Error('Failed to create AudioContext');
        }

        // Create gain node for volume control
        this.gainNode = this.audioContext.createGain();
        this.gainNode.connect(this.audioContext.destination);
        this.gainNode.gain.value = this.volume;

        console.log('AudioContext initialized successfully:', {
          state: this.audioContext.state,
          sampleRate: this.audioContext.sampleRate
        });
      } catch (error) {
        console.error('Failed to initialize AudioContext:', error);
        this.audioContext = null;
        this.gainNode = null;
        throw error;
      }
    }

    // Resume context if suspended (required by some browsers)
    if (this.audioContext && this.audioContext.state === 'suspended') {
      try {
        await this.audioContext.resume();
        console.log('AudioContext resumed, state:', this.audioContext.state);
      } catch (error) {
        console.error('Failed to resume AudioContext:', error);
        throw error;
      }
    }
  }

  // Load audio from URL
  async loadAudio(url: string): Promise<void> {
    try {
      console.log('Loading audio from URL:', url);

      // Initialize audio context first
      await this.initAudioContext();

      // Verify audio context is available
      if (!this.audioContext) {
        throw new Error('AudioContext is not available');
      }

      this.updateState({ isLoading: true });

      const response = await fetch(url);
      if (!response.ok) {
        throw new Error(`Failed to fetch audio: ${response.status} ${response.statusText}`);
      }

      const contentType = response.headers.get('content-type');
      console.log('Audio response content-type:', contentType);

      const arrayBuffer = await response.arrayBuffer();
      console.log('Audio buffer size:', arrayBuffer.byteLength, 'bytes');

      if (arrayBuffer.byteLength === 0) {
        throw new Error('Received empty audio file');
      }

      // Verify audio context is still available before decoding
      if (!this.audioContext) {
        throw new Error('AudioContext became unavailable during loading');
      }

      console.log('Decoding audio data...');
      this.audioBuffer = await this.audioContext.decodeAudioData(arrayBuffer);
      this.duration = this.audioBuffer.duration;

      console.log('Audio loaded successfully:', {
        duration: this.duration,
        sampleRate: this.audioBuffer.sampleRate,
        numberOfChannels: this.audioBuffer.numberOfChannels
      });

      this.updateState({
        isLoading: false,
        duration: this.duration,
        error: undefined
      });
    } catch (error) {
      console.error('Error loading audio:', error);
      const errorMessage = error instanceof Error ? error.message : 'Failed to load audio';
      this.updateState({
        isLoading: false,
        error: errorMessage
      });
      throw error;
    }
  }

  // Play audio
  async play(): Promise<void> {
    try {
      // Ensure audio context is initialized (handles user interaction requirement)
      await this.enableAudio();

      if (!this.audioBuffer || !this.audioContext || !this.gainNode) {
        throw new Error('Audio not loaded or AudioContext not available');
      }

      // Stop current playback if any
      this.stop();

      // Create new source
      this.source = this.audioContext.createBufferSource();
      this.source.buffer = this.audioBuffer;
      this.source.connect(this.gainNode);

      // Set up ended event
      this.source.onended = () => {
        if (this.isPlaying) {
          this.isPlaying = false;
          this.pauseTime = 0;
          this.updateState({ 
            isPlaying: false,
            currentTime: this.duration
          });
        }
      };

      // Start playback
      const offset = this.pauseTime;
      this.source.start(0, offset);
      this.startTime = this.audioContext.currentTime - offset;
      this.isPlaying = true;

      this.updateState({ isPlaying: true });

      // Start time tracking
      this.startTimeTracking();
    } catch (error) {
      console.error('Error playing audio:', error);
      this.updateState({ 
        error: error instanceof Error ? error.message : 'Failed to play audio'
      });
      throw error;
    }
  }

  // Pause audio
  pause(): void {
    if (this.source && this.isPlaying && this.audioContext) {
      this.source.stop();
      this.pauseTime = this.audioContext.currentTime - this.startTime;
      this.isPlaying = false;
      this.updateState({ isPlaying: false });
    }
  }

  // Stop audio
  stop(): void {
    if (this.source) {
      this.source.stop();
      this.source.disconnect();
      this.source = null;
    }
    this.isPlaying = false;
    this.pauseTime = 0;
    this.updateState({ 
      isPlaying: false,
      currentTime: 0
    });
  }

  // Seek to specific time
  seek(time: number): void {
    if (time < 0 || time > this.duration) {
      return;
    }

    const wasPlaying = this.isPlaying;
    this.stop();
    this.pauseTime = time;
    this.updateState({ currentTime: time });

    if (wasPlaying) {
      this.play();
    }
  }

  // Set volume (0.0 to 1.0)
  setVolume(volume: number): void {
    this.volume = Math.max(0, Math.min(1, volume));
    if (this.gainNode) {
      this.gainNode.gain.value = this.volume;
    }
    this.updateState({ volume: this.volume });
  }

  // Replay from beginning
  async replay(): Promise<void> {
    this.stop();
    await this.play();
  }

  // Get current playback time
  getCurrentTime(): number {
    if (!this.audioContext) return 0;
    
    if (this.isPlaying) {
      return Math.min(this.audioContext.currentTime - this.startTime, this.duration);
    } else {
      return this.pauseTime;
    }
  }

  // Get current state
  getState(): AudioPlaybackState {
    return {
      isPlaying: this.isPlaying,
      currentTime: this.getCurrentTime(),
      duration: this.duration,
      volume: this.volume,
      isLoading: false,
    };
  }

  // Start time tracking interval
  private startTimeTracking(): void {
    const updateInterval = setInterval(() => {
      if (!this.isPlaying) {
        clearInterval(updateInterval);
        return;
      }

      this.updateState({ currentTime: this.getCurrentTime() });
    }, 100); // Update every 100ms
  }

  // Update state and notify listeners
  private updateState(partialState: Partial<AudioPlaybackState>): void {
    if (this.onStateChange) {
      const currentState = this.getState();
      const newState = { ...currentState, ...partialState };
      this.onStateChange(newState);
    }
  }

  // Cleanup resources
  dispose(): void {
    this.stop();
    if (this.audioContext) {
      this.audioContext.close();
      this.audioContext = null;
    }
    this.audioBuffer = null;
    this.gainNode = null;
  }
}

// Factory function to create audio controls
export function createAudioControls(audioService: AudioService): AudioControls {
  return {
    play: () => audioService.play(),
    pause: () => audioService.pause(),
    stop: () => audioService.stop(),
    seek: (time: number) => audioService.seek(time),
    setVolume: (volume: number) => audioService.setVolume(volume),
    replay: () => audioService.replay(),
  };
}
