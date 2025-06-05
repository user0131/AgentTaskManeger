# Unity + Flask NPCタスク実行システム 開発計画

## 【全体概要】
- **目的**: 研究室でのZoom会議準備タスクをNPCが自動実行するシステム
- **構成**: Flask（バックエンド） + Unity（フロントエンド）
- **特徴**: 3Dデスクトップアプリ、Immersal研究室モデル使用
- **NPC**: 1体のキャラクターが7つのタスクを順次実行

---

## 【フェーズ1: 環境準備】

### A. Immersalによる研究室3Dモデル作成
```
1. Immersal Mapperアプリをダウンロード（iOS/Android）
2. 研究室で約500枚の写真撮影
   - 様々な角度から撮影
   - タスク実行場所を重点的に撮影
   - 机、棚、機器等の詳細も撮影
3. Immersal Cloudで3D再構築処理（数時間〜1日）
4. Developer Portalから.glbファイルをダウンロード
5. 必要に応じて追加の.plyファイルも取得
```

### B. NPCキャラクター準備
```
1. Mixamo（mixamo.com）でアカウント作成（無料）
2. 適切なキャラクターを選択
   - ビジネス系の見た目推奨
   - 研究室にふさわしい外観
3. 必要なアニメーションをダウンロード：
   - Idle（待機）
   - Walk（歩行）
   - Sitting（座る）
   - Standing Up（立つ）
   - Typing（タイピング）
   - Pickup（物を取る）
   - Waving（手を振る）
4. FBXファイル形式でダウンロード
5. Unityにインポートしてテスト
```

---

## 【フェーズ2: Unity基本実装】

### A. プロジェクトセットアップ
```
1. Unity 2022.3 LTS で新規3Dプロジェクト作成
2. 必要パッケージのインポート：
   - AI Navigation (NavMesh Components)
   - Input System
   - TextMeshPro
   - 必要に応じてNewtonsoft JSON
3. プロジェクト構造作成：
   - Scripts/
   - Prefabs/
   - Materials/
   - Animations/
```

### B. 研究室環境構築
```
1. Immersalの.glbファイルをUnityにインポート
2. 研究室モデルをシーンに配置
3. スケール・位置調整
4. NavMesh設定：
   - モデルをNavMesh Staticに設定
   - Walkable領域の確認
   - Navigation window → Bake実行
   - Agent設定（Radius: 0.5, Height: 2.0）
5. 照明設定とカメラ配置
```

### C. NPCキャラクター配置
```
1. Mixamoキャラクターをシーンに配置
2. 必要コンポーネント追加：
   - NavMeshAgent
   - Animator
   - Collider（Capsule）
   - Rigidbody（Kinematic）
3. Animator Controllerの作成
4. 基本移動テスト実行
   - シンプルなSetDestination()テスト
   - アニメーション動作確認
```

---

## 【フェーズ3: タスクシステム実装】

### A. タスク地点定義
```
7つのタスク地点を研究室内で特定・配置：

1. タスク1: 会議室の鍵保管場所
   - 鍵がある棚・引き出し付近
   
2. タスク2: MacBook設置机
   - 机の上、MacBookを置く位置
   
3. タスク3: 延長ケーブル置き場
   - ケーブル類が保管されている場所
   
4. タスク4: Zoom接続場所
   - MacBookでZoom操作する机の位置
   
5. タスク5: AV機器操作場所
   - プロジェクター、スピーカー操作位置
   
6. タスク6: USB/HDMI接続場所
   - ケーブル接続作業を行う位置
   
7. タスク7: カメラ・マイク設定場所
   - 最終確認を行う位置

各地点の設定：
- 空のGameObjectを配置
- TaskLocationコンポーネント追加
- ID、名前、説明を設定
- Gizmosで視覚化
```

### B. Flask API通信実装
```
1. APIManagerクラス作成
2. UnityWebRequestを使用してHTTP通信
3. Flask APIエンドポイントとの通信：
   - GET /api/current-task
   - POST /api/environment-update  
   - POST /api/get-instruction
   - POST /api/force-complete-task
   - POST /api/reset-tasks
4. JSON シリアライゼーション処理
5. エラーハンドリング・リトライ機能
6. 通信状態の可視化
```

---

## 【フェーズ4: NPC自動実行システム】

### A. メインタスクマネージャー実装
```csharp
NPCTaskBot.cs の主要機能:

1. タスクループ管理
   - 現在のタスクID追跡
   - 次のタスクへの遷移
   
2. NavMeshAgentによる自動移動
   - SetDestination()による移動
   - 到着判定
   - 移動速度調整
   
3. アニメーション制御
   - 移動時：Walk
   - 待機時：Idle  
   - 作業時：対応する作業アニメーション
   
4. Flask APIとの連携
   - タスク情報取得
   - 環境データ送信
   - 完了報告
   
5. タスク完了判定
   - LLMからの指示取得
   - 環境状況の確認
   - 自動/手動完了切り替え
```

### B. 各タスクの動作定義
```
タスク実行フロー:
1. Flask APIから現在タスク取得
2. 対応する地点への移動開始
3. 移動完了まで待機
4. 作業アニメーション実行
5. 環境データの送信
6. LLMによる完了判定
7. 次タスクへの遷移

各タスクの具体的動作:
- タスク1: 歩行 → しゃがむ → 物を取る動作
- タスク2: 歩行 → 机に向かう → 設置動作
- タスク3: 歩行 → 探す動作 → 取る動作
- タスク4: 歩行 → 座る → タイピング動作
- タスク5: 歩行 → 機器操作動作
- タスク6: 歩行 → ケーブル接続動作
- タスク7: 歩行 → 確認動作 → 手を振る
```

