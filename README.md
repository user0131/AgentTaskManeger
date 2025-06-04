# Unity Task Management System with LLM

Unityの3D空間でのタスク管理システム。FlaskバックエンドでLLMと連携し、シンプルなタスク判定を行います。

## 概要

このシステムは研究室でのZoom会議準備タスクを順序立てて管理し、LLMがタスクの完了を自動判定します。

**主な機能:**
- JSON形式によるタスク管理
- OpenAI GPTによるタスク完了の自動判定  
- UnityとFlaskサーバー間の軽量HTTP通信
- シンプルな"keep"/"next_task"判定システム

## システム構成

```
Flask Backend (Python)
├── シンプルタスク判定 (SimpleTaskJudgeSystem)
├── OpenAI LLM統合 (TaskProgressAnalyzer)
└── REST API (1エンドポイント)

Unity Frontend (C#)  
├── タスク位置管理
├── プレイヤー状況送信
└── Flask通信クライアント
```

## プロジェクト構成

```
Unity Task Management System/
├── 📄 app.py                    # メインFlaskアプリ
├── 📄 config.py                 # 設定管理
├── 📁 src/
│   ├── 📄 task_manager.py       # タスク管理クラス  
│   ├── 📄 tasks.json            # タスクデータ
│   └── 📁 utils/
│       └── openai_utils.py      # LLM判定システム
├── 📄 requirements.txt          # 依存パッケージ
└── 📄 README.md                 # プロジェクト説明
```

## タスク管理システム

研究室でのZoom会議準備作業（7ステップ）：

1. **step1**: 中会議室のカギを開ける
2. **step2**: MacBookと充電器とUSBポートを用意する  
3. **step3**: みんながPCを充電する用の延長ケーブルをつなぐ
4. **step4**: Macで研究室Zoomにつなぐ
5. **step5**: Owlカメラとyamahaのマイクとスクリーンつける
6. **step6**: こいつらをUSBポート介してUSBとHDMIでMacにつなぐ
7. **step7**: Zoomのカメラ＆マイクON

## セットアップ手順

### 1. 環境構築

```bash
# Python仮想環境を作成
python -m venv .venv
source .venv/bin/activate  # macOS/Linux

# 依存パッケージをインストール
pip install -r requirements.txt
```

### 2. 環境変数設定

`.env`ファイルを作成：

```bash
# OpenAI API設定
OPENAI_API_KEY=sk-your-openai-api-key

# Flask設定
FLASK_HOST=0.0.0.0
FLASK_PORT=5000
DEBUG_MODE=true

# LLM設定
LLM_MODEL=gpt-4o-mini
LLM_TEMPERATURE=0.0
```

### 3. サーバー起動

```bash
python app.py
# サーバーが http://localhost:5000 で起動
```

## API エンドポイント

### POST `/api/environment-update`

Unity からの環境情報更新とタスク完了判定

**リクエスト:**
```json
{
  "current_task": "中会議室のカギを開ける",
  "player_status": "中会議室の前に到着、ドアを開けた",
  "surroundings": "部屋に入ることができる状態"
}
```

**レスポンス:**
```json
{
  "success": true,
  "data": {
    "action": "next",
    "task_id": "step2"
  },
  "timestamp": "2024-01-01T12:00:00.000000",
  "message": "Task judgment completed: next -> step2"
}
```

**判定ルール:**
- タスク完了 → `"action": "next", "task_id": "step2"` (次のタスクID)
- タスク未完了 → `"action": "keep", "task_id": null` (現在のタスクを継続)

## Unity側実装

### 基本的な通信例

```csharp
[System.Serializable]
public class EnvironmentData
{
    public string current_task;
    public string player_status;
    public string surroundings;
}

[System.Serializable] 
public class APIResponse
{
    public bool success;
    public TaskJudgment data;
    public string timestamp;
    public string message;
}

[System.Serializable]
public class TaskJudgment
{
    public string action;    // "keep" または "next"
    public string task_id;   // "step2", "step3" など
}

// サーバーへ状況を送信
public IEnumerator UpdateEnvironment(string task, string status, string surroundings = "")
{
    var data = new EnvironmentData
    {
        current_task = task,
        player_status = status,
        surroundings = surroundings
    };
    
    string json = JsonUtility.ToJson(data);
    byte[] bodyRaw = System.Text.Encoding.UTF8.GetBytes(json);
    
    using (UnityWebRequest request = new UnityWebRequest("http://localhost:5000/api/environment-update", "POST"))
    {
        request.uploadHandler = new UploadHandlerRaw(bodyRaw);
        request.downloadHandler = new DownloadHandlerText();
        request.SetRequestHeader("Content-Type", "application/json");
        
        yield return request.SendWebRequest();
        
        if (request.result == UnityWebRequest.Result.Success)
        {
            APIResponse response = JsonUtility.FromJson<APIResponse>(request.downloadHandler.text);
            
            if (response.data.action == "next" && !string.IsNullOrEmpty(response.data.task_id))
            {
                // 次のタスクに進む
                LoadNextTask(response.data.task_id);
            }
            // "keep"の場合は現在のタスクを継続
        }
    }
}
```

## LLM判定システム

**SimpleTaskJudgeSystem**は以下の判定を行います：

1. **タスク分析**: 現在のタスク内容、プレイヤー状況、周囲環境を分析
2. **完了判定**: タスクの目標が達成されているかを判定
3. **シンプル応答**: "keep" または 次のタスクID を返す

**判定例:**
- 「カギを開ける」→「ドアを開けた」= 完了 → "step2"
- 「機器を用意する」→「まだ探している」= 未完了 → "keep"
- 「接続する」→「接続完了」= 完了 → "step6"

## 実行フロー

1. **Unity側**: プレイヤーの状況をサーバーに送信
2. **Flask側**: LLMがタスクの完了を判定
3. **応答**: "keep"（継続） または "step○"（次タスク）
4. **Unity側**: 判定結果に基づいてタスクを継続 or 更新

## トラブルシューティング

### よくある問題

**OpenAI APIエラー:**
```bash
# APIキーが設定されているか確認
echo $OPENAI_API_KEY
```

**サーバー起動エラー:**
```bash
# 仮想環境がアクティブか確認
which python
# 依存関係を再インストール
pip install -r requirements.txt
```

**Unity通信エラー:**
- サーバーが http://localhost:5000 で起動しているか確認
- JSONフォーマットが正しいか確認
- CORS設定が有効になっているか確認

## 設定

### config.py 主要設定

```python  
# OpenAI設定
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
LLM_MODEL = 'gpt-4o-mini'
LLM_TEMPERATURE = 0.0

# Flask設定
FLASK_HOST = '0.0.0.0'  
FLASK_PORT = 5000
DEBUG_MODE = True
```

### タスクのカスタマイズ

`src/tasks.json`を編集してタスク内容を変更できます。