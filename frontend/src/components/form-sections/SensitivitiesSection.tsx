/**
 * Sensitivities Section - Sound Sensitivities
 */

import React from 'react';
import { Form, Checkbox, Space, Typography } from 'antd';
import type { FormInstance } from 'antd';
import { SOUND_SENSITIVITIES } from '../../types/form';

const { Text } = Typography;

interface SensitivitiesSectionProps {
  form: FormInstance;
  onChange: (field: string, value: any) => void;
}

export const SensitivitiesSection: React.FC<SensitivitiesSectionProps> = ({
  onChange,
}) => {
  return (
    <div className="form-section">
      <Space direction="vertical" size="large" style={{ width: '100%' }}>
        {/* Sound Sensitivities */}
        <Form.Item
          name="soundSensitivities"
          label={
            <Text strong style={{ fontSize: 16 }}>
              對下列聲音是否敏感？（可複選）
            </Text>
          }
        >
          <Checkbox.Group
            onChange={(values) => onChange('soundSensitivities', values)}
            style={{ width: '100%' }}
          >
            <Space direction="vertical" size="small" style={{ width: '100%' }}>
              {SOUND_SENSITIVITIES.map((sensitivity) => (
                <Checkbox key={sensitivity} value={sensitivity} style={{ fontSize: 16 }}>
                  {sensitivity}
                </Checkbox>
              ))}
            </Space>
          </Checkbox.Group>
        </Form.Item>
      </Space>
    </div>
  );
};
