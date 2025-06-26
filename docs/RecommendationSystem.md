# Symphony AI 推薦系統實現文件

## 概述

本文件描述了 Symphony AI 睡眠音樂推薦系統的實際實現架構與功能。系統採用 LangGraph 多代理工作流程，結合大型語言模型、MusicGen 音樂生成技術和 CLAP 向量相似度搜尋，為用戶提供個性化的睡眠音樂推薦。系統已實現完整的 A/B 測試實驗流程，用於驗證推薦系統的有效性。

## 系統目標

### 已實現的主要目標
- **個性化推薦**: ✅ 基於用戶生理心理狀態提供客製化音樂推薦
- **智能音樂生成**: ✅ 利用 MusicGen 技術動態生成符合需求的參考音樂
- **科學驗證**: ✅ 通過完整的 A/B 測試實驗設計驗證推薦系統效果
- **用戶體驗優化**: ✅ 提供直觀易用的多步驟表單和音樂播放界面

### 已達成的技術目標
- **推薦準確性**: ✅ 實現基於 CLAP 向量嵌入的高品質音樂語義匹配
- **系統響應性**: ✅ 保持良好的用戶互動體驗，支援音樂播放控制
- **實驗可重複性**: ✅ 建立標準化的 A/B 測試評估流程
- **數據收集完整性**: ✅ 全面記錄用戶行為、偏好數據和實驗結果

## 實際系統架構

### 已實現的整體流程圖

```mermaid
flowchart TD
    A[用戶填寫多步驟表單] --> B[LangGraph 五代理分析]
    B --> C[生成 MusicGen 提示詞]
    C --> D[MusicGen 音樂合成<br/>facebook/musicgen-small]
    D --> E[CLAP 音頻編碼<br/>laion/clap-htsat-unfused]
    E --> F[餘弦相似度搜尋]
    F --> G[Top 5 推薦結果]
    G --> H[A/B 測試配對生成]
    H --> I[盲測實驗界面<br/>Web Audio API]
    I --> J[記錄用戶偏好選擇]
    J --> K[實驗結果分析]

    L[(預編碼音樂庫<br/>200+ 音頻檔案)] --> F
    M[(隨機音樂庫)] --> H
```

### 實際系統組件架構

```mermaid
graph TB
    subgraph "前端界面層 (React + TypeScript)"
        UI[多步驟表單界面<br/>Ant Design]
        PLAYER[音樂播放器<br/>Web Audio API]
        TEST[A/B 測試界面<br/>盲測設計]
        RESULTS[推薦結果展示]
    end

    subgraph "後端 API 層 (Flask + RESTful)"
        API[Flask API Gateway<br/>CORS 支援]
        REC_API[推薦 API<br/>/api/recommendations]
        EXP_API[實驗 API<br/>/api/experiment]
        MUSIC_API[音樂 API<br/>/api/music]
        PIPELINE_API[管線 API<br/>/api/pipeline]
    end

    subgraph "業務邏輯層"
        WORKFLOW[LangGraph 工作流程<br/>5 個專業代理]
        RECOMMEND[推薦服務<br/>RecommendationService]
        EXPERIMENT[實驗服務<br/>ExperimentService]
        MUSIC_GEN[音樂生成服務<br/>MusicGenerationService]
    end

    subgraph "AI 模型層"
        LLM[OpenAI GPT-4o-mini<br/>或 Google Gemini-2.0-flash]
        MUSICGEN[MusicGen 模型<br/>facebook/musicgen-small]
        CLAP[CLAP 編碼模型<br/>laion/clap-htsat-unfused]
    end

    subgraph "數據存儲層 (本地檔案系統)"
        EMBEDDINGS[向量嵌入檔案<br/>embeddings.pkl]
        DATASET[音頻檔案庫<br/>dataset/ 目錄]
        GENERATED[生成音頻<br/>generated_audio/ 目錄]
        EXP_DATA[實驗數據<br/>data/experiments/ 目錄]
    end

    UI --> API
    PLAYER --> MUSIC_API
    TEST --> EXP_API
    RESULTS --> REC_API

    API --> WORKFLOW
    REC_API --> RECOMMEND
    EXP_API --> EXPERIMENT
    MUSIC_API --> DATASET
    PIPELINE_API --> WORKFLOW

    WORKFLOW --> LLM
    RECOMMEND --> MUSIC_GEN
    MUSIC_GEN --> MUSICGEN
    RECOMMEND --> CLAP
    RECOMMEND --> EMBEDDINGS
    EXPERIMENT --> EXP_DATA

    CLAP --> EMBEDDINGS
    MUSICGEN --> GENERATED
    EMBEDDINGS --> DATASET
```

