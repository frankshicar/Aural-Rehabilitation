from flask import Flask, render_template, request, jsonify, send_from_directory
import json
import random
import os
import google.generativeai as genai
from datetime import datetime
import logging
from tts_service import tts_service

app = Flask(__name__)

# 設定日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 載入環境變數
from dotenv import load_dotenv
load_dotenv('.env')

# 設定 Gemini API
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
model = genai.GenerativeModel('gemini-pro')

# 載入詞彙列表
with open('data/word_lists.json', 'r', encoding='utf-8') as f:
    word_lists = json.load(f)

class AudioRehabSession:
    def __init__(self):
        self.current_question = 0
        self.total_questions = 20
        self.correct_answers = 0
        self.wrong_answers = []
        self.session_data = []
        self.current_question_data = None
        
    def get_random_question(self):
        """隨機選擇一個音檔和選項"""
        # 隨機選擇一個列表
        available_lists = ['list_A1', 'list_A2', 'list_A3', 'list_B1', 'list_B2', 'list_B3']
        selected_list = random.choice(available_lists)
        
        # 從選中的列表隨機選擇一個詞
        correct_word = random.choice(word_lists[selected_list])
        
        # 生成音檔路徑
        list_code = selected_list.replace('list_', '')
        audio_file = f"audio/{list_code}/{list_code}_{correct_word}.wav"
        
        # 檢查音檔是否存在
        audio_path = f"data/{audio_file}"
        if not os.path.exists(audio_path):
            logger.warning(f"音檔不存在: {audio_path}")
            return self.get_random_question()  # 遞歸重試
        
        # 生成選項（包含正確答案和3個錯誤選項）
        options = [correct_word]
        
        # 從同一列表中選擇錯誤選項
        wrong_options = [word for word in word_lists[selected_list] if word != correct_word]
        options.extend(random.sample(wrong_options, min(3, len(wrong_options))))
        
        # 如果選項不足4個，從其他列表補充
        if len(options) < 4:
            all_words = []
            for lst in word_lists.values():
                if isinstance(lst, list):
                    all_words.extend(lst)
            
            remaining_words = [word for word in all_words if word not in options]
            needed = 4 - len(options)
            options.extend(random.sample(remaining_words, min(needed, len(remaining_words))))
        
        # 隨機排列選項
        random.shuffle(options)
        
        question_data = {
            'audio_file': audio_file,
            'correct_answer': correct_word,
            'options': options,
            'list_type': selected_list
        }
        
        # 儲存當前問題數據
        self.current_question_data = question_data
        return question_data

# 全域會話物件
session = AudioRehabSession()

@app.route('/')
def index():
    """主頁面"""
    return render_template('index.html')

@app.route('/start_session', methods=['POST'])
def start_session():
    """開始新的復健會話"""
    global session
    session = AudioRehabSession()
    return jsonify({'status': 'success', 'message': '會話已開始'})

@app.route('/get_question')
def get_question():
    """獲取下一個問題"""
    if session.current_question >= session.total_questions:
        return jsonify({'status': 'completed'})
    
    question_data = session.get_random_question()
    session.current_question += 1
    
    return jsonify({
        'status': 'success',
        'question_number': session.current_question,
        'total_questions': session.total_questions,
        'audio_file': question_data['audio_file'],
        'options': question_data['options'],
        'question_id': session.current_question - 1
    })

@app.route('/submit_answer', methods=['POST'])
def submit_answer():
    """提交答案"""
    data = request.json
    selected_answer = data.get('answer')
    question_id = data.get('question_id')
    
    if not session.current_question_data:
        return jsonify({'error': '沒有當前問題數據'})
    
    correct_answer = session.current_question_data['correct_answer']
    is_correct = selected_answer == correct_answer
    
    if is_correct:
        session.correct_answers += 1
    else:
        session.wrong_answers.append({
            'question_id': question_id,
            'correct_answer': correct_answer,
            'selected_answer': selected_answer,
            'audio_file': session.current_question_data['audio_file']
        })
    
    session.session_data.append({
        'question_id': question_id,
        'correct_answer': correct_answer,
        'selected_answer': selected_answer,
        'is_correct': is_correct,
        'timestamp': datetime.now().isoformat()
    })
    
    return jsonify({
        'status': 'success',
        'is_correct': is_correct,
        'correct_answer': correct_answer
    })

