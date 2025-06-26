/**
 * Goals Section - Sleep Goal Setting
 */

import React from 'react';
import { Form, Radio, Space, Typography } from 'antd';
import type { FormInstance } from 'antd';
import { SLEEP_GOALS } from '../../types/form';

const { Text } = Typography;

interface GoalsSectionProps {
  form: FormInstance;
  onChange: (field: string, value: any) => void;
}

export const GoalsSection: React.FC<GoalsSectionProps> = ({
  onChange,
}) => {
  return (
    <div className="form-section">
      <Space direction="vertical" size="large" style={{ width: '100%' }}>
        {/* Sleep Goal */}
        <Form.Item
          name="sleepGoal"
          label={
            <Text strong style={{ fontSize: 16 }}>
              今晚你的主要入睡目標是？
            </Text>
          }
          rules={[{ required: true, message: '請選擇您的入睡目標' }]}
        >
          <Radio.Group
            onChange={(e) => onChange('sleepGoal', e.target.value)}
            style={{ width: '100%' }}
          >
            <Space direction="vertical" size="small" style={{ width: '100%' }}>
              {SLEEP_GOALS.map((goal) => (
                <Radio key={goal} value={goal} style={{ fontSize: 16 }}>
                  {goal}
                </Radio>
              ))}
            </Space>
          </Radio.Group>
        </Form.Item>
      </Space>
    </div>
  );
};
