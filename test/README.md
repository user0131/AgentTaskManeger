# Unity Task Management テスト

Unity互換のFlask+Reactシステムのタスク進行テストツール

## 🎯 **テスト概要**

7つのステップからなる「研究室Zoom会議準備タスク」を段階的にテストし、LLMの判定精度を確認します。

### **テストステップ**
1. **Step1**: 中会議室のカギを開ける
2. **Step2**: MacBookと充電器とUSBポートを用意する
3. **Step3**: みんながPCを充電する用の延長ケーブルをつなぐ
4. **Step4**: Macで研究室Zoomにつなぐ
5. **Step5**: Owlカメラとyamahaのマイクとスクリーンつける
6. **Step6**: こいつらをUSBポート介してUSBとHDMIでMacにつなぐ
7. **Step7**: Zoomのカメラ＆マイクON

## 🛠 **テストファイル**

### `test_tasks_progression.py`
全7ステップを自動的に段階的テストする包括テストツール

```bash
# 全ステップテスト実行
cd /path/to/project
python test/test_tasks_progression.py
```

### `test_single_step.py`
指定ステップのみをテストするデバッグツール

```bash
# 単一ステップテスト
python test/test_single_step.py step1    # step1をテスト
python test/test_single_step.py 3        # step3をテスト

# インタラクティブモード
python test/test_single_step.py
```

## 🎮 **使用方法**

### **1. サーバー起動**
```bash
cd src
python app.py
```

### **2. 全ステップテスト実行**
```bash
python test/test_tasks_progression.py
```

### **3. 個別ステップテスト**
```bash
python test/test_single_step.py
```

## 📊 **テスト内容**

各ステップで以下の2つのシナリオをテスト：

### **未完了状態テスト**
- プレイヤーがタスクを開始したが完了していない状況
- 期待結果: `"keep"` (継続判定)

### **完了状態テスト**
- プレイヤーがタスクを正常に完了した状況
- 期待結果: `"step2"`, `"step3"` 等 (次ステップ判定)

## 📋 **テストシナリオ例**

### Step1テスト

**未完了状態:**
```json
{
  "current_task": "中会議室のカギを開ける",
  "player_status": "プレイヤーは中会議室の前に立っている。鍵を探している。",
  "surroundings": "中会議室のドア、鍵穴、廊下、他の部屋のドアが見える"
}
```

**完了状態:**
```json
{
  "current_task": "中会議室のカギを開ける",
  "player_status": "プレイヤーは鍵を使ってドアを開けた。中会議室に入った。",
  "surroundings": "開いた中会議室のドア、室内のテーブル、椅子、ホワイトボードが見える"
}
```

## 🔧 **要件**

- Python 3.7+
- requests ライブラリ
- Flask サーバーが localhost:5000 で起動中

## 📈 **テスト結果**

テスト実行後、以下の情報が表示されます：
- 各ステップの判定結果
- 未完了/完了テストの成功/失敗
- 全体の成功率
- エラー詳細（ある場合）

## 🚨 **注意事項**

1. **サーバー起動確認**: Flask サーバーが起動していることを確認
2. **API接続**: `localhost:5000` への接続が可能であることを確認
3. **OpenAI API**: config.pyでAPIキーが設定されていることを確認
4. **レスポンス時間**: LLM処理のため、各テストに2-5秒かかります