## 已實現的推薦系統核心組件

### 1. LangGraph 多代理工作流程 (已實現)

#### 1.1 實際代理架構

```mermaid
graph LR
    INPUT[表單數據輸入<br/>FormData] --> SA[狀態分析代理<br/>state_analysis_agent]
    INPUT --> EA[情緒識別代理<br/>emotion_recognition_agent]
    INPUT --> PA[偏好分析代理<br/>preference_analysis_agent]

    SA --> IA[需求整合代理<br/>requirement_integration_agent]
    EA --> IA
    PA --> IA

    IA --> PG[提示詞生成代理<br/>prompt_generation_agent]
    PG --> OUTPUT[MusicGen 提示詞輸出<br/>GeneratedPrompt]
```

#### 1.2 實際代理實現與職責

**狀態分析代理 (State Analysis Agent)** - `src/nodes/state_analysis.py`
- **輸入數據**: 壓力指數 (stress_level)、身體症狀 (physical_symptoms)、情緒狀態 (emotional_state)
- **分析功能**: 使用 LLM 評估用戶當前生理心理狀態
- **輸出結果**: StateAnalysis 物件，包含狀態摘要和緊急程度評估
- **實現**: 使用 OpenAI GPT-4o-mini 或 Google Gemini-2.0-flash

**情緒識別代理 (Emotion Recognition Agent)** - `src/nodes/emotion_recognition.py`
- **輸入數據**: 情緒狀態 (emotional_state)、入睡目標 (sleep_goal)
- **分析功能**: 識別主導情緒和情緒調節需求
- **輸出結果**: EmotionAnalysis 物件，包含情緒標籤和調節策略
- **實現**: 結構化 LLM 提示詞分析情緒模式

**偏好分析代理 (Preference Analysis Agent)** - `src/nodes/preference_analysis.py`
- **輸入數據**: 聲音偏好 (sound_preferences)、節奏偏好 (rhythm_preference)、敏感度設定 (sound_sensitivities)
- **分析功能**: 分析用戶音樂偏好和限制條件
- **輸出結果**: PreferenceAnalysis 物件，包含偏好矩陣和禁忌列表
- **實現**: 智能解析用戶偏好選項並生成音樂特徵描述

**需求整合代理 (Requirement Integration Agent)** - `src/nodes/requirement_integration.py`
- **輸入數據**: 各代理的分析結果 (StateAnalysis, EmotionAnalysis, PreferenceAnalysis)
- **整合功能**: 統合所有需求，解決衝突，考慮個人化選項
- **輸出結果**: IntegratedRequirements 物件，統一的需求規格
- **實現**: 智能衝突解決和需求優先級排序

**提示詞生成代理 (Prompt Generation Agent)** - `src/nodes/prompt_generation.py`
- **輸入數據**: 整合需求規格 (IntegratedRequirements)
- **生成功能**: 產生結構化的 MusicGen 提示詞
- **輸出結果**: GeneratedPrompt 物件，包含最佳化的音樂生成指令
- **實現**: 專業音樂術語生成，適配 MusicGen 模型要求

