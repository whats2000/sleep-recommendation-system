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

  constructor(onStateChange?: (state: AudioPlaybackState) => void) {
    this.onStateChange = onStateChange;
  }

  // Initialize audio context
  private async initAudioContext(): Promise<void> {
    if (!this.audioContext) {
      this.audioContext = new (window.AudioContext || (window as any).webkitAudioContext)();
      
      // Create gain node for volume control
      this.gainNode = this.audioContext.createGain();
      this.gainNode.connect(this.audioContext.destination);
      this.gainNode.gain.value = this.volume;
    }

    // Resume context if suspended (required by some browsers)
    if (this.audioContext.state === 'suspended') {
      await this.audioContext.resume();
    }
  }

  // Load audio from URL
  async loadAudio(url: string): Promise<void> {
    try {
      await this.initAudioContext();
      
      this.updateState({ isLoading: true });

      const response = await fetch(url);
      if (!response.ok) {
        throw new Error(`Failed to fetch audio: ${response.statusText}`);
      }

      const arrayBuffer = await response.arrayBuffer();
      this.audioBuffer = await this.audioContext!.decodeAudioData(arrayBuffer);
      this.duration = this.audioBuffer.duration;

      this.updateState({ 
        isLoading: false,
        duration: this.duration,
        error: undefined
      });
    } catch (error) {
      console.error('Error loading audio:', error);
      this.updateState({ 
        isLoading: false,
        error: error instanceof Error ? error.message : 'Failed to load audio'
      });
      throw error;
    }
  }

  // Play audio
  async play(): Promise<void> {
    if (!this.audioBuffer || !this.audioContext || !this.gainNode) {
      throw new Error('Audio not loaded');
    }

    try {
      await this.initAudioContext();

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
