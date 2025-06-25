# Symphony AI 推薦系統設計文件

## 概述

本文件描述了 Symphony AI 睡眠音樂推薦系統的核心架構設計與實驗評估流程。系統採用多代理工作流程，結合大型語言模型、音樂生成技術和向量相似度搜尋，為用戶提供個性化的睡眠音樂推薦。本系統同時設計了嚴謹的 A/B 測試實驗流程，用於驗證推薦系統的有效性。

## 系統目標

### 主要目標
- **個性化推薦**: 基於用戶生理心理狀態提供客製化音樂推薦
- **智能音樂生成**: 利用 AI 技術動態生成符合需求的睡眠音樂
- **科學驗證**: 通過嚴謹的實驗設計驗證推薦系統效果
- **用戶體驗優化**: 提供直觀易用的推薦服務界面

### 技術目標
- **推薦準確性**: 實現高品質的音樂語義匹配
- **系統響應性**: 保持良好的用戶互動體驗
- **實驗可重複性**: 建立標準化的評估流程
- **數據收集完整性**: 全面記錄用戶行為和偏好數據

## 系統架構

### 整體流程圖

```mermaid
flowchart TD
    A[用戶填寫表單] --> B[LangGraph 多代理分析]
    B --> C[生成 MusicGen 提示詞]
    C --> D[MusicGen 音樂合成]
    D --> E[CLAP 音頻編碼]
    E --> F[向量相似度搜尋]
    F --> G[Top 5 推薦結果]
    G --> H[A/B 測試配對]
    H --> I[盲測實驗界面]
    I --> J[記錄用戶偏好選擇]
    
    K[(預編碼音樂庫)] --> F
    L[(隨機音樂庫)] --> H
```

### 系統組件架構

```mermaid
graph TB
    subgraph "用戶界面層"
        UI[表單填寫界面]
        TEST[A/B 測試界面]
        ADMIN[實驗數據管理]
    end
    
    subgraph "業務邏輯層"
        API[API Gateway]
        WORKFLOW[LangGraph 工作流程]
        RECOMMEND[推薦引擎]
        EXPERIMENT[實驗管理引擎]
    end
    
    subgraph "AI 模型層"
        LLM[大型語言模型]
        MUSICGEN[MusicGen 模型]
        CLAP[CLAP 編碼模型]
    end
      subgraph "文件存儲層"
        VECTOR[向量數據文件]
        METADATA[音樂元數據文件]
        AUDIO[音頻檔案庫]
        EXPERIMENT_DATA[實驗數據文件]
        USER_DATA[用戶資料文件]
    end
    
    UI --> API
    TEST --> API
    ADMIN --> API
    API --> WORKFLOW
    API --> EXPERIMENT
    WORKFLOW --> LLM
    WORKFLOW --> RECOMMEND
    RECOMMEND --> MUSICGEN
    RECOMMEND --> CLAP
    RECOMMEND --> VECTOR
    EXPERIMENT --> EXPERIMENT_DATA
    EXPERIMENT --> USER_DATA
    VECTOR --> METADATA
    VECTOR --> AUDIO
```

## 推薦系統核心組件

### 1. LangGraph 多代理工作流程

#### 1.1 代理架構設計

```mermaid
graph LR
    INPUT[表單數據輸入] --> SA[狀態分析代理]
    INPUT --> EA[情緒識別代理]
    INPUT --> PA[偏好分析代理]
    
    SA --> IA[需求整合代理]
    EA --> IA
    PA --> IA
    
    IA --> PG[提示詞生成代理]
    PG --> OUTPUT[MusicGen 提示詞輸出]
```

#### 1.2 代理職責分工

**狀態分析代理 (State Analysis Agent)**
- **輸入數據**: 壓力指數、身體感受、情緒狀態
- **分析功能**: 評估用戶當前生理心理狀態
- **輸出結果**: 狀態摘要和緊急程度評估

**情緒識別代理 (Emotion Recognition Agent)**
- **輸入數據**: 情緒狀態、入睡目標
- **分析功能**: 識別主導情緒和情緒調節需求
- **輸出結果**: 情緒標籤和調節策略

**偏好分析代理 (Preference Analysis Agent)**
- **輸入數據**: 聲音偏好、節奏偏好、敏感度設定
- **分析功能**: 分析用戶音樂偏好和限制條件
- **輸出結果**: 偏好矩陣和禁忌列表

**需求整合代理 (Requirement Integration Agent)**
- **輸入數據**: 各代理的分析結果
- **整合功能**: 統合所有需求，解決衝突
- **輸出結果**: 統一的需求規格

**提示詞生成代理 (Prompt Generation Agent)**
- **輸入數據**: 整合需求規格
- **生成功能**: 產生結構化的 MusicGen 提示詞
- **輸出結果**: 最佳化的音樂生成指令

### 2. MusicGen 音樂合成模組

#### 2.1 提示詞結構設計