### 2. MusicGen 音樂合成模組 (已實現)

#### 2.1 實際實現規格 - `src/service/music_generation.py`

**使用模型**: `facebook/musicgen-small`
**實現方式**: Transformers Pipeline (`text-to-audio`)
**音頻長度限制**: 最大 15 秒 (防止記憶體問題)
**設備支援**: CUDA GPU 或 CPU 自動偵測

**實際提示詞結構組件**
- **音樂類型** (Genre): ambient, lo-fi, classical, electronic, peaceful
- **節奏速度** (Tempo): very slow, slow, moderate, rhythmless
- **情緒氛圍** (Mood): calming, soothing, peaceful, relaxing, meditative
- **樂器選擇** (Instruments): piano, guitar, strings, synthesizer, flute, bells
- **音樂特徵** (Characteristics): soft, gentle, melodic, harmonic, ethereal
- **頻率調諧** (Frequency): 432Hz (當用戶選擇時)
- **音樂長度** (Duration): 固定 15 秒 (技術限制)

#### 2.2 實際提示詞生成流程

```mermaid
flowchart TD
    A[LangGraph 代理分析結果] --> B[提示詞生成代理]
    B --> C[提示詞清理與驗證]
    C --> D{提示詞長度檢查}

    D -->|太短| E[使用預設提示詞<br/>ambient music, slow tempo, peaceful, relaxing]
    D -->|適當| F[MusicGen Pipeline]

    E --> F
    F --> G[生成 15 秒音頻]
    G --> H[儲存到 generated_audio/]
    H --> I[CLAP 編碼處理]
```

#### 2.3 實際音樂生成服務特性

**錯誤處理**: 完整的異常處理，避免系統崩潰
**提示詞清理**: 自動移除無效字符，確保 MusicGen 相容性
**檔案管理**: 自動生成唯一檔名，避免衝突
**記憶體管理**: 限制音頻長度，防止 GPU 記憶體溢出

### 3. CLAP 音頻編碼與向量搜尋 (已實現)

#### 3.1 實際音頻處理流程 - `src/utils/vector_search.py`

**使用模型**: `laion/clap-htsat-unfused`
**向量維度**: 512 維度嵌入向量
**音頻格式支援**: WAV, MP3, M4A 等多種格式
**資料庫**: 本地 pickle 檔案 (`data/embeddings.pkl`)

```mermaid
flowchart LR
    A[音頻檔案<br/>dataset/ 目錄] --> B[CLAP 模型載入<br/>laion/clap-htsat-unfused]
    B --> C[音頻預處理<br/>採樣率標準化]
    C --> D[CLAP 編碼<br/>512 維向量]
    D --> E[向量儲存<br/>embeddings.pkl]
    E --> F[元數據關聯<br/>檔案路徑、名稱]
```

#### 3.2 實際相似度搜尋實現

**搜尋算法**: 餘弦相似度 (Cosine Similarity)
**搜尋庫**: scikit-learn cosine_similarity
**資料庫大小**: 200+ 預編碼音頻檔案
**搜尋效能**: 即時搜尋，毫秒級響應

```mermaid
sequenceDiagram
    participant U as 用戶
    participant API as Flask API
    participant RS as RecommendationService
    participant MG as MusicGen
    participant CLAP as CLAP 編碼器
    participant VS as 向量搜尋引擎
    participant DB as embeddings.pkl

    U->>API: 提交表單數據
    API->>RS: 呼叫推薦服務
    RS->>RS: LangGraph 多代理分析
    RS->>MG: 生成參考音樂 (15秒)
    MG->>CLAP: 編碼音頻為 512 維向量
    CLAP->>VS: 查詢向量
    VS->>DB: 計算餘弦相似度
    DB->>VS: 返回 Top 5 相似音樂
    VS->>API: 推薦音樂列表 + 元數據
    API->>U: JSON 格式推薦結果
```

