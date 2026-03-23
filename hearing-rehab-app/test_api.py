#!/usr/bin/env python3
"""
API 測試腳本
"""

import requests
import json
import time

BASE_URL = 'http://localhost:5001'

def test_api():
    """測試 API 端點"""
    print("🧪 開始 API 測試")
    print("=" * 40)
    
    try:
        # 測試主頁面
        print("1. 測試主頁面...")
        response = requests.get(BASE_URL)
        if response.status_code == 200:
            print("   ✅ 主頁面載入成功")
        else:
            print(f"   ❌ 主頁面載入失敗: {response.status_code}")
            return
        
        # 測試開始會話
        print("2. 測試開始會話...")
        response = requests.post(f"{BASE_URL}/start_session")
        if response.status_code == 200:
            print("   ✅ 會話開始成功")
        else:
            print(f"   ❌ 會話開始失敗: {response.status_code}")
            return
        
        # 測試獲取問題
        print("3. 測試獲取問題...")
        response = requests.get(f"{BASE_URL}/get_question")
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'success':
                print("   ✅ 問題獲取成功")
                print(f"   📝 問題 {data.get('question_number')}/{data.get('total_questions')}")
                print(f"   🎵 音檔: {data.get('audio_file')}")
                print(f"   📋 選項: {data.get('options')}")
                
                # 測試提交答案
                print("4. 測試提交答案...")
                answer_data = {
                    'answer': data.get('options')[0],  # 選擇第一個選項
                    'question_id': data.get('question_id', 0)
                }
                response = requests.post(
                    f"{BASE_URL}/submit_answer",
                    json=answer_data,
                    headers={'Content-Type': 'application/json'}
                )
                if response.status_code == 200:
                    result = response.json()
                    if result.get('status') == 'success':
                        print("   ✅ 答案提交成功")
                        print(f"   🎯 結果: {'正確' if result.get('is_correct') else '錯誤'}")
                        print(f"   📝 正確答案: {result.get('correct_answer')}")
                    else:
                        print(f"   ❌ 答案提交失敗: {result}")
                else:
                    print(f"   ❌ 答案提交失敗: {response.status_code}")
            else:
                print(f"   ❌ 問題獲取失敗: {data}")
        else:
            print(f"   ❌ 問題獲取失敗: {response.status_code}")
        
        print("\n🎉 API 測試完成")
        
    except requests.exceptions.ConnectionError:
        print("❌ 無法連接到服務器")
        print("請確保 Flask 應用程式正在運行 (python run.py)")
    except Exception as e:
        print(f"❌ 測試過程中發生錯誤: {e}")

if __name__ == '__main__':
    test_api()