# bowling-lane-maintenance-system

ボウリング場のレーン設備・貸出用品(シューズ・ボール)のメンテナンス管理を行うAPIシステムです。
FastAPI + PostgreSQL + Docker で構築し、AWS EC2 上で稼働させています。第三弾(店舗管理システム)・第四弾(会員のマイギア管理)とAPI連携しています。

## プロジェクトの位置づけ

このリポジトリは、スポーツボウリング場運営システム構想における「第三弾拡張①(オイル抜きリマインド/メンテナンス管理)」に相当します。既存のシステム群(第一〜五弾)はSQLiteベースで構築されていますが、本プロジェクトはPostgreSQL・Docker・AWSという新しい技術スタックへの挑戦を目的として、あえて独立したリポジトリ・別データベースとして開発しました。

技術スタックが異なるため無理に統合はせず、**API連携**という形で第三弾・第四弾とつなぐ構成にしています(詳細は「他システムとの連携」を参照)。

## 技術スタック

- **バックエンド**: FastAPI (Python)
- **データベース**: PostgreSQL 16
- **ORM / マイグレーション**: SQLAlchemy, Alembic
- **コンテナ**: Docker, Docker Compose
- **インフラ**: AWS EC2 (Ubuntu 24.04 LTS)

FastAPIは既存プロジェクト(第一〜五弾)で使い慣れていたため継続採用し、PostgreSQL・Docker・AWSの3つを新規に習得する形で技術スタックを組みました。

## アーキテクチャ

管理対象を「現在の状態を持つマスタ」と「状態変化の履歴」に分けて設計しています。

- **lanes**: レーン設備(既存のレーンテーブルを流用)
- **rental_items**: 貸出用品(シューズ・ボール)のマスタ。現在の状態(在庫中/貸出中/点検中/修理中/使用停止/廃棄)を保持
- **maintenance_log**: レーン・貸出用品・会員のマイギアを問わない共通の整備記録。対象の種別・整備区分・対応状況・業者情報・費用などを記録

`rental_items` の削除は物理削除ではなく、`status` を「廃棄」に変更する論理削除方式を採用し、廃棄履歴を追跡できるようにしています。

`maintenance_log` はPATCH(全項目修正可能)とDELETE(物理削除)の両方に対応し、記録の訂正と誤登録の取り消しを使い分けられるようにしています。

## 他システムとの連携

### 第三弾(店舗管理システム)との連携

第三弾側でレーンのステータスが「故障中」に更新されると、拡張①の `maintenance_log` に整備記録が自動登録されます。

- 故障中でなかったレーンが**新たに**故障中になったときだけ登録します(同じ故障状態での再更新では重複登録しません)
- 拡張①が停止していても、第三弾側の処理は止まらない設計です(例外を握って本編の処理を継続)
- 第三弾側からは、レーンごとのメンテナンス状況を取得することもできます

### 第四弾(会員のマイギア管理)との連携

双方向で連携しています。

- **第四弾 → 拡張①**: 会員が第四弾の `POST /api/v1/gears/{gear_id}/maintenance/request` で整備を依頼すると、第四弾が拡張①の `POST /maintenance_log` を呼び出し(`X-API-Key` ヘッダー付き)、会員のマイギア(`target_type: member_gear`)を対象にした「未対応」の整備記録を作成
  - 記録の内容: 整備種別は `clean`、整備区分は「日常」、依頼日は当日、備考は「会員依頼: ギア名」
  - 会員ログインが必須で、依頼できるのは自分のマイギアのみです(他人のギアは404)
  - 第四弾側の設定は、第四弾の `.env` の `MAINTENANCE_API_URL` / `MAINTENANCE_API_KEY` です(URL未設定なら送信をスキップ)
  - 拡張①が停止していても、第四弾側の処理は止まりません(タイムアウト5秒、再送なし)
- **拡張① → 第四弾**: 会員のマイギアを対象にした整備記録のステータスが「完了」に更新されると、第四弾の `POST /api/v1/gears/{gear_id}/maintenance/complete` を呼び出し(`X-API-Key` ヘッダー付き)、会員のマイギアのメンテナンス履歴に反映
  - 通知は「完了」への**初回更新時のみ**です(すでに完了の記録を再更新しても重複しません)
  - レーン・貸出用品の整備完了では通知しません(対象が会員のマイギアのときだけ)
  - 通知先URLが未設定の場合は通知をスキップします。第四弾が停止していても、拡張①側の処理は止まりません(タイムアウト5秒、再送なし)
  - 第四弾側はAPIキー認証で受け付け(会員ログインは不要)、完了時点のゲーム数とともにメンテナンス履歴(オイル抜きリマインドの基準)を登録します

