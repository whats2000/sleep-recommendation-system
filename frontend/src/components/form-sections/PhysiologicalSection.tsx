/**
 * Physiological Section - Stress, Physical Symptoms, and Emotional State
 */

import React from 'react';
import { Form, Radio, Checkbox, Space, Typography, Input } from 'antd';
import type { FormInstance } from 'antd';
import {
  STRESS_LEVELS,
  PHYSICAL_SYMPTOMS,
  EMOTIONAL_STATES,
} from '../../types/form';

const { Text } = Typography;

interface PhysiologicalSectionProps {
  form: FormInstance;
  onChange: (field: string, value: any) => void;
}

export const PhysiologicalSection: React.FC<PhysiologicalSectionProps> = ({
  onChange,
}) => {
  return (
    <div className="form-section">
      <Space direction="vertical" size="large" style={{ width: '100%' }}>
        {/* Email Field */}
        <Form.Item
          name="email"
          label={
            <Text strong style={{ fontSize: 16 }}>
              電子郵件地址
            </Text>
          }
          rules={[
            { required: true, message: '請輸入您的電子郵件地址' },
            { type: 'email', message: '請輸入有效的電子郵件地址' }
          ]}
        >
          <Input
            placeholder="請輸入您的電子郵件地址"
            size="large"
            onChange={(e) => onChange('email', e.target.value)}
          />
        </Form.Item>

        {/* Stress Level Assessment */}
        <Form.Item
          name="stressLevel"
          label={
            <Text strong style={{ fontSize: 16 }}>
              今天的壓力指數是多少？
            </Text>
          }
          rules={[{ required: true, message: '請選擇您的壓力指數' }]}
        >
          <Radio.Group
            onChange={(e) => onChange('stressLevel', e.target.value)}
            style={{ width: '100%' }}
          >
            <Space direction="vertical" size="small" style={{ width: '100%' }}>
              {STRESS_LEVELS.map((level) => (
                <Radio key={level} value={level} style={{ fontSize: 16 }}>
                  {level}
                </Radio>
              ))}
            </Space>
          </Radio.Group>
        </Form.Item>

        {/* Physical Symptoms */}
        <Form.Item
          name="physicalSymptoms"
          label={
            <Text strong style={{ fontSize: 16 }}>
              身體感受（可複選）
            </Text>
          }
        >
          <Checkbox.Group
            onChange={(values) => onChange('physicalSymptoms', values)}
            style={{ width: '100%' }}
          >
            <Space direction="vertical" size="small" style={{ width: '100%' }}>
              {PHYSICAL_SYMPTOMS.map((symptom) => (
                <Checkbox key={symptom} value={symptom} style={{ fontSize: 16 }}>
                  {symptom}
                </Checkbox>
              ))}
            </Space>
          </Checkbox.Group>
        </Form.Item>

        {/* Emotional State */}
        <Form.Item
          name="emotionalState"
          label={
            <Text strong style={{ fontSize: 16 }}>
              今天的情緒主要是？
            </Text>
          }
          rules={[{ required: true, message: '請選擇您的主要情緒狀態' }]}
        >
          <Radio.Group
            onChange={(e) => onChange('emotionalState', e.target.value)}
            style={{ width: '100%' }}
          >
            <Space direction="vertical" size="small" style={{ width: '100%' }}>
              {EMOTIONAL_STATES.map((state) => (
                <Radio key={state} value={state} style={{ fontSize: 16 }}>
                  {state}
                </Radio>
              ))}
            </Space>
          </Radio.Group>
        </Form.Item>
      </Space>
    </div>
  );
};
