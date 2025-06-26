/**
 * Recommendations Page - Display music recommendations
 */

import React, { useState, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import {
  Card,
  Button,
  List,
  Typography,
  Space,
  Tag,
  Divider,
  message,
  Spin,
} from 'antd';
import {
  PlayCircleOutlined,
  ExperimentOutlined,
  HomeOutlined, SoundOutlined,
} from '@ant-design/icons';
import type { MusicTrack } from '../types/api';
import type { FormData } from '../types/form';
import { apiService } from '../services/api';

const { Title, Paragraph, Text } = Typography;

interface LocationState {
  sessionId: string;
  recommendations: MusicTrack[];
  formData: FormData;
}

export const RecommendationsPage: React.FC = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);

  const state = location.state as LocationState;

  useEffect(() => {
    if (!state) {
      message.error('無效的頁面訪問');
      navigate('/');
    }
  }, [state, navigate]);

  if (!state) {
    return (
      <div style={{ textAlign: 'center', padding: '50px' }}>
        <Spin size="large" />
      </div>
    );
  }

  const { sessionId, recommendations, formData } = state;

  const handleStartABTest = async () => {
    setLoading(true);
    
    try {
      // Start A/B test session
      const abTestSession = await apiService.startABTest(formData);
      
      navigate('/ab-test', {
        state: {
          session: abTestSession,
        },
      });
    } catch (error) {
      console.error('Error starting A/B test:', error);
      message.error('無法啟動測試，請稍後再試');
    } finally {
      setLoading(false);
    }
  };

  const handlePlayMusic = (track: MusicTrack) => {
    // This would open a music player modal or navigate to a player page
    message.info(`播放: ${track.title}`);
  };

  const formatDuration = (seconds: number): string => {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = Math.floor(seconds % 60);
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
  };

  return (
    <div style={{ maxWidth: 1000, margin: '0 auto', padding: '24px' }}>
      <Card>
        <div style={{ textAlign: 'center', marginBottom: 32 }}>
          <Title level={2}>
            <SoundOutlined /> 為您推薦的睡眠音樂
          </Title>
          <Paragraph style={{ color: '#666', fontSize: 16 }}>
            基於您的偏好和狀態，我們為您精選了以下音樂
          </Paragraph>
        </div>

        {/* User preferences summary */}
        <Card
          title="您的偏好設定"
          size="small"
          style={{ marginBottom: 24, backgroundColor: '#f9f9f9' }}
        >
          <Space direction="vertical" size="small">
            <div>
              <Text strong>壓力指數：</Text>
              <Tag color="blue">{formData.stressLevel}</Tag>
            </div>
            <div>
              <Text strong>情緒狀態：</Text>
              <Tag color="green">{formData.emotionalState}</Tag>
            </div>
            <div>
              <Text strong>入睡目標：</Text>
              <Tag color="purple">{formData.sleepGoal}</Tag>
            </div>
            <div>
              <Text strong>入眠主題：</Text>
              <Tag color="orange">{formData.sleepTheme}</Tag>
            </div>
          </Space>
        </Card>

        {/* Recommendations list */}
        <List
          dataSource={recommendations}
          renderItem={(track, index) => (
            <List.Item
              actions={[
                <Button
                  type="primary"
                  icon={<PlayCircleOutlined />}
                  onClick={() => handlePlayMusic(track)}
                >
                  播放
                </Button>,
              ]}
            >
              <List.Item.Meta
                title={
                  <Space>
                    <Text strong>#{index + 1}</Text>
                    <Text>{track.title}</Text>
                    {track.similarity_score && (
                      <Tag color="cyan">
                        匹配度: {Math.round(track.similarity_score * 100)}%
                      </Tag>
                    )}
                  </Space>
                }
                description={
                  <Space direction="vertical" size="small">
                    {track.artist && (
                      <Text type="secondary">演出者: {track.artist}</Text>
                    )}
                    <Text type="secondary">
                      時長: {formatDuration(track.duration)}
                    </Text>
                    {track.metadata && (
                      <Space wrap>
                        {track.metadata.genre && (
                          <Tag>{track.metadata.genre}</Tag>
                        )}
                        {track.metadata.tempo && (
                          <Tag>{track.metadata.tempo}</Tag>
                        )}
                        {track.metadata.mood && (
                          <Tag>{track.metadata.mood}</Tag>
                        )}
                      </Space>
                    )}
                  </Space>
                }
              />
            </List.Item>
          )}
        />

        <Divider />

        {/* Action buttons */}
        <div style={{ textAlign: 'center' }}>
          <Space size="large">
            <Button
              size="large"
              icon={<HomeOutlined />}
              onClick={() => navigate('/')}
            >
              重新填寫表單
            </Button>
            <Button
              type="primary"
              size="large"
              icon={<ExperimentOutlined />}
              onClick={handleStartABTest}
              loading={loading}
            >
              參與音樂偏好測試
            </Button>
          </Space>
        </div>

        {/* Session info */}
        <div style={{ marginTop: 24, textAlign: 'center' }}>
          <Text type="secondary" style={{ fontSize: 12 }}>
            會話 ID: {sessionId}
          </Text>
        </div>
      </Card>
    </div>
  );
};
