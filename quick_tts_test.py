#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速 TTS 測試腳本
"""

import sys
import os
sys.path.append('hearing-rehab-app')

from tts_service import tts_service

def test_both_engines():
    """測試兩個 TTS 引擎"""
    test_word = "你好"
    
    print("快速 TTS 測試")
    print("="*30)
    
    # 測試 Gemini TTS
    print("\n測試 Gemini TTS:")
    gemini_path = tts_service.synthesize_word(test_word, "test", "gemini")
    if gemini_path and os.path.exists(gemini_path):
        size = os.path.getsize(gemini_path)
        print(f"✅ Gemini TTS 成功: {gemini_path} ({size} bytes)")
    else:
        print("❌ Gemini TTS 失敗")
    
    # 測試 Qwen3-TTS
    print("\n測試 Qwen3-TTS:")
    qwen_path = tts_service.synthesize_word(test_word, "test", "qwen3")
    if qwen_path and os.path.exists(qwen_path):
        size = os.path.getsize(qwen_path)
        print(f"✅ Qwen3-TTS 成功: {qwen_path} ({size} bytes)")
    else:
        print("❌ Qwen3-TTS 失敗")
    
    print(f"\n可用引擎: {tts_service.get_available_engines()}")
    print(f"預設引擎: {tts_service.preferred_engine}")

if __name__ == "__main__":
    test_both_engines()