### 認証

書き込み系エンドポイント(POST / PATCH / DELETE)は、`X-API-Key` ヘッダーによるAPIキー認証を必須にしています。GET系は認証なしです。

- キーなし、または誤ったキー → 401
- 正しいキー → 通常どおり処理

APIキーは `.env` で管理し、リポジトリには含めていません。

## セットアップ(ローカル)

```
git clone https://github.com/Junko-Takahashi-Cloud/bowling-lane-maintenance-system.git
cd bowling-lane-maintenance-system
```

`.env` ファイルを作成し、以下を設定してください(このファイルはgit管理対象外です):

```
POSTGRES_USER=maintenance_user
POSTGRES_PASSWORD=maintenance_pass
POSTGRES_DB=maintenance_db
DATABASE_URL=postgresql://maintenance_user:maintenance_pass@db:5432/maintenance_db
API_KEY=your-api-key
# 第四弾への完了通知(任意。URL未設定なら通知しない)
MEMBER_GEAR_CALLBACK_URL=http://第四弾のホスト:ポート
MEMBER_GEAR_CALLBACK_API_KEY=第四弾側で受け付けるAPIキー
```

コンテナを起動:

```
docker compose up --build -d
```

マイグレーションを適用:

```
docker compose exec web alembic upgrade head
```

`http://localhost:8000/docs` でAPIドキュメント(Swagger UI)にアクセスできます。

## APIエンドポイント

書き込み系(POST / PATCH / DELETE)は `X-API-Key` ヘッダーが必要です。

### rental_items(貸出用品)

| メソッド | パス | 説明 | 認証 |
| ------ | ------------------------- | ----------------------------- | ---- |
| POST | /rental_items | 新規登録 | 必要 |
| GET | /rental_items | 一覧取得(status・item_typeで絞り込み可) | 不要 |
| GET | /rental_items/{item_id} | 詳細取得 | 不要 |
| PATCH | /rental_items/{item_id} | 更新 | 必要 |
| DELETE | /rental_items/{item_id} | 論理削除(statusを「廃棄」に変更) | 必要 |

### maintenance_log(整備記録)

| メソッド | パス | 説明 | 認証 |
| ------ | --------------------------- | ------------------------------------------- | ---- |
| POST | /maintenance_log | 整備記録の登録 | 必要 |
| GET | /maintenance_log | 一覧取得(target_type・target_id・statusで絞り込み可) | 不要 |
| GET | /maintenance_log/{log_id} | 詳細取得 | 不要 |
| PATCH | /maintenance_log/{log_id} | 修正(全項目) | 必要 |
| DELETE | /maintenance_log/{log_id} | 物理削除(誤登録の取り消し用) | 必要 |

## MVPの設計方針

複数のAI(ChatGPT・Claude・Groq・Gemini)による合議を経て、以下の方針でスコープを絞り込みました。

**MVPに入れたもの**

- 対象の状態(利用可否)と整備履歴の役割分離
- 修理の進行ステータス(店舗対応/業者対応の区別を含む)
- 次回整備予定・周期管理(軽量版、専用テーブルなし)
- 実施者の記録

**MVP後に追加したもの**

- 書き込み系エンドポイントのAPIキー認証
- 第三弾(店舗管理システム)とのAPI連携
- 第四弾(会員のマイギア管理)との双方向API連携

**見送ったもの**

- 消耗品在庫(オイル・洗剤等)の本格的な在庫管理
- 法定点検の本格実装(整備区分として持つのみ)
- 費用集計・承認フロー・使用頻度データ・モバイル連携

## デプロイ

AWS EC2(t3.micro, Ubuntu 24.04 LTS)上でDocker Composeを使って稼働しています。本番起動時は開発用の `--reload` オプションを外し、`.env` でDB認証情報とAPIキーをコードから分離しています。デプロイはGitHubからの `git pull` → `docker compose up -d --build` で更新する運用です。

## 今後の展望

- フロントエンド(現状はAPIのみ)
- 消耗品在庫管理の本格実装
- 法定点検の詳細管理
