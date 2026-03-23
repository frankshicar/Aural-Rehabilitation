#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TTS 整合測試腳本
用於驗證 Gemini TTS 和 Qwen3-TTS 的整合是否正常工作
"""

import os
import sys
import json
import logging
from pathlib import Path

# 添加 hearing-rehab-app 到路徑
sys.path.append('hearing-rehab-app')

# 添加 qwen3-tts 到路徑
qwen3_path = os.path.join(os.path.dirname(__file__), 'qwen3-tts')
if os.path.exists(qwen3_path):
    sys.path.insert(0, qwen3_path)
    print(f"✅ 找到 Qwen3-TTS 路徑: {qwen3_path}")
else:
    print(f"⚠️  Qwen3-TTS 路徑不存在: {qwen3_path}")

try:
    from tts_service import tts_service, GeminiTTSEngine, Qwen3TTSEngine
    print("✅ TTS 服務模組載入成功")
except ImportError as e:
    print(f"❌ TTS 服務模組載入失敗: {e}")
    sys.exit(1)

# 設定日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_engines():
    """測試 TTS 引擎可用性"""
    print("\n" + "="*50)
    print("測試 TTS 引擎可用性")
    print("="*50)
    
    available_engines = tts_service.get_available_engines()
    print(f"可用引擎: {available_engines}")
    print(f"預設引擎: {tts_service.preferred_engine}")
    
    if not available_engines:
        print("❌ 沒有可用的 TTS 引擎")
        return False
    
    # 測試每個引擎
    for engine_name in available_engines:
        engine = tts_service.engines[engine_name]
        status = "✅ 可用" if engine.is_available() else "❌ 不可用"
        print(f"{engine_name.upper()} TTS: {status}")
    
    return True

def test_single_synthesis():
    """測試單個字詞合成"""
    print("\n" + "="*50)
    print("測試單個字詞語音合成")
    print("="*50)
    
    test_word = "測試"
    test_list = "A1"
    
    print(f"測試字詞: {test_word}")
    print(f"列表: {test_list}")
    
    # 確保輸出目錄存在
    output_dir = f"hearing-rehab-app/data/audio/{test_list}"
    os.makedirs(output_dir, exist_ok=True)
    
    success = False
    for engine_name in tts_service.get_available_engines():
        print(f"\n使用 {engine_name.upper()} 引擎:")
        
        try:
            audio_path = tts_service.synthesize_word(test_word, test_list, engine_name)
            if audio_path and os.path.exists(audio_path):
                file_size = os.path.getsize(audio_path)
                print(f"✅ 合成成功: {audio_path} ({file_size} bytes)")
                success = True
            else:
                print(f"❌ 合成失敗")
        except Exception as e:
            print(f"❌ 合成時發生錯誤: {e}")
    
    return success

def test_batch_synthesis():
    """測試批次合成"""
    print("\n" + "="*50)
    print("測試批次語音合成")
    print("="*50)
    
    test_words = ["你", "好", "世", "界"]
    test_list = "A2"
    
    print(f"測試字詞: {test_words}")
    print(f"列表: {test_list}")
    
    # 確保輸出目錄存在
    output_dir = f"hearing-rehab-app/data/audio/{test_list}"
    os.makedirs(output_dir, exist_ok=True)
    
    success = False
    for engine_name in tts_service.get_available_engines():
        print(f"\n使用 {engine_name.upper()} 引擎:")
        
        try:
            successful_paths = tts_service.batch_synthesize_list(test_words, test_list, engine_name)
            success_rate = len(successful_paths) / len(test_words) * 100
            print(f"✅ 批次合成完成: {len(successful_paths)}/{len(test_words)} ({success_rate:.1f}%)")
            
            for path in successful_paths:
                if os.path.exists(path):
                    file_size = os.path.getsize(path)
                    print(f"  - {os.path.basename(path)}: {file_size} bytes")
            
            if successful_paths:
                success = True
                
        except Exception as e:
            print(f"❌ 批次合成時發生錯誤: {e}")
    
    return success

def test_missing_audio_check():
    """測試缺失音檔檢查功能"""
    print("\n" + "="*50)
    print("測試缺失音檔檢查功能")
    print("="*50)
    
    # 載入字詞列表
    word_lists_path = "hearing-rehab-app/data/word_lists.json"
    if not os.path.exists(word_lists_path):
        print(f"❌ 字詞列表檔案不存在: {word_lists_path}")
        return False
    
    try:
        with open(word_lists_path, 'r', encoding='utf-8') as f:
            word_lists = json.load(f)
        
        print(f"載入字詞列表: {list(word_lists.keys())}")
        
        # 只檢查一個小列表避免生成太多檔案
        test_list = {"list_A1": word_lists.get("list_A1", [])[:3]}  # 只取前3個字詞
        
        stats = tts_service.synthesize_missing_audio(test_list)
        
        print(f"檢查結果:")
        print(f"  總檢查數: {stats['total_checked']}")
        print(f"  缺失音檔: {stats['missing_found']}")
        print(f"  成功生成: {stats['successfully_generated']}")
        print(f"  生成失敗: {stats['failed_generation']}")
        
        return stats['total_checked'] > 0
        
    except Exception as e:
        print(f"❌ 檢查缺失音檔時發生錯誤: {e}")
        return False

def test_flask_integration():
    """測試 Flask 整合"""
    print("\n" + "="*50)
    print("測試 Flask 應用程式整合")
    print("="*50)
    
    try:
        # 嘗試導入 Flask 應用程式
        sys.path.append('hearing-rehab-app')
        
        # 暫時改變工作目錄到 hearing-rehab-app
        original_cwd = os.getcwd()
        os.chdir('hearing-rehab-app')
        
        try:
            from app import app
            print("✅ Flask 應用程式載入成功")
            
            # 檢查路由
            routes = []
            for rule in app.url_map.iter_rules():
                routes.append(f"{rule.methods} {rule.rule}")
            
            tts_routes = [route for route in routes if 'tts' in route.lower()]
            print(f"TTS 相關路由: {len(tts_routes)}")
            for route in tts_routes:
                print(f"  - {route}")
            
            return True
        finally:
            # 恢復原始工作目錄
            os.chdir(original_cwd)
        
    except Exception as e:
        print(f"❌ Flask 整合測試失敗: {e}")
        return False

def main():
    """主測試函數"""
    print("Qwen3-TTS 整合測試")
    print("="*50)
    
    tests = [
        ("TTS 引擎可用性", test_engines),
        ("單個字詞合成", test_single_synthesis),
        ("批次合成", test_batch_synthesis),
        ("缺失音檔檢查", test_missing_audio_check),
        ("Flask 整合", test_flask_integration),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} 測試時發生未預期錯誤: {e}")
            results.append((test_name, False))
    
    # 顯示測試結果摘要
    print("\n" + "="*50)
    print("測試結果摘要")
    print("="*50)
    
    passed = 0
    for test_name, result in results:
        status = "✅ 通過" if result else "❌ 失敗"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n總計: {passed}/{len(results)} 項測試通過")
    
    if passed == len(results):
        print("🎉 所有測試通過！TTS 整合成功！")
        print("\n下一步:")
        print("1. 啟動 Flask 應用程式: cd hearing-rehab-app && python app.py")
        print("2. 訪問 TTS 管理介面: http://localhost:5001/tts_admin")
        print("3. 生成所需的音檔")
    else:
        print("⚠️  部分測試失敗，請檢查配置")
        print("參考 QWEN3_TTS_SETUP.md 進行故障排除")

if __name__ == "__main__":
    main()