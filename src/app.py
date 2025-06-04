import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# サーバー起動時
from flask import Flask, request, jsonify
from flask_cors import CORS
import json
from datetime import datetime
from typing import Dict, List, Any
from config import Config
from utils.openai_utils import SimpleTaskJudgeSystem

app = Flask(__name__)
CORS(app)

class TaskManager:
    def __init__(self, tasks_file='tasks/tasks.json'):
        self.tasks_file = tasks_file
        self.load_tasks()
    
    def load_tasks(self):
        """JSONファイルからタスクデータを読み込み"""
        try:
            with open(self.tasks_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.task_metadata = data.get('task_metadata', {})
                self.tasks = data.get('tasks', {})
                self.task_order = data.get('task_order', [])
                self.current_step = data.get('current_step', self.task_order[0] if self.task_order else "step1")
                print(f"✓ タスクデータを読み込みました: {len(self.tasks)}個のタスク")
        except FileNotFoundError:
            print(f"⚠️ {self.tasks_file} が見つかりません。デフォルトタスクを使用します。")
            self._create_default_tasks()
        except json.JSONDecodeError as e:
            print(f"⚠️ {self.tasks_file} の読み込みエラー: {e}")
            self._create_default_tasks()
    
    def _create_default_tasks(self):
        """デフォルトタスクを作成（フォールバック）"""
        self.task_metadata = {
            "title": "研究室Zoom会議準備タスク",
            "total_steps": 7
        }
        self.tasks = {
            "step1": {"description": "中会議室のカギを開ける", "completed": False},
            "step2": {"description": "MacBookと充電器とUSBポートを用意する", "completed": False},
            "step3": {"description": "みんながPCを充電する用の延長ケーブルをつなぐ", "completed": False},
            "step4": {"description": "Macで研究室Zoomにつなぐ", "completed": False},
            "step5": {"description": "Owlカメラとyamahaのマイクとスクリーンつける", "completed": False},
            "step6": {"description": "こいつらをUSBポート介してUSBとHDMIでMacにつなぐ", "completed": False},
            "step7": {"description": "Zoomのカメラ＆マイクON", "completed": False}
        }
        self.task_order = ["step1", "step2", "step3", "step4", "step5", "step6", "step7"]
        self.current_step = "step1"
    
    def save_tasks(self):
        """現在のタスク状態をJSONファイルに保存"""
        try:
            # ディレクトリが存在しない場合は作成
            os.makedirs(os.path.dirname(self.tasks_file), exist_ok=True)
            
            data = {
                "task_metadata": self.task_metadata,
                "tasks": self.tasks,
                "task_order": self.task_order,
                "current_step": self.current_step
            }
            with open(self.tasks_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print("✓ タスク状態を保存しました")
        except Exception as e:
            print(f"⚠️ タスク保存エラー: {e}")
    
    def get_current_task(self):
        current_task_data = self.tasks.get(self.current_step, {})
        return {
            "step": self.current_step,
            "task": current_task_data,
            "progress": f"{self.task_order.index(self.current_step) + 1}/{len(self.task_order)}",
            "metadata": self.task_metadata
        }
    
    def complete_current_task(self):
        self.tasks[self.current_step]["completed"] = True
        current_index = self.task_order.index(self.current_step)
        if current_index < len(self.task_order) - 1:
            self.current_step = self.task_order[current_index + 1]
            self.save_tasks()  # 状態を保存
            return True
        self.save_tasks()  # 完了時も保存
        return False  # 全てのタスクが完了
    
    def get_all_tasks_status(self):
        return {
            "current_step": self.current_step,
            "tasks": self.tasks,
            "completion_rate": sum(1 for task in self.tasks.values() if task["completed"]) / len(self.tasks),
            "metadata": self.task_metadata
        }
    
    def reset_tasks(self):
        """全タスクをリセット"""
        for task in self.tasks.values():
            task["completed"] = False
        self.current_step = self.task_order[0] if self.task_order else "step1"
        self.save_tasks()

# グローバルインスタンス
task_manager = TaskManager()
llm_system = SimpleTaskJudgeSystem()

@app.route('/')
def health_check():
    return jsonify({
        "success": True,
        "data": {
            "status": "running",
            "service": "Unity Task Management Server"
        },
        "message": "Service is healthy and running",
        "timestamp": datetime.now().isoformat()
    }), 200

@app.route('/api/current-task', methods=['GET'])
def get_current_task():
    try:
        task_data = task_manager.get_current_task()
        return jsonify({
            "success": True,
            "data": task_data,
            "message": "Current task retrieved successfully",
            "timestamp": datetime.now().isoformat()
        }), 200
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "message": "Failed to retrieve current task",
            "timestamp": datetime.now().isoformat()
        }), 500

