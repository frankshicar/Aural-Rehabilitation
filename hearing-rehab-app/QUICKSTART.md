# 快速啟動指南

## 🚀 5 分鐘快速開始

### 1. 進入專案目錄
```bash
cd hearing-rehab-app
```

### 2. 安裝依賴
```bash
pip install -r requirements.txt
```

### 3. 設定 API 金鑰
```bash
# 複製範例環境檔案
cp .env.example .env

# 編輯 .env 檔案，加入您的 Gemini API 金鑰
# GEMINI_API_KEY=your_api_key_here
```

### 4. 啟動應用程式
```bash
python run.py
```

### 5. 開啟瀏覽器
訪問 `http://localhost:5001`

## 📁 專案結構

```
hearing-rehab-app/
├── app.py              # Flask 主應用程式
├── run.py              # 啟動腳本 (使用這個啟動)
├── wsgi.py             # 生產環境入口點
├── test_api.py         # API 測試腳本
├── requirements.txt    # Python 依賴
├── .env               # 環境變數 (需要設定)
├── .env.example       # 環境變數範例
├── templates/
│   └── index.html     # 網頁介面
├── static/            # 靜態檔案 (CSS, JS, 圖片)
└── data/
    ├── word_lists.json # 詞彙列表
    └── audio/          # 音檔目錄
        ├── A1/         # A1 級別音檔
        ├── A2/         # A2 級別音檔
        └── B1/         # B1 級別音檔
```

## 🧪 測試系統

```bash
# 測試 API 端點
python test_api.py
```

## 🔧 常見問題

### Q: 無法啟動應用程式
A: 檢查是否已安裝所有依賴：`pip install -r requirements.txt`

### Q: API 錯誤
A: 確認 `.env` 檔案中的 `GEMINI_API_KEY` 是否正確設定

### Q: 音檔無法播放
A: 確認 `data/audio/` 目錄中有音檔，且格式為 WAV

### Q: 頁面無法載入
A: 確認 Flask 服務正在運行，檢查控制台是否有錯誤訊息

## 📞 需要幫助？

1. 查看詳細文檔：`README.md`
2. 檢查系統日誌：啟動時會顯示詳細資訊
3. 測試 API：使用 `test_api.py` 檢查功能

## 🎯 使用流程

1. 患者點擊「開始測試」
2. 系統隨機播放音檔
3. 患者從 4 個選項中選擇答案
4. 完成 20 題測試
5. 獲得 AI 生成的個人化復健報告