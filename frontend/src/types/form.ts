/**
 * TypeScript types for the Symphony AI Sleep Recommendation Form
 * Based on FormDesign.md specifications
 */

// Form data structure matching the backend API
export interface FormData {
  stressLevel: string;
  physicalSymptoms: string[];
  emotionalState: string;
  sleepGoal: string;
  soundPreferences: string[];
  rhythmPreference: string;
  soundSensitivities: string[];
  playbackMode: string;
  guidedVoice: string;
  sleepTheme: string;
  timestamp?: string;
}

// Form field options
export const STRESS_LEVELS = [
  '非常輕鬆',
  '稍微有點壓力',
  '中度壓力',
  '很大壓力',
  '壓力爆表'
] as const;

export const PHYSICAL_SYMPTOMS = [
  '頭腦過度活躍',
  '肌肉緊繃',
  '心悸或心跳快',
  '呼吸急促',
  '沒有不適，身體放鬆'
] as const;

export const EMOTIONAL_STATES = [
  '焦慮',
  '沮喪',
  '平靜',
  '開心',
  '煩躁',
  '無感'
] as const;

export const SLEEP_GOALS = [
  '快速入眠',
  '維持整夜好眠',
  '深度放鬆情緒',
  '降低焦慮/壓力',
  '喚起正面情緒（愉悅/幸福感）'
] as const;

export const SOUND_PREFERENCES = [
  '自然聲（海浪、森林、雨聲）',
  '樂器聲（鋼琴、古典、弦樂）',
  '電子氛圍（低頻、白噪音、Lo-Fi）',
  '冥想音（頌缽、嗡鳴聲、深呼吸引導）',
  '無特定偏好，依AI推薦'
] as const;

export const RHYTHM_PREFERENCES = [
  '超慢（冥想般，幾乎無節奏）',
  '緩慢穩定（放鬆心跳）',
  '中低頻流動（輕柔有律動）',
  '完全無節奏（環境聲）'
] as const;

export const SOUND_SENSITIVITIES = [
  '低頻震動',
  '高頻刺耳聲',
  '重複旋律',
  '無，皆可接受'
] as const;

export const PLAYBACK_MODES = [
  '逐漸淡出（10~20分鐘入睡）',
  '全夜播放穩定背景音',
  '智慧偵測深睡後自動關閉',
  '無偏好'
] as const;

export const GUIDED_VOICE_OPTIONS = [
  '是，睡前呼吸引導',
  '是，情緒釋放引導',
  '否，只需要純音樂'
] as const;

export const SLEEP_THEMES = [
  '平靜如水（穩定神經）',
  '深海之夢（低頻深度放鬆）',
  '森林療癒（自然共振）',
  '星空冥想（輕盈與遼闊）',
  'AI自動推薦'
] as const;

// Type guards for form validation
export type StressLevel = typeof STRESS_LEVELS[number];
export type PhysicalSymptom = typeof PHYSICAL_SYMPTOMS[number];
export type EmotionalState = typeof EMOTIONAL_STATES[number];
export type SleepGoal = typeof SLEEP_GOALS[number];
export type SoundPreference = typeof SOUND_PREFERENCES[number];
export type RhythmPreference = typeof RHYTHM_PREFERENCES[number];
export type SoundSensitivity = typeof SOUND_SENSITIVITIES[number];
export type PlaybackMode = typeof PLAYBACK_MODES[number];
export type GuidedVoiceOption = typeof GUIDED_VOICE_OPTIONS[number];
export type SleepTheme = typeof SLEEP_THEMES[number];

// Form validation rules
export const REQUIRED_FIELDS = [
  'stressLevel',
  'emotionalState',
  'sleepGoal',
  'sleepTheme'
] as const;

// Form section structure for UI organization
export interface FormSection {
  id: string;
  title: string;
  description?: string;
  fields: string[];
}

export const FORM_SECTIONS: FormSection[] = [
  {
    id: 'physiological',
    title: '當日狀態評估',
    description: '請根據今天的實際感受填寫',
    fields: ['stressLevel', 'physicalSymptoms', 'emotionalState']
  },
  {
    id: 'goals',
    title: '入睡目標設定',
    description: '明確您今晚的主要需求',
    fields: ['sleepGoal']
  },
  {
    id: 'preferences',
    title: '聲音偏好',
    description: '選擇您喜歡的音樂類型和節奏',
    fields: ['soundPreferences', 'rhythmPreference']
  },
  {
    id: 'sensitivities',
    title: '敏感度設定',
    description: '告訴我們需要避免的聲音類型',
    fields: ['soundSensitivities']
  },
  {
    id: 'personalization',
    title: '個人化優化選項',
    description: '自訂您的聆聽體驗',
    fields: ['playbackMode', 'guidedVoice', 'sleepTheme']
  }
];
