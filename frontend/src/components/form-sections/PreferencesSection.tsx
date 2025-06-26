/**
 * Preferences Section - Sound and Rhythm Preferences
 */

import React from 'react';
import { Form, Radio, Checkbox, Space, Typography } from 'antd';
import type { FormInstance } from 'antd';
import {
  SOUND_PREFERENCES,
  RHYTHM_PREFERENCES,
} from '../../types/form';

const { Text } = Typography;

interface PreferencesSectionProps {
  form: FormInstance;
  onChange: (field: string, value: any) => void;
}

export const PreferencesSection: React.FC<PreferencesSectionProps> = ({
  onChange,
}) => {
  return (
    <div className="form-section">
      <Space direction="vertical" size="large" style={{ width: '100%' }}>
        {/* Sound Preferences */}
        <Form.Item
          name="soundPreferences"
          label={
            <Text strong style={{ fontSize: 16 }}>
              你偏好的聲音類型是？（可複選）
            </Text>
          }
        >
          <Checkbox.Group
            onChange={(values) => onChange('soundPreferences', values)}
            style={{ width: '100%' }}
          >
            <Space direction="vertical" size="small" style={{ width: '100%' }}>
              {SOUND_PREFERENCES.map((preference) => (
                <Checkbox key={preference} value={preference} style={{ fontSize: 16 }}>
                  {preference}
                </Checkbox>
              ))}
            </Space>
          </Checkbox.Group>
        </Form.Item>

        {/* Rhythm Preferences */}
        <Form.Item
          name="rhythmPreference"
          label={
            <Text strong style={{ fontSize: 16 }}>
              音樂節奏偏好？
            </Text>
          }
        >
          <Radio.Group
            onChange={(e) => onChange('rhythmPreference', e.target.value)}
            style={{ width: '100%' }}
          >
            <Space direction="vertical" size="small" style={{ width: '100%' }}>
              {RHYTHM_PREFERENCES.map((rhythm) => (
                <Radio key={rhythm} value={rhythm} style={{ fontSize: 16 }}>
                  {rhythm}
                </Radio>
              ))}
            </Space>
          </Radio.Group>
        </Form.Item>
      </Space>
    </div>
  );
};