#### 3.3 實際資料庫結構

**音頻檔案庫**: `backend/dataset/` (200+ 檔案)
- 包含多種睡眠音樂類型：搖籃曲、自然聲音、環境音樂
- 支援多種音頻格式：WAV, MP3, M4A
- 檔案命名包含描述性資訊

**向量資料庫**: `backend/data/embeddings.pkl`
- 結構：`{file_id: numpy_array_512d}`
- 元數據：檔案路徑、名稱、藝術家資訊
- 自動更新機制：新增檔案時重新編碼

### 4. 推薦引擎邏輯 (已實現)

#### 4.1 實際推薦策略 - `src/service/recommendation_service.py`

```mermaid
flowchart TD
    A[用戶表單輸入<br/>FormData] --> B[LangGraph 五代理分析<br/>RecommendationPipeline]
    B --> C[生成參考音樂<br/>MusicGenerationService]
    C --> D[CLAP 向量編碼<br/>512 維嵌入]
    D --> E[餘弦相似度計算<br/>search_similar_tracks]
    E --> F[Top 5 推薦結果<br/>包含相似度分數]
    F --> G[結果格式化<br/>包含元數據]
```

#### 4.2 實際排序算法

**主要排序依據**: 餘弦相似度分數 (0.0 - 1.0)
**結果格式**:
```json
{
  "track_id": "unique_file_id",
  "title": "音樂標題",
  "artist": "藝術家",
  "file_path": "相對檔案路徑",
  "similarity_score": 0.85,
  "metadata": {
    "file_name": "原始檔名",
    "duration": "音頻長度"
  }
}
```

**品質保證機制**:
- 自動過濾損壞的音頻檔案
- 確保推薦結果的多樣性
- 錯誤處理：無結果時返回預設推薦

## A/B 測試實驗設計 (已完整實現)

### 實際實驗流程架構

```mermaid
flowchart TD
    A[用戶填寫表單<br/>多步驟表單] --> B[系統生成推薦<br/>RecommendationService]
    B --> C[獲得 Top 5 推薦音樂<br/>基於向量相似度]
    C --> D[隨機選取 5 首對照音樂<br/>排除高相似度音樂]
    D --> E[A/B 配對組合<br/>ExperimentService]
    E --> F[盲測界面呈現<br/>ABTestInterface]
    F --> G[用戶進行 5 次偏好選擇<br/>Web Audio API 播放]
    G --> H[記錄詳細選擇數據<br/>播放次數、聆聽時間]
    H --> I[實驗結果儲存<br/>data/experiments/]
    I --> J[數據分析與統計<br/>API 端點支援]
```

### 實際實驗設計實現

#### 1. 數據收集階段 (已實現)

**實際表單數據收集** - `frontend/src/types/form.ts`
- **用戶識別**: 電子郵件地址 (必填)
- **生理狀態**: 壓力指數、身體症狀
- **心理狀態**: 情緒狀態、入睡目標
- **音樂偏好**: 聲音類型、節奏偏好、敏感度設定
- **個人化選項**: 播放模式、引導語音、睡眠主題

**表單實現特性**:
- 多步驟界面設計 (5 個步驟)
- 即時驗證和狀態保存
- Ant Design 組件庫
- TypeScript 類型安全

#### 2. 推薦生成階段 (已實現)

```mermaid
graph LR
    A[表單輸入<br/>FormData] --> B[LangGraph 分析<br/>5 個代理]
    B --> C[MusicGen 生成<br/>15秒參考音樂]
    C --> D[CLAP 編碼<br/>512維向量]
    D --> E[向量搜尋<br/>餘弦相似度]
    E --> F[Top 5 推薦<br/>相似度排序]

    G[音樂資料庫<br/>200+ 檔案] --> H[隨機選取 5 首<br/>排除高相似度音樂]
    H --> I[對照組音樂<br/>隨機基準]
```

