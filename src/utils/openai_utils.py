#!/usr/bin/env python3
"""
Unity Task Management - LLMタスク判定システム
"""

from openai import OpenAI
import json
import os
from datetime import datetime
from typing import Dict, Any
import sys

# プロジェクト設定をインポート
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
try:
    from config import Config
except ImportError:
    sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    from config import Config

class TaskProgressAnalyzer:
    """LLM: タスク進捗状況を分析・判定"""
    
    def __init__(self):
        # OpenAIクライアント初期化
        api_key = Config.OPENAI_API_KEY or os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OpenAI API key not found. Please set OPENAI_API_KEY environment variable.")
        
        self.client = OpenAI(api_key=api_key)
        self.model = Config.LLM_MODEL
        self.max_tokens = 50
        self.temperature = Config.LLM_TEMPERATURE
    
    def analyze_task_progress(self, current_task: str, player_status: str, surroundings: str = "", task_pool: list = None) -> Dict[str, Any]:
        """
        Unity状況とタスクを分析し、シンプルな判定を返す
        
        Returns:
            判定結果（keepまたはpick + task_id）
        """
        
        task_pool_str = "\n".join([f"- {task}" for task in (task_pool or [])])
        
        prompt = f"""あなたはUnityゲームのタスク判定システムです。プレイヤーの行動を分析し、現在のタスクが完了したかどうかを正確に判定してください。

【現在のタスク】
{current_task}

【プレイヤーの状況】
{player_status}

【周囲の環境】  
{surroundings}

【利用可能なタスクプール】
{task_pool_str}

判定基準：
- タスクの目標が完全に達成されている場合 → 次のタスクID (step2, step3など)
- タスクの目標が未達成、または進行中の場合 → "keep"

具体的な判定例：
- 「カギを開ける」→「ドアを開けた、入った」= 完了 → step2
- 「機器を用意する」→「設置した、準備完了」= 完了 → step3  
- 「接続する」→「接続した、認識された」= 完了 → step4
- 「ONする」→「有効化した、ONした」= 完了 → 次のstep

現在の状況を分析して、以下のいずれかのみで回答してください：

1. タスクが完了している場合: 次のタスクID（step2, step3, step4, step5, step6, step7）
2. タスクが未完了の場合: "keep"

回答:"""

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "あなたはシンプルなタスク判定システムです。keepまたはタスクIDのみで回答します。"},
                {"role": "user", "content": prompt}
            ],
            max_tokens=self.max_tokens,
            temperature=self.temperature
        )
        
        result_text = response.choices[0].message.content.strip().lower()
        
        # 結果の解析
        if result_text == "keep":
            return {
                "action": "keep", 
                "task_id": None,
                "completed": False,
                "raw_response": result_text
            }
        else:
            return {
                "action": "next",
                "task_id": result_text,
                "completed": True,
                "raw_response": result_text
            }


class SimpleTaskJudgeSystem:
    """シンプルなタスク判定システム"""
    
    def __init__(self):
        self.task_analyzer = TaskProgressAnalyzer()
    
    def judge_task_status(
        self, 
        current_task: str, 
        player_status: str, 
        surroundings: str = "",
        task_pool: list = None
    ) -> Dict[str, Any]:
        """
        Unity状況を分析し、シンプルな判定を返す
        """
        
        print(f"🔍 タスク判定開始: {current_task}")
        
        # タスク判定
        result = self.task_analyzer.analyze_task_progress(
            current_task=current_task,
            player_status=player_status,
            surroundings=surroundings,
            task_pool=task_pool or ["step1", "step2", "step3", "step4", "step5", "step6", "step7"]
        )
        
        print(f"📊 判定結果: {result['action']}" + (f" -> {result.get('task_id')}" if result.get('task_id') else ""))
        
        return {
            "success": True,
            "data": {
                "action": result["action"],
                "task_id": result.get("task_id"),
            },
            "timestamp": datetime.now().isoformat(),
            "message": f"Task judgment completed: {result['action']}" + (f" -> {result.get('task_id')}" if result.get('task_id') else "")
        }
