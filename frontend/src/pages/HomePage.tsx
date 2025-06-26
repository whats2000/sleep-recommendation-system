/**
 * Home Page - Main entry point with form
 */

import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { message } from 'antd';
import { SleepRecommendationForm } from '../components/SleepRecommendationForm';
import type { FormData } from '../types/form';
import { apiService } from '../services/api';

export const HomePage: React.FC = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);

  const handleFormSubmit = async (formData: FormData) => {
    setLoading(true);

    try {
      // Show a message about processing time
      message.info('正在分析您的需求並生成個人化推薦，這可能需要 1-3 分鐘，請耐心等待...', 5);

      // Submit form data to generate recommendations (but don't show them)
      const response = await apiService.getRecommendations(formData);

      message.success('分析完成，準備開始實驗！');

      // Navigate to experiment setup page with session data AND recommendation results
      navigate('/experiment-setup', {
        state: {
          sessionId: response.session_id,
          formData,
          recommendationResults: response, // Pass the full recommendation results
        },
      });
    } catch (error) {
      console.error('Error generating recommendations:', error);
      if (error.code === 'ECONNABORTED') {
        message.error('請求超時，請檢查網路連接或稍後再試');
      } else {
        message.error('分析失敗，請稍後再試');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <SleepRecommendationForm
      onSubmit={handleFormSubmit}
      loading={loading}
    />
  );
};