#### 3. A/B 測試配對設計 (已實現)

**實際配對策略** - `src/service/experiment_service.py`
- **測試組**: Top 5 推薦音樂 (基於 AI 分析)
- **對照組**: 5 首隨機音樂 (排除與推薦音樂高相似度的檔案)
- **配對方式**: 1對1 隨機配對，共 5 輪測試
- **呈現順序**: 隨機化 A/B 位置，避免位置偏誤
- **盲測保證**: 不顯示音樂來源、標題或任何識別資訊

#### 4. 盲測實驗界面 (已實現)

**實際界面實現** - `frontend/src/components/ABTestInterface.tsx`

```mermaid
stateDiagram-v2
    [*] --> 實驗說明頁面
    實驗說明頁面 --> 第一輪測試: 開始實驗
    第一輪測試 --> 第二輪測試: 選擇完成
    第二輪測試 --> 第三輪測試: 選擇完成
    第三輪測試 --> 第四輪測試: 選擇完成
    第四輪測試 --> 第五輪測試: 選擇完成
    第五輪測試 --> 結果提交: 完成測試
    結果提交 --> [*]: 實驗結束

    第一輪測試 --> 第一輪測試: 重新播放音樂
    第二輪測試 --> 第二輪測試: 重新播放音樂
    第三輪測試 --> 第三輪測試: 重新播放音樂
    第四輪測試 --> 第四輪測試: 重新播放音樂
    第五輪測試 --> 第五輪測試: 重新播放音樂
```

**實際界面功能**
- **盲測保證**: ✅ 完全不顯示音樂來源、標題或任何識別資訊
- **播放控制**: ✅ Web Audio API 實現，支援播放/暫停/重播
- **選擇記錄**: ✅ 清楚的 A/B 選項，Radio Button 設計
- **進度顯示**: ✅ 進度條顯示測試進度（1/5, 2/5...）
- **時間記錄**: ✅ 精確記錄每輪選擇的決策時間 (毫秒級)
- **播放統計**: ✅ 記錄每首音樂的播放次數和總聆聽時間
- **音頻載入**: ✅ 自動載入音頻檔案，支援多種格式
- **錯誤處理**: ✅ 完整的錯誤處理和用戶提示

#### 5. 數據記錄規格 (已實現)

**實際用戶選擇數據** - `frontend/src/types/api.ts`
```typescript
interface ABTestChoice {
  pair_id: string;                    // 配對唯一識別碼
  chosen_track: 'A' | 'B';           // 用戶選擇結果
  decision_time_ms: number;          // 決策時間 (毫秒)
  play_count_a: number;              // 音樂 A 播放次數
  play_count_b: number;              // 音樂 B 播放次數
  total_listen_time_a: number;       // 音樂 A 總聆聽時間
  total_listen_time_b: number;       // 音樂 B 總聆聽時間
}
```

**實際音樂配對數據**
```typescript
interface ABTestPair {
  id: string;                        // 配對唯一識別碼
  track_a: MusicTrack;              // 音樂 A (推薦或隨機)
  track_b: MusicTrack;              // 音樂 B (推薦或隨機)
  recommended_track: 'A' | 'B';     // 哪一個是推薦音樂
  similarity_score?: number;         // 推薦音樂的相似度分數
}
```

**實際儲存位置**: `backend/data/experiments/` 目錄
**檔案格式**: JSON 格式，包含完整實驗會話數據
**數據完整性**: 包含用戶表單、推薦結果、配對資訊、選擇記錄

### 實驗評估指標 (已實現)

#### 實際評估指標實現

