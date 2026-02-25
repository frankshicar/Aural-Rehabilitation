import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

# 載入 .env 檔案中的環境變數
load_dotenv()

# 可選的聲音列表
AVAILABLE_VOICES = ["Puck", "Charon", "Kore", "Fenrir", "Aoede"]


def generate_speech(client, text: str, voice_name: str, output_filename: str):
    """
    使用 Gemini API 將文字轉為音訊並存檔

    :param client: Gemini 客戶端
    :param text: 要轉換的文字
    :param voice_name: 人物聲音名稱 (可選: Puck, Charon, Kore, Fenrir, Aoede)
    :param output_filename: 輸出的音訊檔案名稱
    """
    print(f"\n正在使用 '{voice_name}' 的聲音生成音訊...")

    try:
        response = client.models.generate_content(
            model='gemini-2.0-flash',
            contents=text,
            config=types.GenerateContentConfig(
                response_modalities=["AUDIO"],
                speech_config=types.SpeechConfig(
                    voice_config=types.VoiceConfig(
                        prebuilt_voice_config=types.PrebuiltVoiceConfig(
                            voice_name=voice_name
                        )
                    )
                )
            )
        )

        # 尋找並儲存回傳的音訊資料
        for candidate in response.candidates:
            if candidate.content and candidate.content.parts:
                for part in candidate.content.parts:
                    if part.inline_data and part.inline_data.data:
                        audio_bytes = part.inline_data.data
                        with open(output_filename, "wb") as f:
                            f.write(audio_bytes)
                        print(f"✅ 成功！音訊已儲存至 {output_filename}")
                        return

        print("⚠️  API 回應成功，但未能在回傳內容中找到音訊資料。")

    except Exception as e:
        print(f"❌ 呼叫 API 時發生錯誤: {e}")


def select_voice() -> str:
    """讓使用者選擇聲音，回傳聲音名稱"""
    print("\n可選擇的聲音:")
    for i, voice in enumerate(AVAILABLE_VOICES, 1):
        print(f"  {i}. {voice}")
    print(f"  0. 保持目前設定")

    while True:
        choice = input("請輸入數字選擇聲音 (直接按 Enter 保持目前設定): ").strip()
        if choice == "" or choice == "0":
            return ""
        try:
            idx = int(choice)
            if 1 <= idx <= len(AVAILABLE_VOICES):
                return AVAILABLE_VOICES[idx - 1]
            else:
                print(f"  請輸入 1~{len(AVAILABLE_VOICES)} 之間的數字。")
        except ValueError:
            # 也允許直接輸入聲音名稱
            if choice in AVAILABLE_VOICES:
                return choice
            print(f"  無效輸入，請輸入數字或聲音名稱。")


def interactive_mode():
    """互動模式：手動輸入文字讓 Gemini 朗讀"""
    print("=" * 50)
    print("  Gemini TTS 互動模式")
    print("=" * 50)

    # 初始化 Gemini 客戶端
    try:
        client = genai.Client()
        print("✅ Gemini 客戶端初始化成功！")
    except Exception as e:
        print("❌ 用戶端初始化失敗，請確認已設定 GEMINI_API_KEY 環境變數。")
        print(f"   錯誤訊息: {e}")
        return

    # 預設聲音
    current_voice = "Aoede"
    # 輸出檔案計數器
    file_counter = 1

    print(f"\n目前使用的聲音: {current_voice}")
    print("輸入 'voice' 可更換聲音")
    print("輸入 'quit' 或 'exit' 可離開程式")
    print("-" * 50)

    while True:
        try:
            text = input("\n請輸入要朗讀的文字: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n\n👋 再見！")
            break

        if not text:
            print("  ⚠️  請輸入一些文字。")
            continue

        # 離開指令
        if text.lower() in ("quit", "exit", "q"):
            print("\n👋 再見！")
            break

        # 更換聲音指令
        if text.lower() == "voice":
            new_voice = select_voice()
            if new_voice:
                current_voice = new_voice
                print(f"  已切換聲音為: {current_voice}")
            else:
                print(f"  保持目前聲音: {current_voice}")
            continue

        # 產生輸出檔名
        output_file = f"output_{file_counter:03d}.wav"
        generate_speech(client, text, current_voice, output_file)
        file_counter += 1


if __name__ == "__main__":
    interactive_mode()