---

## 【フェーズ5: UI・デバッグ機能】

### A. ユーザーインターフェース
```
Canvas作成（Screen Space Overlay）:

1. 現在タスク表示パネル
   - タスクID、名前
   - 進行状況バー
   - 現在の動作状態
   
2. デバッグ情報パネル
   - Flask API接続状態
   - 現在位置情報
   - NavMesh状態
   - アニメーション状態
   
3. 手動操作ボタン
   - タスク強制完了
   - 次のタスクへスキップ
   - 全タスクリセット
   - 一時停止/再開
   
4. ログ表示エリア
   - API通信ログ
   - エラーメッセージ
   - タスク実行ログ
```

### B. カメラシステム
```
複数カメラ対応:

1. フリールックカメラ
   - マウス操作で自由視点
   - WASD移動対応
   
2. NPCフォローカメラ  
   - NPCを自動追跡
   - 適度な距離を維持
   
3. 固定視点カメラ
   - 研究室全体を見渡せる位置
   - タスク地点を俯瞰
   
4. タスク地点カメラ
   - 各タスク実行時の詳細ビュー
   
カメラ切り替え:
- 数字キー1-4で切り替え
- UIボタンでの切り替え
- 自動切り替えオプション
```

---

## 【フェーズ6: 統合テスト・調整】

### A. システム統合
```
1. Flask サーバー起動確認
   - src/app.py の実行
   - API エンドポイント動作確認
   
2. Unity-Flask通信テスト
   - 各APIの応答確認
   - エラーレスポンス処理
   - タイムアウト処理
   
3. 全タスク通し実行テスト
   - 1-7番タスクの連続実行
   - 各段階での動作確認
   - 異常終了時の復旧
   
4. エラー状況での動作確認
   - ネットワーク切断時
   - Flask サーバー停止時
   - 不正なレスポンス時
```

### B. 最終調整
```
1. NPCの移動調整
   - 移動速度の最適化
   - 回転速度の調整
   - 障害物回避の確認
   
2. アニメーション同期調整
   - 移動とアニメーションの同期
   - 状態遷移のスムーズ化
   - ループアニメーションの調整
   
3. UI表示改善
   - フォントサイズ調整
   - 色彩・レイアウト改善
   - 情報の見やすさ向上
   
4. デバッグ機能拡充
   - より詳細なログ出力
   - パフォーマンス監視
   - 設定保存・読み込み
```

---

## 【実装優先順序】

```
フェーズ1: 環境準備（1-2週間）
├── Immersal撮影・3D生成
└── Mixamoキャラクター準備

フェーズ2: Unity基本（1週間）  
├── プロジェクト作成
├── 3Dモデルインポート
└── NPC配置・移動テスト

フェーズ3: タスクシステム（1-2週間）
├── タスク地点定義
└── Flask API通信

フェーズ4: 自動実行（2-3週間）
├── NPCタスクボット実装
└── 各タスク動作定義

フェーズ5: UI・カメラ（1週間）
├── インターフェース実装
└── カメラシステム

フェーズ6: 統合・調整（1週間）
├── システム統合テスト
└── 最終調整・ポリッシュ

総開発期間目安: 7-10週間
```

---

## 【重要なファイル構成】

### Unity側（新規作成）
```
Scripts/
├── NPCTaskBot.cs（メインNPC制御）
├── TaskLocationManager.cs（タスク地点管理）
├── APIManager.cs（Flask通信）
├── UIManager.cs（UI制御）
├── CameraController.cs（カメラ制御）
├── TaskLocation.cs（地点データクラス）
├── TaskData.cs（タスクデータクラス）
└── DebugManager.cs（デバッグ機能）

Prefabs/
├── NPC_Character.prefab
├── TaskLocation.prefab
├── UI_Canvas.prefab
└── CameraRig.prefab

Scenes/
├── MainScene.unity
└── TestScene.unity
```

### Flask側（既存）
```
src/
├── app.py（メインアプリケーション）
├── config.py（設定管理）
├── tasks/tasks.json（タスク定義）
└── utils/openai_utils.py（LLM統合）
```

---

## 【必要なソフトウェア・アセット】

### 必須
- Unity 2022.3 LTS
- Immersal Mapper アプリ
- Mixamo アカウント（無料）
- Python 3.8+（Flask実行用）

### 推奨
- Blender（3Dモデル調整用）
- Visual Studio Code
- Git（バージョン管理）

### Unity Assets（無料）
- AI Navigation package
- Input System
- TextMeshPro
- ProBuilder（レベルデザイン補助）

---

## 【次のアクション】

**最初に取り組むべき項目:**

1. **Immersal撮影の実行**
   - 研究室で500枚程度の写真撮影
   - 各タスク地点を重点的に撮影

2. **Mixamoキャラクター準備**
   - アカウント作成
   - キャラクター・アニメーション選択
   - Unity対応形式でダウンロード

3. **Unity基本プロジェクト作成**
   - 新規プロジェクト作成
   - 必要パッケージインストール
   - フォルダ構成整理

**どの項目から開始しますか？** 