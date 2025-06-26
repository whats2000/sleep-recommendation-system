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
import { apiService } from '../services/api';

const { Title, Paragraph, Text } = Typography;

interface LocationState {
  sessionId: string;
  formData: FormData;
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

  const { sessionId, formData } = state;

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
