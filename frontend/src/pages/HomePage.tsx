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
      // Submit form data to get recommendations
      const response = await apiService.getRecommendations(formData);
      
      message.success('推薦生成成功！');
      
      // Navigate to recommendations page with session data
      navigate('/recommendations', {
        state: {
          sessionId: response.session_id,
          recommendations: response.recommendations,
          formData,
        },
      });
    } catch (error) {
      console.error('Error getting recommendations:', error);
      message.error('獲取推薦失敗，請稍後再試');
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