@app.route('/api/task-status', methods=['GET'])
def get_task_status():
    try:
        status_data = task_manager.get_all_tasks_status()
        return jsonify({
            "success": True,
            "data": status_data,
            "message": "Task status retrieved successfully",
            "timestamp": datetime.now().isoformat()
        }), 200
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "message": "Failed to retrieve task status",
            "timestamp": datetime.now().isoformat()
        }), 500

@app.route('/api/environment-update', methods=['POST'])
def update_environment():
    """Unity環境情報の更新とシンプルなタスク判定"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                "success": False,
                "error": "No JSON data provided",
                "message": "Request body must contain JSON data",
                "timestamp": datetime.now().isoformat()
            }), 400
        
        current_task = data.get('current_task', '')
        player_status = data.get('player_status', '')
        surroundings = data.get('surroundings', '')
        
        print(f"\n🎮 Unity環境更新:")
        print(f"   タスク: {current_task}")
        print(f"   状況: {player_status}")
        
        # シンプルなタスク判定
        result = llm_system.judge_task_status(
            current_task=current_task,
            player_status=player_status,
            surroundings=surroundings
        )
        
        # タスク完了判定とNext Task追加
        if result.get("data", {}).get('action') == 'next':
            task_id = result.get("data", {}).get('task_id')
            print(f"🎯 タスク完了判定: 次のタスク {task_id}")
            has_next = task_manager.complete_current_task()
            
            if has_next:
                next_task = task_manager.get_current_task()
                result["data"]["next_task"] = next_task
                print(f"   → 次のタスク: {next_task['task']['description']}")
            else:
                result["data"]["all_completed"] = True
                result["message"] = "All tasks completed!"
                print("🎉 全タスク完了！")
        
        return jsonify(result), 200
        
    except Exception as e:
        print(f"❌ 環境更新エラー: {e}")
        return jsonify({
            "success": False,
            "error": str(e),
            "message": "Internal server error during task judgment",
            "data": {
                "action": "keep",  # エラー時は継続
                "task_id": None
            },
            "timestamp": datetime.now().isoformat()
        }), 500

@app.route('/api/force-complete-task', methods=['POST'])
def force_complete_task():
    """現在のタスクを強制完了"""
    try:
        has_next = task_manager.complete_current_task()
        current_task = task_manager.get_current_task()
        
        return jsonify({
            "success": True,
            "data": {
                "has_next_task": has_next,
                "current_task": current_task
            },
            "message": "Task completed successfully",
            "timestamp": datetime.now().isoformat()
        }), 200
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "message": "Failed to complete task",
            "timestamp": datetime.now().isoformat()
        }), 500

@app.route('/api/reset-tasks', methods=['POST'])
def reset_tasks():
    """全タスクをリセット"""
    try:
        task_manager.reset_tasks()
        current_task = task_manager.get_current_task()
        
        return jsonify({
            "success": True,
            "data": {
                "current_task": current_task
            },
            "message": "All tasks have been reset successfully",
            "timestamp": datetime.now().isoformat()
        }), 200
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "message": "Failed to reset tasks",
            "timestamp": datetime.now().isoformat()
        }), 500

if __name__ == '__main__':
    print("🚀 Unity Task Management Server 起動中...")
    print(f"🔧 LLMモデル: {Config.LLM_MODEL}")
    print(f"🌡️  Temperature: {Config.LLM_TEMPERATURE}")
    print(f"📊 最大トークン: {Config.LLM_MAX_TOKENS}")
    
    Config.print_config()
    
    # 設定の妥当性チェック
    config_errors = Config.validate_config()
    if config_errors:
        print("⚠️  設定エラー:")
        for error in config_errors:
            print(f"   - {error}")
    
    app.run(
        host=Config.UNITY_SERVER_HOST,
        port=Config.UNITY_SERVER_PORT,
        debug=Config.DEBUG_MODE
    ) 