@app.route('/get_report')
def get_report():
    """生成並返回復健報告"""
    if session.current_question == 0:
        return jsonify({'error': '尚未開始測試'})
    
    # 計算統計數據
    accuracy = (session.correct_answers / session.current_question) * 100
    
    # 準備 Gemini API 的提示
    prompt = f"""
    請為聽能復健患者生成一份詳細的復健報告。以下是測試結果：

    測試統計：
    - 總題數：{session.current_question}
    - 正確答案：{session.correct_answers}
    - 錯誤答案：{len(session.wrong_answers)}
    - 準確率：{accuracy:.1f}%

    錯誤詳情：
    """
    
    for wrong in session.wrong_answers:
        prompt += f"- 音檔：{wrong['audio_file']}，正確答案：{wrong['correct_answer']}，患者選擇：{wrong['selected_answer']}\n"
    
    prompt += """
    請提供：
    1. 整體表現評估
    2. 錯誤模式分析
    3. 具體改善建議
    4. 後續復健方向

    請用繁體中文回答，語氣要專業但溫和鼓勵。
    """
    
    try:
        response = model.generate_content(prompt)
        report = response.text
    except Exception as e:
        logger.error(f"Gemini API 錯誤: {e}")
        report = f"報告生成失敗，但您的測試結果是：準確率 {accuracy:.1f}%，共答對 {session.correct_answers} 題，答錯 {len(session.wrong_answers)} 題。"
    
    return jsonify({
        'status': 'success',
        'report': report,
        'statistics': {
            'total_questions': session.current_question,
            'correct_answers': session.correct_answers,
            'wrong_answers': len(session.wrong_answers),
            'accuracy': accuracy
        }
    })

@app.route('/audio/<path:filename>')
def serve_audio(filename):
    """提供音檔服務"""
    return send_from_directory('data/audio', filename)

@app.route('/generate_audio', methods=['POST'])
def generate_audio():
    """生成單個字詞的語音"""
    data = request.json
    word = data.get('word')
    list_name = data.get('list_name', 'A1')
    engine = data.get('engine')  # 可選：指定 TTS 引擎
    
    if not word:
        return jsonify({'error': '缺少字詞參數'})
    
    try:
        audio_path = tts_service.synthesize_word(word, list_name, engine)
        if audio_path:
            # 轉換為相對於 static 的路徑
            relative_path = audio_path.replace('data/', '')
            return jsonify({
                'status': 'success',
                'audio_path': relative_path,
                'engine_used': engine or tts_service.preferred_engine
            })
        else:
            return jsonify({'error': '語音生成失敗'})
    except Exception as e:
        logger.error(f"生成語音時發生錯誤: {e}")
        return jsonify({'error': f'生成語音時發生錯誤: {str(e)}'})

@app.route('/batch_generate_audio', methods=['POST'])
def batch_generate_audio():
    """批次生成語音"""
    data = request.json
    word_list = data.get('word_list', [])
    list_name = data.get('list_name', 'A1')
    engine = data.get('engine')
    
    if not word_list:
        return jsonify({'error': '缺少字詞列表'})
    
    try:
        successful_paths = tts_service.batch_synthesize_list(word_list, list_name, engine)
        return jsonify({
            'status': 'success',
            'generated_count': len(successful_paths),
            'total_count': len(word_list),
            'success_rate': len(successful_paths) / len(word_list) * 100,
            'engine_used': engine or tts_service.preferred_engine
        })
    except Exception as e:
        logger.error(f"批次生成語音時發生錯誤: {e}")
        return jsonify({'error': f'批次生成語音時發生錯誤: {str(e)}'})

@app.route('/check_missing_audio', methods=['POST'])
def check_missing_audio():
    """檢查並生成缺失的音檔"""
    data = request.json
    engine = data.get('engine')
    
    try:
        stats = tts_service.synthesize_missing_audio(word_lists, engine)
        return jsonify({
            'status': 'success',
            'stats': stats,
            'engine_used': engine or tts_service.preferred_engine
        })
    except Exception as e:
        logger.error(f"檢查缺失音檔時發生錯誤: {e}")
        return jsonify({'error': f'檢查缺失音檔時發生錯誤: {str(e)}'})

@app.route('/tts_admin')
def tts_admin():
    """TTS 管理介面"""
    return render_template('tts_admin.html')

@app.route('/tts_engines')
def get_tts_engines():
    """獲取可用的 TTS 引擎"""
    return jsonify({
        'available_engines': tts_service.get_available_engines(),
        'preferred_engine': tts_service.preferred_engine
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)