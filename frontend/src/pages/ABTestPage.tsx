/**
 * A/B Test Page - Blind music comparison testing
 */

import React, { useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { message, Result, Button } from 'antd';
import { CheckCircleOutlined, HomeOutlined } from '@ant-design/icons';
import { ABTestInterface } from '../components/ABTestInterface';
import type { ABTestSession, ABTestResult } from '../types/api';
import { apiService } from '../services/api';

interface LocationState {
  session: ABTestSession;
}

export const ABTestPage: React.FC = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const [completed, setCompleted] = useState(false);
  const [, setSubmitting] = useState(false);

  const state = location.state as LocationState;

  if (!state?.session) {
    return (
      <Result
        status="error"
        title="無效的測試會話"
        subTitle="請重新開始測試流程"
        extra={
          <Button type="primary" onClick={() => navigate('/')}>
            返回首頁
          </Button>
        }
      />
    );
  }

  const { session } = state;

  const handleTestComplete = async (result: ABTestResult) => {
    setSubmitting(true);

    try {
      // Submit test results to backend with complete session data
      await apiService.submitABTestResults({
        session_id: session.session_id,
        results: result,
        session_data: session, // Include the complete session data
      });

      message.success('測試結果已提交，感謝您的參與！');
      setCompleted(true);
    } catch (error) {
      console.error('Error submitting test results:', error);
      message.error('提交結果失敗，請稍後再試');
    } finally {
      setSubmitting(false);
    }
  };

  const handleError = (error: string) => {
    message.error(error);
  };

  if (completed) {
    return (
      <div style={{ maxWidth: 600, margin: '0 auto', padding: '50px 24px' }}>
        <Result
          icon={<CheckCircleOutlined style={{ color: '#52c41a' }} />}
          title="測試完成！"
          subTitle="感謝您參與音樂偏好測試，您的回饋將幫助我們改善推薦系統"
          extra={[
            <Button type="primary" key="home" onClick={() => navigate('/')}>
              <HomeOutlined /> 返回首頁
            </Button>,
          ]}
        />
      </div>
    );
  }

  return (
    <ABTestInterface
      session={session}
      onComplete={handleTestComplete}
      onError={handleError}
    />
  );
};
