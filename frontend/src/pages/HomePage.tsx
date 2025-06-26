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
      // Submit form data to generate recommendations (but don't show them)
      const response = await apiService.getRecommendations(formData);

      message.success('分析完成，準備開始實驗！');

      // Navigate to experiment setup page with session data
      navigate('/experiment-setup', {
        state: {
          sessionId: response.session_id,
          formData,
        },
      });
    } catch (error) {
      console.error('Error generating recommendations:', error);
      message.error('分析失敗，請稍後再試');
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