```mermaid
graph TD
    subgraph "推薦系統效果指標 (已實現)"
        A[推薦選擇率<br/>實際計算用戶選擇推薦音樂比例]
        B[決策時間分析<br/>毫秒級精確記錄]
        C[聆聽行為分析<br/>播放次數、聆聽時間]
    end

    subgraph "用戶體驗指標 (已實現)"
        D[平均決策時間<br/>每輪測試決策時間]
        E[重複播放頻率<br/>音樂重播次數統計]
        F[完整聆聽率<br/>音樂播放完整度]
    end

    subgraph "系統性能指標 (已實現)"
        G[推薦生成時間<br/>LangGraph + MusicGen 處理時間]
        H[向量搜尋效率<br/>CLAP 編碼 + 相似度計算]
        I[界面響應速度<br/>Web Audio API 載入時間]
    end
```

**實際計算實現** - `src/api/experiment.py`
- **推薦選擇率**: 統計 `chosen_track` 為推薦音樂的比例
- **決策時間分析**: 分析 `decision_time_ms` 分布
- **聆聽行為**: 分析 `play_count` 和 `total_listen_time` 模式

#### 實際統計分析支援

**API 端點**: `/api/experiment/analyze`
**支援功能**:
- 實驗會話統計分析
- 用戶行為模式分析
- 推薦效果評估報告
- 數據匯出功能

**假設檢驗框架** (可擴展):
- H0: 推薦系統效果與隨機選擇無差異
- H1: 推薦系統顯著優於隨機選擇
- 數據基礎: 實際用戶選擇記錄

**實驗數據完整性**:
- ✅ 用戶表單數據
- ✅ 推薦生成過程
- ✅ A/B 測試配對
- ✅ 用戶選擇行為
- ✅ 時間戳記錄

## 實際數據流設計

### 已實現的數據管線

```mermaid
flowchart LR
    subgraph "數據輸入 (已實現)"
        A[用戶表單<br/>React 多步驟表單]
        B[音頻檔案<br/>dataset/ 目錄]
        C[實驗選擇<br/>ABTestInterface]
    end

    subgraph "數據處理 (已實現)"
        D[表單數據驗證<br/>TypeScript 類型檢查]
        E[CLAP 音頻編碼<br/>512維向量]
        F[選擇數據記錄<br/>JSON 格式]
    end

    subgraph "檔案存儲 (已實現)"
        G[實驗會話檔案<br/>data/experiments/]
        H[向量嵌入檔案<br/>data/embeddings.pkl]
        I[生成音頻檔案<br/>generated_audio/]
    end

    subgraph "數據分析 (API 支援)"
        J[會話統計分析<br/>/api/experiment/analyze]
        K[推薦效果評估<br/>選擇率計算]
        L[用戶行為分析<br/>聆聽模式]
    end

    A --> D --> G
    B --> E --> H
    C --> F --> G

    G --> J
    H --> J
    I --> J

    J --> K --> L
```

### 實際數據結構實現

**實驗會話數據** - `ABTestSession`
```typescript
{
  session_id: string;              // UUID 會話識別碼
  user_id: string;                 // 用戶識別碼 (基於 email)
  form_data: FormData;             // 完整表單數據
  test_pairs: ABTestPair[];        // 5 組 A/B 測試配對
  start_time: string;              // ISO 時間戳
  recommendation_metadata: {       // 推薦生成元數據
    recommendations_count: number;
    generation_time_ms: number;
  }
}
```

**用戶選擇數據** - `ABTestResult`
```typescript
{
  session_id: string;              // 關聯會話
  choices: ABTestChoice[];         // 5 次選擇記錄
  completion_time: string;         // 完成時間
  total_duration_ms: number;       // 總實驗時長
}
```

**檔案存儲位置**:
- 實驗數據: `backend/data/experiments/session_{uuid}.json`
- 向量數據: `backend/data/embeddings.pkl`
- 音頻檔案: `backend/dataset/` (原始) + `backend/generated_audio/` (生成)

## 實際系統開發架構

### 已實現的技術棧

