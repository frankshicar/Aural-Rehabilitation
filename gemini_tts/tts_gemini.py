import os
import json
import random
import time
import wave
from dotenv import load_dotenv
from google import genai
from google.genai import types

# 載入 .env 檔案中的環境變數
load_dotenv()

# Set up the wave file to save the output:
def wave_file(filename, pcm, channels=1, rate=24000, sample_width=2):
    with wave.open(filename, "wb") as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(sample_width)
        wf.setframerate(rate)
        wf.writeframes(pcm)


def load_word_lists(filepath="word_lists.json"):
    """載入字詞表"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    full_path = os.path.join(script_dir, filepath)
    with open(full_path, "r", encoding="utf-8") as f:
        return json.load(f)


def pick_random_word(word_lists):
    """
    從 List A (A1/A2/A3) 隨機選一個字，
    從 List B (B1/B2/B3) 隨機選一個字，
    組合成一個雙字詞。
    """
    # 隨機選一個 A list 和一個 B list
    a_list_name = random.choice(["list_A1", "list_A2", "list_A3"])
    b_list_name = random.choice(["list_B1", "list_B2", "list_B3"])

    a_char = random.choice(word_lists[a_list_name])
    b_char = random.choice(word_lists[b_list_name])

    print(f"  A字: {a_char} (from {a_list_name})")
    print(f"  B字: {b_char} (from {b_list_name})")
    print(f"  組合: {a_char}{b_char}")
    return a_char, b_char


def synthesize_word(client, a_char, b_char, max_retries=3):
    """使用 Gemini TTS 朗讀指定的兩個字"""
    word = f"{a_char}"
    word2 = f"{b_char}"
    print(f"\n正在生成語音:{word}{word2}")

    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash-preview-tts",
                # contents=f"Say:{word}，{word2}",
                contents = (
                    "You are a professional phonetics assistant. "
                    "Please pronounce these two isolated Chinese characters clearly"
                    f"for a hearing test: {a_char}{b_char}. "
                    "Do not interpret the meaning, just read the sounds."
                ),
                config=types.GenerateContentConfig(
                    response_modalities=["AUDIO"],
                    speech_config=types.SpeechConfig(
                        language_code='cmn',
                        voice_config=types.VoiceConfig(
                            prebuilt_voice_config=types.PrebuiltVoiceConfig(
                                voice_name='Kore',
                            )
                        )
                    ),
                ),
            )

            data = response.candidates[0].content.parts[0].inline_data.data
            # 儲存到 result 資料夾
            script_dir = os.path.dirname(os.path.abspath(__file__))
            result_dir = os.path.join(script_dir, "result")
            os.makedirs(result_dir, exist_ok=True)
            file_name = f"{a_char}{b_char}.wav"
            file_path = os.path.join(result_dir, file_name)
            wave_file(file_path, data)
            print(f"✅ 音訊已儲存至 {file_path}")
            break

        except Exception as e:
            print(f"❌ 生成語音時發生錯誤: {e}")

def main():
    print("=" * 50)
    print("  MMRT 字詞 TTS 生成器")
    print("=" * 50)

    # 載入字詞表
    word_lists = load_word_lists()
    print("✅ 字詞表載入成功！")

    # 初始化 Gemini 客戶端
    client = genai.Client()
    print("✅ Gemini 客戶端初始化成功！")

    file_counter = 1

    print("\n按 Enter 隨機生成一個詞並朗讀")
    print("輸入 'quit' 或 'exit' 離開")
    print("-" * 50)

    while True:
        try:
            user_input = input("\n按 Enter 生成下一個詞 (或輸入 quit 離開): ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n\n👋 再見！")
            break

        if user_input.lower() in ("quit", "exit", "q"):
            print("\n👋 再見！")
            break

        # 隨機選詞
        a_char, b_char = pick_random_word(word_lists)

        # 生成語音
        output_file = f"output_{file_counter:03d}.wav"
        try:
            synthesize_word(client, a_char, b_char)
            file_counter += 1
        except Exception as e:
            print(f"❌ 生成語音時發生錯誤: {e}")


if __name__ == "__main__":
    main()