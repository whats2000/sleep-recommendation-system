/**
 * Experiment Setup Page - Prepare for blind A/B testing
 */

import React, { useState, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import {
  Card,
  Button,
  Typography,
  Space,
  Tag,
  Divider,
  message,
  Spin,
  Alert,
} from 'antd';
import {
  ExperimentOutlined,
  HomeOutlined,
  SoundOutlined,
} from '@ant-design/icons';
import type { FormData } from '../types/form';

const { Title, Paragraph, Text } = Typography;

interface RecommendationResults {
  session_id: string;
  recommendations: unknown[];
  [key: string]: unknown;
}

interface LocationState {
  sessionId: string;
  formData: FormData;
  recommendationResults?: RecommendationResults; // Full recommendation results from the initial API call
}

export const ExperimentSetupPage: React.FC = () => {
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

  const { sessionId, formData, recommendationResults } = state;

  const handleStartABTest = async () => {
    setLoading(true);

    try {
      // Validate we have recommendation results
      if (!recommendationResults || !recommendationResults.recommendations) {
        message.error('沒有可用的推薦結果，請重新提交表單');
        return;
      }

      const recommendations = recommendationResults.recommendations;

      // Validate we have enough recommendations (need at least 5)
      if (recommendations.length < 5) {
        message.error('推薦結果不足，需要至少5首推薦音樂');
        return;
      }

      console.log('Creating A/B test with REAL music data...');
      console.log('Recommended tracks:', recommendations);

      // Get 5 random tracks from the database for comparison
      message.info('正在獲取隨機音樂樣本進行對比測試...');

      const randomTracksResponse = await fetch('/api/music/random?count=5');
      if (!randomTracksResponse.ok) {
        throw new Error('Failed to fetch random tracks');
      }

      const randomTracks = await randomTracksResponse.json();

      if (!randomTracks || randomTracks.length < 5) {
        throw new Error('Insufficient random tracks available');
      }

      console.log('Random tracks for comparison:', randomTracks);

      // Create 5 test pairs: each pair compares 1 recommended track vs 1 random track
      const testPairs = [];
      for (let i = 0; i < 5; i++) {
        const recommendedTrack = recommendations[i] as any;
        const randomTrack = randomTracks[i] as any;

        // Randomly decide which position (A or B) gets the recommended track
        const recommendedInA = Math.random() > 0.5;

        const trackA = recommendedInA ? {
          id: recommendedTrack.track_id || recommendedTrack.id,
          title: recommendedTrack.title,
          artist: recommendedTrack.artist,
          duration: recommendedTrack.duration || 180,
          file_path: recommendedTrack.file_path,
          similarity_score: recommendedTrack.similarity_score,
          metadata: recommendedTrack.metadata,
          track_type: 'recommended' // Mark as recommended track
        } : {
          id: randomTrack.track_id || randomTrack.id,
          title: randomTrack.title,
          artist: randomTrack.artist,
          duration: randomTrack.duration || 180,
          file_path: randomTrack.file_path,
          metadata: randomTrack.metadata,
          track_type: 'random' // Mark as random track
        };

        const trackB = recommendedInA ? {
          id: randomTrack.track_id || randomTrack.id,
          title: randomTrack.title,
          artist: randomTrack.artist,
          duration: randomTrack.duration || 180,
          file_path: randomTrack.file_path,
          metadata: randomTrack.metadata,
          track_type: 'random'
        } : {
          id: recommendedTrack.track_id || recommendedTrack.id,
          title: recommendedTrack.title,
          artist: recommendedTrack.artist,
          duration: recommendedTrack.duration || 180,
          file_path: recommendedTrack.file_path,
          similarity_score: recommendedTrack.similarity_score,
          metadata: recommendedTrack.metadata,
          track_type: 'recommended'
        };

        testPairs.push({
          id: `pair_${i + 1}`,
          track_a: trackA,
          track_b: trackB,
          position_randomized: recommendedInA,
          recommended_track_position: recommendedInA ? 'A' : 'B'
        });
      }

      // Create A/B test session with REAL music comparison
      const abTestSession = {
        session_id: sessionId,
        user_id: `user_${Date.now()}`,
        form_data: formData,
        test_pairs: testPairs,
        current_pair_index: 0,
        total_pairs: testPairs.length,
        start_time: new Date().toISOString(),
        recommendation_metadata: {
          reused_existing: true,
          recommendations_count: recommendations.length,
          random_tracks_count: randomTracks.length,
          test_type: 'recommended_vs_random',
          local_session: false // This uses REAL data
        }
      };

      console.log('Created A/B test session with REAL music data:', abTestSession);

      navigate('/ab-test', {
        state: {
          session: abTestSession,
        },
      });
    } catch (error) {
      console.error('Error creating A/B test session:', error);
      message.error('無法創建測試會話，請稍後再試');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: 800, margin: '0 auto', padding: '24px' }}>
      <Card>
        <div style={{ textAlign: 'center', marginBottom: 32 }}>
          <Title level={2}>
            <SoundOutlined /> 準備開始音樂偏好實驗
          </Title>
          <Paragraph style={{ color: '#666', fontSize: 16 }}>
            我們已根據您的偏好生成了個人化音樂，現在進行盲測實驗
          </Paragraph>
        </div>

        {/* Experiment explanation */}
        <Alert
          message="實驗說明"
          description={
            <div>
              <Paragraph>
                為了提供最準確的音樂推薦，我們需要進行盲測實驗：
              </Paragraph>
              <ul style={{ paddingLeft: 20 }}>
                <li>您將聆聽多組音樂對比</li>
                <li>每組包含兩首音樂（A 和 B）</li>
                <li>請選擇您更偏好的一首</li>
                <li>這將幫助我們改善推薦算法</li>
              </ul>
              <Paragraph style={{ marginTop: 16, fontWeight: 'bold', color: '#1890ff' }}>
                ⚠️ 重要：為確保實驗準確性，您將無法預先知道推薦的音樂內容
              </Paragraph>
            </div>
          }
          type="info"
          showIcon
          style={{ marginBottom: 24 }}
        />

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
              style={{
                minWidth: 180,
                background: 'linear-gradient(135deg, #1890ff 0%, #096dd9 100%)',
                border: 'none',
                boxShadow: '0 4px 12px rgba(24, 144, 255, 0.3)'
              }}
            >
              🎵 開始盲測實驗
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
