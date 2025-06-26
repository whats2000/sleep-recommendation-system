/**
 * A/B Testing Interface for blind music comparison
 * Based on RecommendationSystem.md specifications
 */

import React, { useState, useEffect, useRef } from 'react';
import {
  Card,
  Button,
  Space,
  Typography,
  Progress,
  Radio,
  Divider,
  message,
  Spin,
} from 'antd';
import {
  PlayCircleOutlined,
  PauseCircleOutlined,
  ReloadOutlined,
  SoundOutlined,
} from '@ant-design/icons';
import type {
  ABTestSession,
  ABTestChoice,
  ABTestResult,
  MusicTrack,
  AudioPlaybackState,
} from '../types/api';
import { AudioService, createAudioControls } from '../services/audio';

const { Title, Text, Paragraph } = Typography;

interface ABTestInterfaceProps {
  session: ABTestSession;
  onComplete: (result: ABTestResult) => void;
  onError: (error: string) => void;
}

export const ABTestInterface: React.FC<ABTestInterfaceProps> = ({
  session,
  onComplete,
  onError,
}) => {
  const [currentPairIndex, setCurrentPairIndex] = useState(0);
  const [choices, setChoices] = useState<ABTestChoice[]>([]);
  const [selectedChoice, setSelectedChoice] = useState<'A' | 'B' | null>(null);
  const [startTime] = useState<number>(Date.now());
  const [pairStartTime, setPairStartTime] = useState<number>(Date.now());
  
  // Audio states
  const [audioStateA, setAudioStateA] = useState<AudioPlaybackState>({
    isPlaying: false,
    currentTime: 0,
    duration: 0,
    volume: 1,
    isLoading: false,
  });
  const [audioStateB, setAudioStateB] = useState<AudioPlaybackState>({
    isPlaying: false,
    currentTime: 0,
    duration: 0,
    volume: 1,
    isLoading: false,
  });

  // Audio services
  const audioServiceA = useRef<AudioService | null>(null);
  const audioServiceB = useRef<AudioService | null>(null);
  const audioControlsA = useRef<any>(null);
  const audioControlsB = useRef<any>(null);

  // Play counts and listen times
  const [playCountA, setPlayCountA] = useState(0);
  const [playCountB, setPlayCountB] = useState(0);
  const [listenTimeA, setListenTimeA] = useState(0);
  const [listenTimeB, setListenTimeB] = useState(0);

  const currentPair = session.test_pairs[currentPairIndex];
  const progress = ((currentPairIndex + 1) / session.total_pairs) * 100;

  // Initialize audio services
  useEffect(() => {
    if (!currentPair) return;

    // Initialize audio services
    audioServiceA.current = new AudioService(setAudioStateA);
    audioServiceB.current = new AudioService(setAudioStateB);

    audioControlsA.current = createAudioControls(audioServiceA.current);
    audioControlsB.current = createAudioControls(audioServiceB.current);

    // Load audio files
    const loadAudio = async () => {
      try {
        if (audioServiceA.current && audioServiceB.current) {
          await Promise.all([
            audioServiceA.current.loadAudio(`/api/audio/${currentPair.track_a.file_path}`),
            audioServiceB.current.loadAudio(`/api/audio/${currentPair.track_b.file_path}`),
          ]);
        }
      } catch (error) {
        console.error('Error loading audio:', error);
        onError('無法載入音頻檔案');
      }
    };

    loadAudio();

    // Reset pair-specific state
    setSelectedChoice(null);
    setPairStartTime(Date.now());
    setPlayCountA(0);
    setPlayCountB(0);
    setListenTimeA(0);
    setListenTimeB(0);

    // Cleanup function
    return () => {
      audioServiceA.current?.dispose();
      audioServiceB.current?.dispose();
    };
  }, [currentPairIndex, currentPair, onError]);

  // Track listen time
  useEffect(() => {
    const interval = setInterval(() => {
      if (audioStateA.isPlaying) {
        setListenTimeA(prev => prev + 100);
      }
      if (audioStateB.isPlaying) {
        setListenTimeB(prev => prev + 100);
      }
    }, 100);

    return () => clearInterval(interval);
  }, [audioStateA.isPlaying, audioStateB.isPlaying]);

  // Handle audio play
  const handlePlay = async (track: 'A' | 'B') => {
    try {
      if (track === 'A') {
        // Stop B if playing
        if (audioStateB.isPlaying) {
          audioControlsB.current?.pause();
        }
        await audioControlsA.current?.play();
        setPlayCountA(prev => prev + 1);
      } else {
        // Stop A if playing
        if (audioStateA.isPlaying) {
          audioControlsA.current?.pause();
        }
        await audioControlsB.current?.play();
        setPlayCountB(prev => prev + 1);
      }
    } catch (error) {
      console.error('Error playing audio:', error);
      message.error('播放失敗');
    }
  };

  // Handle audio pause
  const handlePause = (track: 'A' | 'B') => {
    if (track === 'A') {
      audioControlsA.current?.pause();
    } else {
      audioControlsB.current?.pause();
    }
  };

  // Handle audio replay
  const handleReplay = async (track: 'A' | 'B') => {
    try {
      if (track === 'A') {
        await audioControlsA.current?.replay();
        setPlayCountA(prev => prev + 1);
      } else {
        await audioControlsB.current?.replay();
        setPlayCountB(prev => prev + 1);
      }
    } catch (error) {
      console.error('Error replaying audio:', error);
      message.error('重播失敗');
    }
  };

  // Handle choice selection
  const handleChoiceChange = (choice: 'A' | 'B') => {
    setSelectedChoice(choice);
  };

  // Handle next pair or completion
  const handleNext = () => {
    if (!selectedChoice) {
      message.error('請選擇您偏好的音樂');
      return;
    }

    // Record choice
    const choice: ABTestChoice = {
      pair_id: currentPair.id,
      chosen_track: selectedChoice,
      decision_time_ms: Date.now() - pairStartTime,
      play_count_a: playCountA,
      play_count_b: playCountB,
      total_listen_time_a: listenTimeA,
      total_listen_time_b: listenTimeB,
    };

    const newChoices = [...choices, choice];
    setChoices(newChoices);

    // Check if this is the last pair
    if (currentPairIndex === session.total_pairs - 1) {
      // Complete the test
      const result: ABTestResult = {
        session_id: session.session_id,
        choices: newChoices,
        completion_time: new Date().toISOString(),
        total_duration_ms: Date.now() - startTime,
      };
      onComplete(result);
    } else {
      // Move to next pair
      setCurrentPairIndex(prev => prev + 1);
    }
  };

  // Render audio player
  const renderAudioPlayer = (
    _track: MusicTrack,
    label: 'A' | 'B',
    audioState: AudioPlaybackState,
    onPlay: () => void,
    onPause: () => void,
    onReplay: () => void
  ) => (
    <Card
      title={`音樂 ${label}`}
      style={{ width: '100%' }}
      extra={
        <Text type="secondary">
          播放次數: {label === 'A' ? playCountA : playCountB}
        </Text>
      }
    >
      <Space direction="vertical" style={{ width: '100%' }}>
        {/* Audio controls */}
        <Space size="large" style={{ justifyContent: 'center', width: '100%' }}>
          <Button
            type="primary"
            shape="circle"
            size="large"
            icon={audioState.isPlaying ? <PauseCircleOutlined /> : <PlayCircleOutlined />}
            onClick={audioState.isPlaying ? onPause : onPlay}
            loading={audioState.isLoading}
          />
          <Button
            shape="circle"
            size="large"
            icon={<ReloadOutlined />}
            onClick={onReplay}
            disabled={audioState.isLoading}
          />
        </Space>

        {/* Progress bar */}
        {audioState.duration > 0 && (
          <Progress
            percent={(audioState.currentTime / audioState.duration) * 100}
            showInfo={false}
            strokeColor="#1890ff"
          />
        )}

        {/* Time display */}
        <div style={{ textAlign: 'center' }}>
          <Text type="secondary">
            {Math.floor(audioState.currentTime)}s / {Math.floor(audioState.duration)}s
          </Text>
        </div>
      </Space>
    </Card>
  );

  if (!currentPair) {
    return (
      <div style={{ textAlign: 'center', padding: '50px' }}>
        <Spin size="large" />
        <Paragraph style={{ marginTop: 16 }}>載入測試資料中...</Paragraph>
      </div>
    );
  }

  return (
    <div style={{ maxWidth: 900, margin: '0 auto', padding: '24px' }}>
      <Card>
        <div style={{ marginBottom: 24 }}>
          <Title level={2} style={{ textAlign: 'center', marginBottom: 8 }}>
            音樂偏好測試
          </Title>
          <Paragraph style={{ textAlign: 'center', color: '#666' }}>
            請聆聽以下兩首音樂，選擇您更偏好的一首
          </Paragraph>
          
          {/* Progress */}
          <div style={{ marginBottom: 24 }}>
            <Progress
              percent={progress}
              format={() => `${currentPairIndex + 1} / ${session.total_pairs}`}
            />
          </div>
        </div>

        {/* Audio players */}
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '24px', marginBottom: 32 }}>
          {renderAudioPlayer(
            currentPair.track_a,
            'A',
            audioStateA,
            () => handlePlay('A'),
            () => handlePause('A'),
            () => handleReplay('A')
          )}
          {renderAudioPlayer(
            currentPair.track_b,
            'B',
            audioStateB,
            () => handlePlay('B'),
            () => handlePause('B'),
            () => handleReplay('B')
          )}
        </div>

        <Divider />

        {/* Choice selection */}
        <div style={{ textAlign: 'center', marginBottom: 32 }}>
          <Title level={4} style={{ marginBottom: 16 }}>
            <SoundOutlined /> 請選擇您更偏好的音樂：
          </Title>
          <Radio.Group
            value={selectedChoice}
            onChange={(e) => handleChoiceChange(e.target.value)}
            size="large"
          >
            <Space size="large">
              <Radio value="A">音樂 A</Radio>
              <Radio value="B">音樂 B</Radio>
            </Space>
          </Radio.Group>
        </div>

        {/* Next button */}
        <div style={{ textAlign: 'center' }}>
          <Button
            type="primary"
            size="large"
            onClick={handleNext}
            disabled={!selectedChoice}
            style={{ minWidth: 120 }}
          >
            {currentPairIndex === session.total_pairs - 1 ? '完成測試' : '下一組'}
          </Button>
        </div>
      </Card>
    </div>
  );
};
