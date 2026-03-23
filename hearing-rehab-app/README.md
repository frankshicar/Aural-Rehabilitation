# 聽能復健系統

一個基於 Flask 和 Gemini AI 的聽能復健訓練平台，提供音檔播放、選擇題測試和個人化復健報告。

## 功能特色

- 🎵 **音檔播放**: 隨機播放 data/audio 資料夾中的音檔
- 📝 **選擇題測試**: 每題提供 4 個選項供患者選擇
- 📊 **進度追蹤**: 即時顯示測試進度和統計
- 🤖 **AI 報告**: 使用 Gemini API 生成個人化復健建議
- 📱 **響應式設計**: 支援桌面和行動裝置
- 🎨 **友善介面**: 直觀易用的使用者介面

## 專案結構

```
hearing-rehab-app/
├── app.py                 # Flask 主應用程式
├── wsgi.py               # WSGI 入口點
├── run.py                # 啟動腳本
├── test_api.py           # API 測試腳本
├── requirements.txt      # Python 依賴
├── .env                  # 環境變數
├── templates/
│   └── index.html       # 前端介面
├── static/              # 靜態檔案 (CSS, JS, 圖片)
└── data/
    ├── word_lists.json  # 詞彙列表
    └── audio/           # 音檔目錄
        ├── A1/
        ├── A2/
        └── B1/
```

## 系統需求

- Python 3.7+
- Flask 2.3+
- Google Generative AI API 金鑰

## 安裝步驟

1. **進入專案目錄**
   ```bash
   cd hearing-rehab-app
   ```

2. **安裝依賴**
   ```bash
   pip install -r requirements.txt
   ```

3. **設定 API 金鑰**
   
   編輯 `.env` 檔案，確保包含您的 Gemini API 金鑰：
   ```
   GEMINI_API_KEY=your_api_key_here
   ```

4. **檢查音檔**
   
   確保 `data/audio/` 目錄結構如下：
   ```
   data/audio/
   ├── A1/
   │   ├── A1_知.wav
   │   ├── A1_上.wav
   │   └── ...
   ├── A2/
   │   ├── A2_地.wav
   │   └── ...
   └── B1/
       ├── B1_經.wav
       └── ...
   ```

## 使用方法

1. **啟動系統**
   ```bash
   python run.py
   ```

2. **開啟瀏覽器**
   
   訪問 `http://localhost:5001`

3. **開始測試**
   - 點擊「開始測試」按鈕
   - 聽取音檔並從 4 個選項中選擇答案
   - 完成 20 題測試
   - 查看個人化復健報告

## API 端點

- `GET /` - 主頁面
- `POST /start_session` - 開始新的測試會話
- `GET /get_question` - 獲取下一個問題
- `POST /submit_answer` - 提交答案
- `GET /get_report` - 獲取復健報告
- `GET /audio/<filename>` - 提供音檔服務

## 開發和測試

### 測試 API
```bash
python test_api.py
```

### 生產環境部署
```bash
# 使用 Gunicorn
pip install gunicorn
gunicorn --bind 0.0.0.0:5001 --workers 4 wsgi:app
```

## 自訂設定

### 修改測試題數
在 `app.py` 中修改 `AudioRehabSession` 類別：
```python
self.total_questions = 30  # 改為 30 題
```

### 新增詞彙列表
在 `data/word_lists.json` 中新增：
```json
{
  "list_C1": ["新詞1", "新詞2", "新詞3", ...]
}
```

## 故障排除

### 常見問題

1. **音檔無法播放**
   - 檢查 `data/audio/` 目錄中的音檔
   - 確認音檔格式為 WAV
   - 檢查檔案權限

2. **API 錯誤**
   - 驗證 `.env` 檔案中的 Gemini API 金鑰
   - 檢查網路連線
   - 查看 API 使用配額

3. **頁面無法載入**
   - 確認 Flask 服務正在運行
   - 檢查防火牆設定
   - 查看控制台錯誤訊息

## 授權

本專案採用 MIT 授權條款。