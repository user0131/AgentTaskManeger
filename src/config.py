# システムの心臓部

import os
from dotenv import load_dotenv

# .envファイルを読み込み
load_dotenv()

class Config:
    # OpenAI設定
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
    
    # Unity通信設定
    UNITY_SERVER_HOST = os.getenv('UNITY_SERVER_HOST', '0.0.0.0')
    UNITY_SERVER_PORT = int(os.getenv('UNITY_SERVER_PORT', 5000))
    
    # デバッグモード
    DEBUG_MODE = os.getenv('DEBUG_MODE', 'true').lower() == 'true'
    
    # LLM設定
    LLM_MODEL = os.getenv('LLM_MODEL', 'gpt-3.5-turbo')
    LLM_MAX_TOKENS = int(os.getenv('LLM_MAX_TOKENS', 500))
    LLM_TEMPERATURE = float(os.getenv('LLM_TEMPERATURE', 0.0))
    
    # タスク設定
    TASK_COMPLETION_TIMEOUT = int(os.getenv('TASK_COMPLETION_TIMEOUT', 30))
    AUTO_TASK_PROGRESSION = os.getenv('AUTO_TASK_PROGRESSION', 'true').lower() == 'true'
    
    @classmethod
    def validate_config(cls):
        """設定の妥当性をチェック"""
        errors = []
        
        if not cls.OPENAI_API_KEY:
            errors.append("OPENAI_API_KEY が設定されていません")
        
        if cls.UNITY_SERVER_PORT < 1 or cls.UNITY_SERVER_PORT > 65535:
            errors.append("UNITY_SERVER_PORT は1-65535の範囲で設定してください")
        
        return errors
    
    @classmethod
    def print_config(cls):
        """設定の確認用表示"""
        print("=== Unity Task Management System Configuration ===")
        print(f"Server: {cls.UNITY_SERVER_HOST}:{cls.UNITY_SERVER_PORT}")
        print(f"Debug Mode: {cls.DEBUG_MODE}")
        print(f"LLM Model: {cls.LLM_MODEL}")
        print(f"OpenAI API Key: {'設定済み' if cls.OPENAI_API_KEY else '未設定'}")
        print(f"Task Completion Timeout: {cls.TASK_COMPLETION_TIMEOUT}秒")
        print("=" * 50) 