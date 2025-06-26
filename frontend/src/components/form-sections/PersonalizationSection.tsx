/**
 * Personalization Section - Playback Mode, Guided Voice, and Sleep Theme
 */

import React from 'react';
import { Form, Radio, Space, Typography } from 'antd';
import type { FormInstance } from 'antd';
import {
  PLAYBACK_MODES,
  GUIDED_VOICE_OPTIONS,
  SLEEP_THEMES,
} from '../../types/form';

const { Text } = Typography;

interface PersonalizationSectionProps {
  form: FormInstance;
  onChange: (field: string, value: any) => void;
}

export const PersonalizationSection: React.FC<PersonalizationSectionProps> = ({
  onChange,
}) => {
  return (
    <div className="form-section">
      <Space direction="vertical" size="large" style={{ width: '100%' }}>
        {/* Playback Mode */}
        <Form.Item
          name="playbackMode"
          label={
            <Text strong style={{ fontSize: 16 }}>
              你喜歡音樂播放的方式？
            </Text>
          }
        >
          <Radio.Group
            onChange={(e) => onChange('playbackMode', e.target.value)}
            style={{ width: '100%' }}
          >
            <Space direction="vertical" size="small" style={{ width: '100%' }}>
              {PLAYBACK_MODES.map((mode) => (
                <Radio key={mode} value={mode} style={{ fontSize: 16 }}>
                  {mode}
                </Radio>
              ))}
            </Space>
          </Radio.Group>
        </Form.Item>

        {/* Guided Voice */}
        <Form.Item
          name="guidedVoice"
          label={
            <Text strong style={{ fontSize: 16 }}>
              今晚是否想搭配引導式語音？
            </Text>
          }
        >
          <Radio.Group
            onChange={(e) => onChange('guidedVoice', e.target.value)}
            style={{ width: '100%' }}
          >
            <Space direction="vertical" size="small" style={{ width: '100%' }}>
              {GUIDED_VOICE_OPTIONS.map((option) => (
                <Radio key={option} value={option} style={{ fontSize: 16 }}>
                  {option}
                </Radio>
              ))}
            </Space>
          </Radio.Group>
        </Form.Item>

        {/* Sleep Theme */}
        <Form.Item
          name="sleepTheme"
          label={
            <Text strong style={{ fontSize: 16 }}>
              請選擇今晚的入眠主題：
            </Text>
          }
          rules={[{ required: true, message: '請選擇入眠主題' }]}
        >
          <Radio.Group
            onChange={(e) => onChange('sleepTheme', e.target.value)}
            style={{ width: '100%' }}
          >
            <Space direction="vertical" size="small" style={{ width: '100%' }}>
              {SLEEP_THEMES.map((theme) => (
                <Radio key={theme} value={theme} style={{ fontSize: 16 }}>
                  {theme}
                </Radio>
              ))}
            </Space>
          </Radio.Group>
        </Form.Item>
      </Space>
    </div>
  );
};