**基本結構組件**
- **音樂類型** (Genre): lo-fi, ambient, classical, electronic
- **節奏速度** (Tempo): very slow, slow, moderate, rhythmless
- **情緒氛圍** (Mood): calming, soothing, peaceful, relaxing
- **樂器選擇** (Instruments): piano, guitar, strings, synthesizer
- **音樂特徵** (Characteristics): soft, gentle, melodic, harmonic
- **頻率調諧** (Frequency): 432Hz, standard tuning
- **音樂長度** (Duration): 30-120 seconds

#### 2.2 提示詞生成策略

```mermaid
flowchart TD
    A[用戶需求分析] --> B{入睡目標}
    
    B -->|快速入眠| C[超慢節奏 + 低頻音樂]
    B -->|維持好眠| D[穩定背景音樂]
    B -->|深度放鬆| E[冥想式無節拍]
    B -->|降低焦慮| F[432Hz 調諧音樂]
    B -->|正面情緒| G[輕柔旋律音樂]
    
    C --> H[組合提示詞]
    D --> H
    E --> H
    F --> H
    G --> H
    
    H --> I[MusicGen 提示詞]
```

### 3. CLAP 音頻編碼與向量搜尋

#### 3.1 音頻處理流程

```mermaid
flowchart LR
    A[原始音頻文件] --> B[音頻載入與預處理]
    B --> C[採樣率標準化]
    C --> D[音頻長度調整]
    D --> E[音量正規化]
    E --> F[CLAP 模型編碼]
    F --> G[向量嵌入輸出]
```

#### 3.2 相似度搜尋流程

```mermaid
sequenceDiagram
    participant U as 用戶
    participant WF as LangGraph 工作流程
    participant MG as MusicGen
    participant CLAP as CLAP 編碼器
    participant VS as 向量搜尋引擎
    participant DB as 向量資料庫
    
    U->>WF: 提交表單數據
    WF->>WF: 多代理協作分析
    WF->>MG: 生成參考音樂
    MG->>CLAP: 編碼音頻為向量
    CLAP->>VS: 查詢向量
    VS->>DB: 計算餘弦相似度
    DB->>VS: 返回 Top 5 相似音樂
    VS->>U: 推薦音樂列表
```

### 4. 推薦引擎邏輯

#### 4.1 推薦策略設計

```mermaid
flowchart TD
    A[用戶表單輸入] --> B[多代理分析]
    B --> C[生成參考音樂]
    C --> D[向量編碼]
    D --> E[相似度計算]
    E --> F[Top 5 推薦結果]
```

#### 4.2 排序算法設計

**綜合評分因子**
- **向量相似度**: 主要排序依據
- **用戶偏好匹配**: 聲音類型、節奏偏好符合度
- **音樂品質評估**: 音頻質量和完整性

## A/B 測試實驗設計

### 實驗流程架構

```mermaid
flowchart TD
    A[用戶填寫表單] --> B[收集受測者資料]
    B --> C[系統生成推薦]
    C --> D[獲得 Top 5 推薦音樂]
    D --> E[隨機選取 5 首對照音樂]
    E --> F[A/B 配對組合]
    F --> G[盲測界面呈現]
    G --> H[用戶進行 5 次偏好選擇]
    H --> I[記錄選擇結果]
    I --> J[數據分析與統計]
```

### 實驗設計詳細說明

#### 1. 數據收集階段

**受測者資料收集**
- 基本人口統計學資料
- 睡眠習慣問卷
- 音樂偏好背景
- 參與實驗同意書

**表單數據結構化**
- 生理心理狀態評估
- 音樂偏好設定
- 入睡目標定義
- 敏感度設定記錄

#### 2. 推薦生成階段

```mermaid
graph LR
    A[表單輸入] --> B[LangGraph 分析]
    B --> C[MusicGen 生成]
    C --> D[CLAP 編碼]
    D --> E[向量搜尋]
    E --> F[Top 5 推薦]
    
    G[音樂資料庫] --> H[隨機選取 5 首，排除 Top 5 相似音樂]
    H --> I[對照組音樂]
```

#### 3. A/B 測試配對設計

**配對策略**
- **測試組**: Top 5 推薦音樂
- **對照組**: 5 首隨機音樂（排除與 Top 5 高相似度的音樂）
- **配對方式**: 1對1 隨機配對，共 5 輪測試
- **呈現順序**: 隨機化 A/B 位置避免位置偏誤

#### 4. 盲測實驗界面

```mermaid
stateDiagram-v2
    [*] --> 實驗說明
    實驗說明 --> 第一輪測試
    第一輪測試 --> 第二輪測試
    第二輪測試 --> 第三輪測試
    第三輪測試 --> 第四輪測試
    第四輪測試 --> 第五輪測試
    第五輪測試 --> 結果提交
    結果提交 --> [*]
    
    第一輪測試 --> 第一輪測試: 重新聆聽
    第二輪測試 --> 第二輪測試: 重新聆聽
    第三輪測試 --> 第三輪測試: 重新聆聽
    第四輪測試 --> 第四輪測試: 重新聆聽
    第五輪測試 --> 第五輪測試: 重新聆聽
```

