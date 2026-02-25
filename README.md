# Gemini TTS 互動式文字轉語音工具

使用 Google Gemini API 將手動輸入的文字轉為語音音訊檔案。

## 環境需求

- Python 3.8+
- Google Gemini API Key

## 安裝步驟

### 1. 安裝 Python 套件

```bash
cd gemini_tts
pip install -r requirements.txt
```

### 2. 設定 API Key

複製 `.env.example` 為 `.env`，並填入你的 Gemini API Key：

```bash
cp .env.example .env
```

編輯 `.env` 檔案：

```
GEMINI_API_KEY=你的_API_KEY
```

> [!TIP]
> API Key 可在 [Google AI Studio](https://aistudio.google.com/apikey) 取得。

## 執行方式

```bash
cd gemini_tts
python tts_gemini.py
```

啟動後會進入互動模式，直接輸入文字即可產生語音。

## 使用方式

```
==================================================
  Gemini TTS 互動模式
==================================================
✅ Gemini 客戶端初始化成功！

目前使用的聲音: Aoede
輸入 'voice' 可更換聲音
輸入 'quit' 或 'exit' 可離開程式
--------------------------------------------------

請輸入要朗讀的文字: 你好，這是一段測試語音
正在使用 'Aoede' 的聲音生成音訊...
✅ 成功！音訊已儲存至 output_001.wav

請輸入要朗讀的文字: voice

可選擇的聲音:
  1. Puck
  2. Charon
  3. Kore
  4. Fenrir
  5. Aoede
  0. 保持目前設定
請輸入數字選擇聲音: 1
  已切換聲音為: Puck

請輸入要朗讀的文字: quit
👋 再見！
```

## 指令說明

| 指令 | 說明 |
|------|------|
| 輸入任意文字 | 使用目前聲音生成語音，儲存為 `output_001.wav`、`output_002.wav`… |
| `voice` | 切換聲音角色 |
| `quit` / `exit` / `q` | 離開程式 |

## 可用聲音

| 編號 | 名稱 |
|------|------|
| 1 | Puck |
| 2 | Charon |
| 3 | Kore |
| 4 | Fenrir |
| 5 | Aoede |

## 輸出檔案

生成的音訊檔會以遞增編號命名存放在 `gemini_tts/` 目錄下：

```
output_001.wav
output_002.wav
output_003.wav
...
```
