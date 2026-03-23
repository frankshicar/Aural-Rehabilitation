# Bug 修復記錄

## 問題描述
第二題之後「確認答案」按鈕消失，導致無法繼續測試。

## 問題原因
在 `setupQuestion()` 函數中，當載入新問題時：
1. 「確認答案」按鈕被設為 `disabled = true`（正確）
2. 「下一題」按鈕被隱藏（正確）
3. 但是「確認答案」按鈕的 `display` 屬性沒有被重置

當用戶提交答案後，「確認答案」按鈕被設為 `display = 'none'`，但在下一題載入時沒有重新顯示。

## 修復方案
在 `setupQuestion()` 函數中添加一行代碼：

```javascript
// 重置狀態
this.selectedAnswer = null;
document.getElementById('submit-answer').disabled = true;
document.getElementById('submit-answer').style.display = 'inline-block'; // 🔧 新增這行
document.getElementById('next-question').style.display = 'none';
document.getElementById('feedback').style.display = 'none';
```

## 修復後的流程
1. 載入新問題時，「確認答案」按鈕顯示但禁用
2. 用戶選擇答案後，按鈕啟用
3. 提交答案後，按鈕隱藏，「下一題」按鈕顯示
4. 載入下一題時，「確認答案」按鈕重新顯示並禁用

## 測試方法
1. 啟動應用程式：`python run.py`
2. 開啟瀏覽器：`http://localhost:5001`
3. 完成第一題，點擊「下一題」
4. 確認第二題及後續題目都有「確認答案」按鈕

## 相關檔案
- `templates/index.html` - 前端 JavaScript 代碼
- `app.py` - 後端 Flask 應用程式

## 版本資訊
- 修復日期：2026-03-23
- 影響版本：v1.0.0
- 修復版本：v1.0.1