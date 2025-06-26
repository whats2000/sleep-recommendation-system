/**
 * Main Sleep Recommendation Form Component
 * Based on FormDesign.md specifications
 */

import React, { useState } from 'react';
import {
  Form,
  Card,
  Button,
  Steps,
  message,
  Space,
  Typography,
  Progress,
} from 'antd';
import type {
  FormData,
} from '../types/form';
import {
  FORM_SECTIONS,
  REQUIRED_FIELDS,
} from '../types/form';
import { PhysiologicalSection } from './form-sections/PhysiologicalSection';
import { GoalsSection } from './form-sections/GoalsSection';
import { PreferencesSection } from './form-sections/PreferencesSection';
import { SensitivitiesSection } from './form-sections/SensitivitiesSection';
import { PersonalizationSection } from './form-sections/PersonalizationSection';

const { Title, Paragraph } = Typography;

interface SleepRecommendationFormProps {
  onSubmit: (formData: FormData) => void;
  loading?: boolean;
}

export const SleepRecommendationForm: React.FC<SleepRecommendationFormProps> = ({
  onSubmit,
  loading = false,
}) => {
  const [form] = Form.useForm();
  const [currentStep, setCurrentStep] = useState(0);
  const [formData, setFormData] = useState<Partial<FormData>>({});

  // Calculate form completion percentage
  const calculateProgress = (): number => {
    const totalFields = REQUIRED_FIELDS.length;
    const completedFields = REQUIRED_FIELDS.filter(
      field => formData[field as keyof FormData]
    ).length;
    return Math.round((completedFields / totalFields) * 100);
  };

  // Handle form field changes
  const handleFieldChange = (field: string, value: any) => {
    setFormData(prev => ({
      ...prev,
      [field]: value,
    }));

    // Also update the form instance to ensure consistency
    form.setFieldValue(field, value);
  };

  // Validate current step
  const validateCurrentStep = async (): Promise<boolean> => {
    const currentSection = FORM_SECTIONS[currentStep];
    const fieldsToValidate = currentSection.fields.filter(field =>
      REQUIRED_FIELDS.includes(field as any)
    );

    try {
      // Get current form values and sync with local state
      const currentValues = form.getFieldsValue();
      setFormData(prev => ({ ...prev, ...currentValues }));

      await form.validateFields(fieldsToValidate);
      return true;
    } catch (error) {
      message.error('請完成必填項目後再繼續');
      return false;
    }
  };

  // Handle next step
  const handleNext = async () => {
    if (await validateCurrentStep()) {
      setCurrentStep(prev => Math.min(prev + 1, FORM_SECTIONS.length - 1));
    }
  };

  // Handle previous step
  const handlePrevious = () => {
    setCurrentStep(prev => Math.max(prev - 1, 0));
  };

  // Handle form submission
  const handleSubmit = async () => {
    try {
      // First sync all form values with local state
      const currentValues = form.getFieldsValue();
      const mergedData = { ...formData, ...currentValues };
      setFormData(mergedData);

      const values = await form.validateFields();
      console.log('Form values before submission:', values);
      console.log('Merged form data:', mergedData);

      // Check if all required fields are present in the merged data
      const missingFields = REQUIRED_FIELDS.filter(field => !mergedData[field]);
      if (missingFields.length > 0) {
        console.error('Missing required fields:', missingFields);
        message.error(`請填寫必填項目: ${missingFields.join(', ')}`);
        return;
      }

      const completeFormData: FormData = {
        ...mergedData,
        timestamp: new Date().toISOString(),
      };
      console.log('Complete form data:', completeFormData);
      onSubmit(completeFormData);
    } catch (error) {
      console.error('Form validation error:', error);
      message.error('請檢查並完成所有必填項目');
    }
  };

  // Render current step content
  const renderStepContent = () => {
    const section = FORM_SECTIONS[currentStep];
    
    switch (section.id) {
      case 'physiological':
        return (
          <PhysiologicalSection
            form={form}
            onChange={handleFieldChange}
          />
        );
      case 'goals':
        return (
          <GoalsSection
            form={form}
            onChange={handleFieldChange}
          />
        );
      case 'preferences':
        return (
          <PreferencesSection
            form={form}
            onChange={handleFieldChange}
          />
        );
      case 'sensitivities':
        return (
          <SensitivitiesSection
            form={form}
            onChange={handleFieldChange}
          />
        );
      case 'personalization':
        return (
          <PersonalizationSection
            form={form}
            onChange={handleFieldChange}
          />
        );
      default:
        return null;
    }
  };

  const progress = calculateProgress();
  const isLastStep = currentStep === FORM_SECTIONS.length - 1;
  const isFirstStep = currentStep === 0;

  return (
    <div style={{ maxWidth: 900, margin: '0 auto', padding: '24px' }}>
      <Card style={{ borderRadius: 12, boxShadow: '0 4px 12px rgba(0,0,0,0.1)' }}>
        <div style={{ marginBottom: 32 }}>
          <Title level={2} style={{ textAlign: 'center', marginBottom: 16, color: '#1890ff' }}>
            🎵 Symphony AI 睡眠音樂推薦
          </Title>
          <Paragraph style={{ textAlign: 'center', color: '#666', fontSize: 16 }}>
            請填寫以下問卷，我們將為您推薦最適合的睡眠音樂
          </Paragraph>

          {/* Progress indicator */}
          <div className="progress-indicator" style={{ marginBottom: 24 }}>
            <Progress
              percent={progress}
              strokeColor={{
                '0%': '#108ee9',
                '100%': '#87d068',
              }}
              format={() => `${progress}% 完成`}
              size={8}
            />
          </div>
        </div>

        {/* Steps indicator */}
        <Steps
          current={currentStep}
          size="small"
          style={{ marginBottom: 32 }}
          items={FORM_SECTIONS.map((section, index) => ({
            title: section.title,
            status: currentStep === index ? 'process' : currentStep > index ? 'finish' : 'wait',
          }))}
        />

        {/* Form content */}
        <Form
          form={form}
          layout="vertical"
          onValuesChange={(changedValues) => {
            Object.entries(changedValues).forEach(([field, value]) => {
              handleFieldChange(field, value);
            });
          }}
        >
          <Card
            title={
              <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                <span style={{
                  background: '#1890ff',
                  color: 'white',
                  borderRadius: '50%',
                  width: 24,
                  height: 24,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontSize: 12,
                  fontWeight: 'bold'
                }}>
                  {currentStep + 1}
                </span>
                {FORM_SECTIONS[currentStep].title}
              </div>
            }
            style={{
              marginBottom: 32,
              borderRadius: 8,
              border: '1px solid #e8f4fd'
            }}
            styles={{
              header: {
                background: '#f8fcff',
                borderRadius: '8px 8px 0 0'
              }
            }}
          >
            {FORM_SECTIONS[currentStep].description && (
              <Paragraph style={{ marginBottom: 24, color: '#666', fontSize: 15 }}>
                {FORM_SECTIONS[currentStep].description}
              </Paragraph>
            )}

            {renderStepContent()}
          </Card>

          {/* Navigation buttons */}
          <div style={{
            textAlign: 'center',
            padding: '24px 0',
            borderTop: '1px solid #f0f0f0',
            marginTop: 24
          }}>
            <Space size="large">
              <Button
                onClick={handlePrevious}
                disabled={isFirstStep}
                size="large"
                style={{ minWidth: 100 }}
              >
                上一步
              </Button>

              {!isLastStep ? (
                <Button
                  type="primary"
                  onClick={handleNext}
                  size="large"
                  style={{ minWidth: 100 }}
                >
                  下一步
                </Button>
              ) : (
                <Button
                  type="primary"
                  onClick={handleSubmit}
                  loading={loading}
                  size="large"
                  style={{
                    minWidth: 160,
                    background: 'linear-gradient(135deg, #1890ff 0%, #096dd9 100%)',
                    border: 'none',
                    boxShadow: '0 4px 12px rgba(24, 144, 255, 0.3)'
                  }}
                >
                  {loading ? '🎵 AI 正在分析中...' : '🎵 獲取推薦 (需1-3分鐘)'}
                </Button>
              )}
            </Space>
          </div>
        </Form>
      </Card>
    </div>
  );
};
