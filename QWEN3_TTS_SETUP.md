# Qwen3-TTS 整合設置指南

## 概述

本指南將幫助你將 Qwen3-TTS 整合到聽能復健系統中。系統現在支援兩種 TTS 引擎：
- **Gemini TTS**: 基於 Google 的雲端 TTS 服務
- **Qwen3-TTS**: 阿里巴巴開源的本地 TTS 模型

## 系統架構

```
hearing-rehab-app/
├── app.py                 # 主 Flask 應用程式
├── tts_service.py         # TTS 服務整合模組
├── templates/
│   ├── index.html         # 主頁面（已添加 TTS 管理連結）
│   └── tts_admin.html     # TTS 管理介面
└── data/
    └── audio/             # 生成的音檔存放目錄
```

## 安裝步驟

### 1. 安裝 Qwen3-TTS 依賴

```bash
# 安裝 PyTorch (根據你的 CUDA 版本選擇)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# 安裝 Qwen3-TTS
cd Qwen3-TTS
pip install -e .

# 安裝其他必要依賴
pip install soundfile librosa
```

### 2. 下載 Qwen3-TTS 模型

你可以選擇以下模型之一：

#### Base 模型 (需要參考音檔進行 voice clone)
```bash
# 使用 Hugging Face Hub
pip install huggingface_hub
python -c "from huggingface_hub import snapshot_download; snapshot_download('Qwen/Qwen3-TTS-12Hz-1.7B-Base', local_dir='./models/qwen3-tts-base')"
```

#### Custom Voice 模型 (內建多種說話者)
```bash
python -c "from huggingface_hub import snapshot_download; snapshot_download('Qwen/Qwen3-TTS-12Hz-1.7B-CustomVoice', local_dir='./models/qwen3-tts-custom')"
```

### 3. 配置 TTS 服務

編輯 `hearing-rehab-app/tts_service.py` 中的模型路徑：

```python
# 如果使用本地模型
class Qwen3TTSEngine(TTSEngine):
    def __init__(self, model_path: str = "./models/qwen3-tts-base"):  # 修改為你的模型路徑
        # ...
```

### 4. 環境變數設置

確保你的 `.env` 檔案包含：

```env
# Gemini API Key (如果使用 Gemini TTS)
GEMINI_API_KEY=your_gemini_api_key_here

# 可選：設置 CUDA 設備
CUDA_VISIBLE_DEVICES=0
```

## 使用方法

### 1. 啟動應用程式

```bash
cd hearing-rehab-app
python app.py
```

### 2. 訪問 TTS 管理介面

打開瀏覽器訪問：`http://localhost:5001/tts_admin`

### 3. 功能說明

#### 單個字詞生成
- 輸入要合成的字詞
- 選擇列表類型 (A1, A2, A3, B1, B2, B3)
- 選擇 TTS 引擎
- 點擊「生成語音」

#### 批次生成
- 在文字框中輸入多個字詞（每行一個）
- 選擇列表類型和引擎
- 點擊「批次生成」

#### 缺失音檔檢查
- 自動檢查 `data/word_lists.json` 中所有字詞的音檔
- 自動生成缺失的音檔
- 顯示詳細統計資訊

## 模型選擇建議

### Qwen3-TTS Base 模型
- **優點**: 音質最佳，支援 voice clone
- **缺點**: 需要提供參考音檔和參考文字
- **適用**: 需要特定說話者聲音的場景

### Qwen3-TTS Custom Voice 模型
- **優點**: 內建多種說話者，使用簡單
- **缺點**: 說話者選擇有限
- **適用**: 快速生成，不需要特定聲音

### Gemini TTS
- **優點**: 雲端服務，無需本地資源，中文效果好
- **缺點**: 需要網路連接，有 API 限制
- **適用**: 快速原型開發，小量生成

## 故障排除

### 1. CUDA 記憶體不足
```python
# 在 tts_service.py 中修改
self.device = "cpu"  # 強制使用 CPU
```

### 2. 模型載入失敗
- 檢查模型路徑是否正確
- 確認模型檔案完整下載
- 檢查 PyTorch 版本相容性

### 3. 音檔生成失敗
- 檢查輸出目錄權限
- 確認磁碟空間充足
- 查看日誌檔案中的錯誤訊息

## API 端點

### TTS 相關端點
- `GET /tts_engines` - 獲取可用的 TTS 引擎
- `POST /generate_audio` - 生成單個字詞語音
- `POST /batch_generate_audio` - 批次生成語音
- `POST /check_missing_audio` - 檢查並生成缺失音檔
- `GET /tts_admin` - TTS 管理介面

### 原有端點
- `GET /` - 主頁面
- `POST /start_session` - 開始復健會話
- `GET /get_question` - 獲取問題
- `POST /submit_answer` - 提交答案
- `GET /get_report` - 獲取報告

## 效能優化建議

1. **使用 GPU**: 如果有 NVIDIA GPU，確保安裝 CUDA 版本的 PyTorch
2. **批次處理**: 使用批次生成功能可以提高效率
3. **模型快取**: 模型載入後會保持在記憶體中，避免重複載入
4. **音檔快取**: 已生成的音檔會被保存，避免重複生成

## 下一步

1. 測試兩種 TTS 引擎的效果
2. 根據需求選擇合適的模型
3. 批次生成所有需要的音檔
4. 在聽能復健系統中測試音檔品質