**界面設計要求**
- **盲測保證**: 不顯示音樂來源和類型資訊
- **播放控制**: 支援重複播放和暫停功能
- **選擇記錄**: 清楚標示 A/B 選項
- **進度顯示**: 明確顯示測試進度（1/5, 2/5...）
- **時間記錄**: 記錄每輪選擇的思考時間

#### 5. 數據記錄規格

**用戶選擇數據**
- 每輪測試的選擇結果（A 或 B）
- 選擇決策時間
- 音樂播放時長
- 重複播放次數

**音樂配對數據**
- 推薦音樂與對照音樂的配對關係
- 音樂的向量相似度分數
- 音樂的元數據資訊
- A/B 位置隨機化記錄

### 實驗評估指標

#### 主要評估指標

```mermaid
graph TD
    subgraph "推薦系統效果指標"
        A[推薦選擇率]
        B[一致性指標]
        C[決策信心度]
    end
    
    subgraph "用戶體驗指標"
        D[平均決策時間]
        E[重複播放頻率]
        F[完整聆聽率]
    end
    
    subgraph "系統性能指標"
        G[推薦生成時間]
        H[向量搜尋效率]
        I[界面響應速度]
    end
```

**計算方式**
- **推薦選擇率**: 用戶選擇推薦音樂的比例 (0-100%)
- **一致性指標**: 同類型用戶偏好的一致性程度
- **決策信心度**: 基於決策時間和重複播放行為的信心評估

#### 統計分析方法

**假設檢驗**
- H0: 推薦系統效果與隨機選擇無差異
- H1: 推薦系統顯著優於隨機選擇
- 統計檢驗: 卡方檢驗、t 檢驗

**效果量評估**
- Cohen's d: 評估推薦效果的實際意義
- 95% 信賴區間: 估計真實效果範圍

## 數據流設計

### 實驗數據管線

```mermaid
flowchart LR
    subgraph "數據輸入"
        A[用戶表單]
        B[音頻檔案]
        C[實驗選擇]
    end
    
    subgraph "數據處理"
        D[表單數據結構化]
        E[音頻特徵提取]
        F[選擇數據標準化]
    end
      subgraph "文件存儲"
        G[用戶資料文件]
        H[音樂向量文件]
        I[實驗結果文件]
    end
    
    subgraph "數據分析"
        J[描述性統計]
        K[推論統計]
        L[效果評估]
    end
    
    A --> D --> G
    B --> E --> H
    C --> F --> I
    
    G --> J
    H --> J
    I --> J
    
    J --> K --> L
```

### 實驗數據結構

**用戶檔案數據**
- 用戶唯一識別碼
- 人口統計學資料
- 音樂背景調查
- 睡眠習慣資訊

**實驗會話數據**
- 會話唯一識別碼
- 表單填寫時間戳
- 推薦生成結果
- A/B 測試配對記錄

**偏好選擇數據**
- 每輪測試結果
- 決策時間記錄
- 音樂播放行為
- 用戶反饋意見

## 系統開發架構

### 技術棧選擇

**後端架構**
- **框架**: Flask + Flask-RESTful
- **AI 模型**: Transformers Library (MusicGen, CLAP)
    - `facebook/musicgen-large`
    - `laion/clap-htsat-unfused`
- **工作流程**: LangGraph
- **數據存儲**: 本地檔案系統（JSON 文件暫存）
- **檔案存儲**: 本地檔案系統

**前端架構**
- **框架**: React + TypeScript
- **建置工具**: Vite + SWC
- **音頻播放**: Web Audio API
- **UI 組件**: Ant Design
- **狀態管理**: React Context / Redux (可選)

**開發工具**
- **版本控制**: Git
- **容器化**: Docker
- **依賴管理**: uv (Python) / npm (JavaScript)
- **測試框架**: pytest / Jest

### 模組化設計

```mermaid
graph TB
    subgraph "前端模組"
        FM1[表單組件]
        FM2[A/B測試界面]
        FM3[數據視覺化]
        FM4[管理後台]
    end
    
    subgraph "API 層"
        API1[用戶管理 API]
        API2[推薦服務 API]
        API3[實驗管理 API]
        API4[數據分析 API]
    end
    
    subgraph "業務邏輯層"
        BL1[LangGraph 工作流程]
        BL2[推薦引擎]
        BL3[實驗控制器]
        BL4[數據分析器]
    end
    
    subgraph "AI 模型層"
        ML1[MusicGen 服務]
        ML2[CLAP 編碼服務]
        ML3[向量搜尋服務]
    end
      subgraph "文件存取層"
        DL1[用戶數據文件]
        DL2[音樂數據文件]
        DL3[實驗數據文件]
        DL4[向量數據文件]
    end
    
    FM1 --> API1
    FM2 --> API2
    FM3 --> API4
    FM4 --> API3
    
    API1 --> BL2
    API2 --> BL1
    API3 --> BL3
    API4 --> BL4
    
    BL1 --> ML1
    BL1 --> ML2
    BL2 --> ML3
    
    BL2 --> DL1
    BL2 --> DL2
    BL3 --> DL3
    BL4 --> DL4
```
