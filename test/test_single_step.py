#!/usr/bin/env python3
"""
Unity Task Management - 単一ステップテスト
指定したステップのみをテストするデバッグ用スクリプト
"""

import requests
import json
import sys
import os

# プロジェクトルートを追加
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# test_tasks_progressionを直接インポート
from test_tasks_progression import TaskProgressionTester

def test_single_step(step_id: str):
    """指定されたステップのみをテスト"""
    
    if step_id not in [f"step{i}" for i in range(1, 8)]:
        print(f"❌ 無効なステップID: {step_id}")
        print("   有効なステップ: step1, step2, step3, step4, step5, step6, step7")
        return
    
    tester = TaskProgressionTester()
    
    # サーバー接続確認
    if not tester.test_api_connection():
        return
    
    # 単一ステップテスト実行
    result = tester.test_step_progression(step_id)
    
    # 詳細結果表示
    print(f"\n📊 === {step_id.upper()} 詳細結果 ===")
    
    print("\n🔍 未完了テスト結果:")
    incomplete = result["incomplete_test"]
    print(f"   成功: {incomplete.get('success', False)}")
    if incomplete.get('success'):
        data = incomplete.get('data', {})
        print(f"   アクション: {data.get('action')}")
        print(f"   タスクID: {data.get('task_id')}")
    else:
        print(f"   エラー: {incomplete.get('error')}")
    
    print("\n✅ 完了テスト結果:")
    complete = result["complete_test"]
    print(f"   成功: {complete.get('success', False)}")
    if complete.get('success'):
        data = complete.get('data', {})
        print(f"   アクション: {data.get('action')}")
        print(f"   タスクID: {data.get('task_id')}")
        if data.get('next_task'):
            next_task = data['next_task']
            print(f"   次のタスク: {next_task['task']['description']}")
    else:
        print(f"   エラー: {complete.get('error')}")

def interactive_test():
    """インタラクティブテストモード"""
    tester = TaskProgressionTester()
    
    print("🎮 === Unity Task Management インタラクティブテスト ===")
    print("使用方法:")
    print("  - ステップ番号を入力してテスト (1-7)")
    print("  - 'all' で全ステップテスト")
    print("  - 'quit' で終了")
    
    while True:
        user_input = input("\n⚡ コマンドを入力 (1-7/all/quit): ").strip().lower()
        
        if user_input == 'quit':
            print("👋 テスト終了")
            break
        elif user_input == 'all':
            tester.run_full_progression_test()
        elif user_input in ['1', '2', '3', '4', '5', '6', '7']:
            step_id = f"step{user_input}"
            test_single_step(step_id)
        else:
            print("❌ 無効な入力です。1-7, all, quit のいずれかを入力してください。")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # コマンドライン引数でステップ指定
        step_arg = sys.argv[1].lower()
        if step_arg.startswith('step'):
            test_single_step(step_arg)
        elif step_arg.isdigit():
            test_single_step(f"step{step_arg}")
        else:
            print("使用方法: python test/test_single_step.py step1")
            print("         python test/test_single_step.py 1")
    else:
        # インタラクティブモード
        interactive_test() 