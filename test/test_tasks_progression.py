#!/usr/bin/env python3
"""
Unity Task Management - 段階的タスク進行テスト
各ステップを段階的にテストし、LLMの判定動作を確認する
"""

import requests
import json
import time
from typing import Dict, Any

class TaskProgressionTester:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.test_scenarios = self._create_test_scenarios()
    
    def _create_test_scenarios(self) -> Dict[str, Dict[str, Any]]:
        """各ステップのテストシナリオを作成"""
        return {
            "step1": {
                "task": "中会議室のカギを開ける",
                "incomplete": {
                    "player_status": "プレイヤーは中会議室の前に立っている。鍵を探している。",
                    "surroundings": "中会議室のドア、鍵穴、廊下、他の部屋のドアが見える"
                },
                "complete": {
                    "player_status": "プレイヤーは鍵を使ってドアを開けた。中会議室に入った。",
                    "surroundings": "開いた中会議室のドア、室内のテーブル、椅子、ホワイトボードが見える"
                }
            },
            "step2": {
                "task": "MacBookと充電器とUSBポートを用意する",
                "incomplete": {
                    "player_status": "プレイヤーは会議室内でMacBookを探している。まだ見つかっていない。",
                    "surroundings": "会議室のテーブル、椅子、棚、カバン、書類が見える"
                },
                "complete": {
                    "player_status": "プレイヤーはMacBook、充電器、USBハブを机の上に設置した。",
                    "surroundings": "机の上にMacBook、充電器、USBハブが置かれている。コンセントが見える"
                }
            },
            "step3": {
                "task": "みんながPCを充電する用の延長ケーブルをつなぐ",
                "incomplete": {
                    "player_status": "プレイヤーは延長ケーブルを持っているが、まだ接続していない。",
                    "surroundings": "コンセント、延長ケーブル、USBハブ、MacBookが見える"
                },
                "complete": {
                    "player_status": "プレイヤーは延長ケーブルをコンセントに差し込んだ。充電環境が整った。",
                    "surroundings": "接続された延長ケーブル、電源タップ、充電中のデバイス類が見える"
                }
            },
            "step4": {
                "task": "Macで研究室Zoomにつなぐ",
                "incomplete": {
                    "player_status": "プレイヤーはMacBookを開いてZoomアプリを起動しようとしている。",
                    "surroundings": "起動中のMacBook、デスクトップ画面、アプリケーション一覧が見える"
                },
                "complete": {
                    "player_status": "プレイヤーはZoomミーティングに正常に接続した。画面に参加者が表示されている。",
                    "surroundings": "Zoom画面、接続中の表示、ミーティング参加者の映像が見える"
                }
            },
            "step5": {
                "task": "Owlカメラとyamahaのマイクとスクリーンつける",
                "incomplete": {
                    "player_status": "プレイヤーはOwlカメラを箱から出して設定場所を探している。",
                    "surroundings": "Owlカメラ、yamahaマイク、スクリーン、ケーブル類が机の上にある"
                },
                "complete": {
                    "player_status": "プレイヤーはOwlカメラ、yamahaマイク、スクリーンを全て設置し終えた。",
                    "surroundings": "設置済みのOwlカメラ、yamahaマイク、展開されたスクリーン、整理されたケーブル"
                }
            },
            "step6": {
                "task": "こいつらをUSBポート介してUSBとHDMIでMacにつなぐ",
                "incomplete": {
                    "player_status": "プレイヤーはUSBケーブルとHDMIケーブルを持って接続作業をしている。",
                    "surroundings": "MacBook、USBハブ、USBケーブル、HDMIケーブル、各種機器が見える"
                },
                "complete": {
                    "player_status": "プレイヤーは全ての機器をMacBookに正常に接続した。デバイス認識も完了。",
                    "surroundings": "接続済みの全機器、動作中のLEDライト、MacBookの認識通知が見える"
                }
            },
            "step7": {
                "task": "Zoomのカメラ＆マイクON",
                "incomplete": {
                    "player_status": "プレイヤーはZoom設定画面でカメラとマイクの設定を確認している。",
                    "surroundings": "Zoom設定画面、カメラプレビュー、マイクレベル表示が見える"
                },
                "complete": {
                    "player_status": "プレイヤーはZoomでカメラとマイクを有効化した。会議準備が完了した。",
                    "surroundings": "動作中のカメラ映像、マイクONの表示、完全に準備された会議環境"
                }
            }
        }
    
    def test_api_connection(self) -> bool:
        """APIサーバーとの接続テスト"""
        try:
            response = requests.get(f"{self.base_url}/")
            if response.status_code == 200:
                print("✅ Flask サーバー接続成功")
                return True
            else:
                print(f"❌ サーバー接続エラー: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ サーバー接続失敗: {e}")
            return False
    
    def send_environment_update(self, current_task: str, player_status: str, surroundings: str) -> Dict[str, Any]:
        """環境更新APIにデータを送信"""
        data = {
            "current_task": current_task,
            "player_status": player_status,
            "surroundings": surroundings
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/api/environment-update",
                json=data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ API エラー {response.status_code}: {response.text}")
                return {"success": False, "error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            print(f"❌ リクエスト送信失敗: {e}")
            return {"success": False, "error": str(e)}
    
    def reset_tasks(self) -> bool:
        """タスクをリセット"""
        try:
            response = requests.post(f"{self.base_url}/api/reset-tasks")
            if response.status_code == 200:
                print("🔄 タスクをリセットしました")
                return True
            else:
                print(f"❌ タスクリセット失敗: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ タスクリセット失敗: {e}")
            return False
    
    def test_step_progression(self, step_id: str) -> Dict[str, Any]:
        """指定ステップの進行テスト"""
        print(f"\n🎯 === {step_id.upper()} テスト開始 ===")
        
        scenario = self.test_scenarios[step_id]
        task = scenario["task"]
        
        print(f"📋 タスク: {task}")
        
        # 1. 未完了状態のテスト
        print("\n🔍 未完了状態テスト:")
        print(f"   状況: {scenario['incomplete']['player_status']}")
        
        incomplete_result = self.send_environment_update(
            current_task=task,
            player_status=scenario['incomplete']['player_status'],
            surroundings=scenario['incomplete']['surroundings']
        )
        
        if incomplete_result.get("success"):
            action = incomplete_result.get("data", {}).get("action")
            print(f"   結果: {action}")
            if action == "keep":
                print("   ✅ 正しく継続判定")
            else:
                print("   ⚠️  継続が期待されましたが、違う結果")
        else:
            print(f"   ❌ エラー: {incomplete_result.get('error')}")
        
        time.sleep(2)  # API呼び出し間隔
        
        # 2. 完了状態のテスト
        print("\n✅ 完了状態テスト:")
        print(f"   状況: {scenario['complete']['player_status']}")
        
        complete_result = self.send_environment_update(
            current_task=task,
            player_status=scenario['complete']['player_status'],
            surroundings=scenario['complete']['surroundings']
        )
        
        if complete_result.get("success"):
            action = complete_result.get("data", {}).get("action")
            task_id = complete_result.get("data", {}).get("task_id")
            print(f"   結果: {action}" + (f" -> {task_id}" if task_id else ""))
            
            if action == "pick":
                print("   ✅ 正しく完了判定")
                next_task = complete_result.get("data", {}).get("next_task")
                if next_task:
                    print(f"   📈 次のタスク: {next_task['task']['description']}")
            else:
                print("   ⚠️  完了が期待されましたが、継続判定")
        else:
            print(f"   ❌ エラー: {complete_result.get('error')}")
        
        return {
            "step": step_id,
            "incomplete_test": incomplete_result,
            "complete_test": complete_result
        }
    
    def run_full_progression_test(self):
        """全ステップの段階的テスト実行"""
        print("🚀 === Unity Task Management 段階的テスト開始 ===")
        
        # サーバー接続確認
        if not self.test_api_connection():
            return
        
        # タスクリセット
        self.reset_tasks()
        
        # 各ステップをテスト
        results = []
        for step_id in ["step1", "step2", "step3", "step4", "step5", "step6", "step7"]:
            result = self.test_step_progression(step_id)
            results.append(result)
            time.sleep(3)  # ステップ間の待機
        
        # 結果サマリー
        self._print_test_summary(results)
    
    def _print_test_summary(self, results: list):
        """テスト結果のサマリーを表示"""
        print("\n📊 === テスト結果サマリー ===")
        
        for result in results:
            step = result["step"]
            incomplete_success = result["incomplete_test"].get("success", False)
            complete_success = result["complete_test"].get("success", False)
            
            status = "✅" if incomplete_success and complete_success else "❌"
            print(f"{status} {step}: 未完了テスト={incomplete_success}, 完了テスト={complete_success}")
        
        success_count = sum(1 for r in results 
                          if r["incomplete_test"].get("success") and r["complete_test"].get("success"))
        print(f"\n🎯 成功率: {success_count}/{len(results)} ({success_count/len(results)*100:.1f}%)")

if __name__ == "__main__":
    tester = TaskProgressionTester()
    tester.run_full_progression_test() 