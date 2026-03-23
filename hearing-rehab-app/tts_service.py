#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TTS 服務整合模組
支援 Gemini TTS 和 Qwen3-TTS 兩種語音合成引擎
"""

import os
import json
import wave
import logging
from typing import List, Optional, Tuple, Union
from abc import ABC, abstractmethod
import numpy as np

# Gemini TTS 相關
from dotenv import load_dotenv
from google import genai
from google.genai import types

# Qwen3-TTS 相關 (條件性導入)
try:
    import sys
    import os
    # 添加 qwen3-tts 到 Python 路徑
    qwen3_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'qwen3-tts')
    if os.path.exists(qwen3_path):
        sys.path.insert(0, qwen3_path)
    
    import torch
    import soundfile as sf
    from qwen_tts import Qwen3TTSModel
    QWEN_AVAILABLE = True
    logging.info(f"Qwen3-TTS 載入成功，路徑: {qwen3_path}")
except ImportError as e:
    QWEN_AVAILABLE = False
    logging.warning(f"Qwen3-TTS 未安裝，將只使用 Gemini TTS: {e}")

load_dotenv()
logger = logging.getLogger(__name__)


class TTSEngine(ABC):
    """TTS 引擎抽象基類"""
    
    @abstractmethod
    def synthesize(self, text: str, output_path: str, **kwargs) -> bool:
        """
        合成語音
        
        Args:
            text: 要合成的文字
            output_path: 輸出音檔路徑
            **kwargs: 其他參數
            
        Returns:
            bool: 是否成功
        """
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """檢查引擎是否可用"""
        pass


class GeminiTTSEngine(TTSEngine):
    """Gemini TTS 引擎"""
    
    def __init__(self):
        self.client = None
        self._initialize()
    
    def _initialize(self):
        """初始化 Gemini 客戶端"""
        try:
            self.client = genai.Client()
            logger.info("Gemini TTS 引擎初始化成功")
        except Exception as e:
            logger.error(f"Gemini TTS 引擎初始化失敗: {e}")
            self.client = None
    
    def is_available(self) -> bool:
        return self.client is not None
    
    def synthesize(self, text: str, output_path: str, **kwargs) -> bool:
        """使用 Gemini TTS 合成語音"""
        if not self.is_available():
            return False
        
        try:
            voice_name = kwargs.get('voice_name', 'Kore')
            language_code = kwargs.get('language_code', 'cmn')
            
            response = self.client.models.generate_content(
                model="gemini-2.5-flash-preview-tts",
                contents=f"請清楚地朗讀這個中文字: {text}",
                config=types.GenerateContentConfig(
                    response_modalities=["AUDIO"],
                    speech_config=types.SpeechConfig(
                        language_code=language_code,
                        voice_config=types.VoiceConfig(
                            prebuilt_voice_config=types.PrebuiltVoiceConfig(
                                voice_name=voice_name,
                            )
                        )
                    ),
                ),
            )
            
            # 檢查回應是否有效
            if not response or not response.candidates:
                logger.error("Gemini API 回應無效")
                return False
            
            candidate = response.candidates[0]
            if not candidate.content or not candidate.content.parts:
                logger.error("Gemini API 回應內容無效")
                return False
            
            part = candidate.content.parts[0]
            if not hasattr(part, 'inline_data') or not part.inline_data:
                logger.error("Gemini API 回應沒有音訊資料")
                return False
            
            data = part.inline_data.data
            self._save_wave_file(output_path, data)
            logger.info(f"Gemini TTS 合成成功: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Gemini TTS 合成失敗: {e}")
            return False
    
    def _save_wave_file(self, filename: str, pcm_data: bytes, channels=1, rate=24000, sample_width=2):
        """儲存 WAV 檔案"""
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with wave.open(filename, "wb") as wf:
            wf.setnchannels(channels)
            wf.setsampwidth(sample_width)
            wf.setframerate(rate)
            wf.writeframes(pcm_data)


class Qwen3TTSEngine(TTSEngine):
    """Qwen3-TTS 引擎"""
    
    def __init__(self, model_path: str = None):
        if model_path is None:
            # 嘗試找到模型路徑
            possible_paths = [
                "../models/qwen3-tts-custom",
                "./models/qwen3-tts-custom", 
                "Qwen/Qwen3-TTS-12Hz-1.7B-CustomVoice"
            ]
            
            for path in possible_paths:
                if os.path.exists(path):
                    self.model_path = path
                    break
            else:
                # 如果本地路徑都不存在，使用 HuggingFace Hub
                self.model_path = "Qwen/Qwen3-TTS-12Hz-1.7B-CustomVoice"
        else:
            self.model_path = model_path
            
        self.model = None
        self.device = "cuda:0" if torch.cuda.is_available() else "cpu"
        self._initialize()
    
    def _initialize(self):
        """初始化 Qwen3-TTS 模型"""
        if not QWEN_AVAILABLE:
            logger.warning("Qwen3-TTS 不可用")
            return
        
        try:
            # 檢查是否有 flash-attention
            try:
                import flash_attn
                attn_implementation = "flash_attention_2"
                logger.info("使用 Flash Attention 2")
            except ImportError:
                attn_implementation = "eager"
                logger.info("Flash Attention 不可用，使用標準注意力機制")
            
            self.model = Qwen3TTSModel.from_pretrained(
                self.model_path,
                device_map=self.device,
                dtype=torch.bfloat16 if torch.cuda.is_available() else torch.float32,
                attn_implementation=attn_implementation,
            )
            logger.info(f"Qwen3-TTS 引擎初始化成功 (device: {self.device})")
        except Exception as e:
            logger.error(f"Qwen3-TTS 引擎初始化失敗: {e}")
            self.model = None
    
    def is_available(self) -> bool:
        return QWEN_AVAILABLE and self.model is not None
    
    def synthesize(self, text: str, output_path: str, **kwargs) -> bool:
        """使用 Qwen3-TTS 合成語音"""
        if not self.is_available():
            return False
        
        try:
            language = kwargs.get('language', 'Chinese')
            
            # 檢查模型類型
            if hasattr(self.model.model, 'tts_model_type'):
                model_type = self.model.model.tts_model_type
            else:
                model_type = "unknown"
            
            if model_type == "custom_voice":
                # Custom Voice 模型
                speaker = kwargs.get('speaker', 'vivian')  # 使用支援的說話者
                wavs, sr = self.model.generate_custom_voice(
                    text=text,
                    speaker=speaker,
                    language=language,
                    max_new_tokens=2048,
                    do_sample=True,
                    top_k=50,
                    top_p=1.0,
                    temperature=0.9,
                )
            elif model_type == "base":
                # Base 模型需要參考音檔
                ref_audio = kwargs.get('ref_audio')
                ref_text = kwargs.get('ref_text')
                
                if not ref_audio or not ref_text:
                    logger.error("Qwen3-TTS Base 模型需要參考音檔和參考文字")
                    return False
                
                wavs, sr = self.model.generate_voice_clone(
                    text=text,
                    language=language,
                    ref_audio=ref_audio,
                    ref_text=ref_text,
                    x_vector_only_mode=kwargs.get('x_vector_only_mode', False),
                    max_new_tokens=2048,
                    do_sample=True,
                    top_k=50,
                    top_p=1.0,
                    temperature=0.9,
                )
            else:
                logger.error(f"不支援的模型類型: {model_type}")
                return False
            
            # 儲存音檔
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            sf.write(output_path, wavs[0], sr)
            logger.info(f"Qwen3-TTS 合成成功: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Qwen3-TTS 合成失敗: {e}")
            return False


class TTSService:
    """TTS 服務管理器"""
    
    def __init__(self, preferred_engine: str = "gemini"):
        self.engines = {}
        self.preferred_engine = preferred_engine
        self._initialize_engines()
    
    def _initialize_engines(self):
        """初始化所有可用的 TTS 引擎"""
        # 初始化 Gemini TTS
        gemini_engine = GeminiTTSEngine()
        if gemini_engine.is_available():
            self.engines['gemini'] = gemini_engine
            logger.info("Gemini TTS 引擎已載入")
        
        # 初始化 Qwen3-TTS
        if QWEN_AVAILABLE:
            qwen_engine = Qwen3TTSEngine()
            if qwen_engine.is_available():
                self.engines['qwen3'] = qwen_engine
                logger.info("Qwen3-TTS 引擎已載入")
    
    def get_available_engines(self) -> List[str]:
        """獲取可用的引擎列表"""
        return list(self.engines.keys())
    
    def synthesize_word(self, word: str, list_name: str, engine: Optional[str] = None) -> str:
        """
        為單個字詞合成語音
        
        Args:
            word: 要合成的字詞
            list_name: 列表名稱 (如 A1, A2, B1 等)
            engine: 指定使用的引擎，None 則使用預設引擎
            
        Returns:
            str: 生成的音檔路徑，失敗則返回空字串
        """
        # 選擇引擎
        engine_name = engine or self.preferred_engine
        if engine_name not in self.engines:
            # 如果指定引擎不可用，使用第一個可用引擎
            if self.engines:
                engine_name = list(self.engines.keys())[0]
            else:
                logger.error("沒有可用的 TTS 引擎")
                return ""
        
        tts_engine = self.engines[engine_name]
        
        # 生成輸出路徑
        output_dir = f"data/audio/{list_name}"
        output_path = f"{output_dir}/{list_name}_{word}.wav"
        
        # 合成語音
        success = tts_engine.synthesize(word, output_path)
        
        if success:
            logger.info(f"使用 {engine_name} 引擎成功合成: {word} -> {output_path}")
            return output_path
        else:
            logger.error(f"使用 {engine_name} 引擎合成失敗: {word}")
            return ""
    
    def batch_synthesize_list(self, word_list: List[str], list_name: str, engine: Optional[str] = None) -> List[str]:
        """
        批次合成整個列表的語音
        
        Args:
            word_list: 字詞列表
            list_name: 列表名稱
            engine: 指定使用的引擎
            
        Returns:
            List[str]: 成功生成的音檔路徑列表
        """
        successful_paths = []
        
        for word in word_list:
            path = self.synthesize_word(word, list_name, engine)
            if path:
                successful_paths.append(path)
        
        logger.info(f"批次合成完成: {len(successful_paths)}/{len(word_list)} 個音檔")
        return successful_paths
    
    def synthesize_missing_audio(self, word_lists: dict, engine: Optional[str] = None) -> dict:
        """
        檢查並合成缺失的音檔
        
        Args:
            word_lists: 字詞列表字典
            engine: 指定使用的引擎
            
        Returns:
            dict: 合成結果統計
        """
        stats = {
            'total_checked': 0,
            'missing_found': 0,
            'successfully_generated': 0,
            'failed_generation': 0
        }
        
        for list_key, words in word_lists.items():
            if not isinstance(words, list):
                continue
                
            list_code = list_key.replace('list_', '')
            
            for word in words:
                stats['total_checked'] += 1
                audio_path = f"data/audio/{list_code}/{list_code}_{word}.wav"
                
                if not os.path.exists(audio_path):
                    stats['missing_found'] += 1
                    logger.info(f"發現缺失音檔: {audio_path}")
                    
                    # 嘗試生成
                    generated_path = self.synthesize_word(word, list_code, engine)
                    if generated_path:
                        stats['successfully_generated'] += 1
                    else:
                        stats['failed_generation'] += 1
        
        logger.info(f"音檔檢查完成: {stats}")
        return stats


# 全域 TTS 服務實例
tts_service = TTSService()