**後端架構** (已實現)
- **框架**: ✅ Flask + Flask-RESTful + CORS 支援
- **AI 模型**: ✅ Transformers Library
    - `facebook/musicgen-small` (實際使用，非 large)
    - `laion/clap-htsat-unfused`
    - OpenAI GPT-4o-mini 或 Google Gemini-2.0-flash
- **工作流程**: ✅ LangGraph (5 個專業代理)
- **數據存儲**: ✅ 本地檔案系統 (JSON + Pickle)
- **API 文檔**: ✅ Swagger/OpenAPI 自動生成

**前端架構** (已實現)
- **框架**: ✅ React 19 + TypeScript
- **建置工具**: ✅ Vite 7 (非 SWC，使用預設)
- **音頻播放**: ✅ Web Audio API (完整實現)
- **UI 組件**: ✅ Ant Design 5
- **路由**: ✅ React Router DOM 7
- **HTTP 客戶端**: ✅ Axios

**開發工具** (已實現)
- **版本控制**: ✅ Git
- **依賴管理**: ✅ uv (Python) / npm (JavaScript)
- **測試框架**: ✅ pytest (後端) / 前端測試待實現
- **代碼品質**: ✅ ESLint + TypeScript 嚴格模式

### 實際模組化實現

```mermaid
graph TB
    subgraph "前端模組 (已實現)"
        FM1[多步驟表單組件<br/>SleepRecommendationForm]
        FM2[A/B測試界面<br/>ABTestInterface]
        FM3[音樂播放器<br/>AudioService]
        FM4[推薦結果展示<br/>RecommendationResults]
    end

    subgraph "API 層 (已實現)"
        API1[推薦 API<br/>/api/recommendations]
        API2[實驗 API<br/>/api/experiment]
        API3[音樂 API<br/>/api/music]
        API4[管線 API<br/>/api/pipeline]
    end

    subgraph "業務邏輯層 (已實現)"
        BL1[LangGraph 工作流程<br/>RecommendationPipeline]
        BL2[推薦引擎<br/>RecommendationService]
        BL3[實驗控制器<br/>ExperimentService]
        BL4[音樂生成服務<br/>MusicGenerationService]
    end

    subgraph "AI 模型層 (已實現)"
        ML1[MusicGen 服務<br/>facebook/musicgen-small]
        ML2[CLAP 編碼服務<br/>laion/clap-htsat-unfused]
        ML3[向量搜尋服務<br/>cosine_similarity]
        ML4[LLM 服務<br/>OpenAI/Gemini]
    end

    subgraph "檔案存取層 (已實現)"
        DL1[實驗數據檔案<br/>data/experiments/]
        DL2[音樂數據檔案<br/>dataset/]
        DL3[向量數據檔案<br/>data/embeddings.pkl]
        DL4[生成音頻檔案<br/>generated_audio/]
    end

    FM1 --> API1
    FM2 --> API2
    FM3 --> API3
    FM4 --> API1

    API1 --> BL2
    API2 --> BL3
    API3 --> DL2
    API4 --> BL1

    BL1 --> ML4
    BL2 --> ML1
    BL2 --> ML2
    BL2 --> ML3
    BL3 --> DL1

    ML1 --> DL4
    ML2 --> DL3
    ML3 --> DL3
```

### 實際檔案結構

**後端結構** (`backend/src/`)
```
src/
├── api/              # Flask API 端點 (已實現)
├── nodes/            # LangGraph 代理節點 (已實現)
├── pipeline/         # LangGraph 管線 (已實現)
├── service/          # 業務邏輯服務 (已實現)
├── state/            # 狀態管理 (已實現)
└── utils/            # 工具函數 (已實現)
```

**前端結構** (`frontend/src/`)
```
src/
├── components/       # React 組件 (已實現)
├── pages/           # 頁面組件 (已實現)
├── services/        # API 和音頻服務 (已實現)
├── types/           # TypeScript 類型定義 (已實現)
└── utils/           # 工具函數 (已實現)
```
