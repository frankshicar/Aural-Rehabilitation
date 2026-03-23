#!/usr/bin/env python3
"""
聽能復健系統啟動腳本
"""

import os
import sys

def check_requirements():
    """檢查必要的檔案和目錄"""
    required_files = [
        '.env',
        'data/word_lists.json',
        'templates/index.html'
    ]
    
    required_dirs = [
        'data/audio',
        'templates'
    ]
    
    missing_files = []
    missing_dirs = []
    
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    for dir_path in required_dirs:
        if not os.path.exists(dir_path):
            missing_dirs.append(dir_path)
    
    if missing_files or missing_dirs:
        print("❌ 缺少必要的檔案或目錄:")
        for file_path in missing_files:
            print(f"   - 檔案: {file_path}")
        for dir_path in missing_dirs:
            print(f"   - 目錄: {dir_path}")
        return False
    
    return True

def check_audio_files():
    """檢查音檔是否存在"""
    audio_dirs = ['data/audio/A1', 'data/audio/A2', 'data/audio/B1']
    total_files = 0
    
    for audio_dir in audio_dirs:
        if os.path.exists(audio_dir):
            files = [f for f in os.listdir(audio_dir) if f.endswith('.wav')]
            total_files += len(files)
            print(f"📁 {audio_dir}: {len(files)} 個音檔")
    
    print(f"🎵 總共找到 {total_files} 個音檔")
    return total_files > 0

def main():
    print("🎧 聽能復健系統啟動檢查")
    print("=" * 40)
    
    # 檢查必要檔案
    if not check_requirements():
        print("\n❌ 系統檢查失敗，請確保所有必要檔案都存在")
        sys.exit(1)
    
    # 檢查音檔
    if not check_audio_files():
        print("\n⚠️  警告: 沒有找到音檔，請確保 data/audio/ 目錄中有音檔")
    
    print("\n✅ 系統檢查完成")
    print("\n🚀 啟動 Flask 應用程式...")
    print("📱 請在瀏覽器中開啟: http://localhost:5001")
    print("⏹️  按 Ctrl+C 停止服務")
    print("=" * 40)
    
    # 啟動 Flask 應用程式
    from app import app
    app.run(debug=True, host='0.0.0.0', port=5001)

if __name__ == '__main__':
    main()