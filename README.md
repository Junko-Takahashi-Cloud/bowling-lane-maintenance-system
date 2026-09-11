# bowling-lane-maintenance-system

ボウリング場のレーン設備・貸出用品(シューズ・ボール)のメンテナンス管理を行うAPIシステムです。

## プロジェクトの位置づけ

このリポジトリは、スポーツボウリング場運営システム構想における「第三弾拡張①(オイル抜きリマインド/メンテナンス管理)」に相当します。既存のシステム群(第一〜五弾)はSQLiteベースで構築されていますが、本プロジェクトはPostgreSQL・Docker・AWSという新しい技術スタックへの挑戦を目的として、あえて独立したリポジトリ・別データベースとして開発しました。

将来的には、本来の構想上の位置づけである第三弾拡張①として、API連携などの形で本編システムに組み込むことも視野に入れています。

## 技術スタック

- **バックエンド**: FastAPI (Python)
- **データベース**: PostgreSQL 16
- **ORM / マイグレーション**: SQLAlchemy, Alembic
- **コンテナ**: Docker, Docker Compose
- **インフラ**: AWS EC2 (Ubuntu 24.04 LTS)

FastAPIは既存プロジェクト(第一〜五弾)で使い慣れていたため継続採用し、PostgreSQL・Docker・AWSの3つを新規に習得する形で技術スタックを組みました。

## アーキテクチャ

管理対象を「現在の状態を持つマスタ」と「状態変化の履歴」に分けて設計しています。

- **rental_items**: 貸出用品(シューズ・ボール)のマスタ。現在の状態(在庫中/貸出中/点検中/修理中/使用停止/廃棄)を保持
- **maintenance_log**: レーン・貸出用品を問わない共通の整備記録。対象の種別・整備区分・対応状況・業者情報・費用などを記録

`rental_items` の削除は物理削除ではなく、`status` を「廃棄」に変更する論理削除方式を採用し、廃棄履歴を追跡できるようにしています。

`maintenance_log` はPATCH(全項目修正可能)とDELETE(物理削除)の両方に対応し、記録の訂正と誤登録の取り消しを使い分けられるようにしています。

## セットアップ(ローカル)

```bash
git clone https://github.com/Junko-Takahashi-Cloud/bowling-lane-maintenance-system.git
cd bowling-lane-maintenance-system
```

`.env` ファイルを作成し、以下を設定してください(このファイルはgit管理対象外です):

```
POSTGRES_USER=maintenance_user
POSTGRES_PASSWORD=maintenance_pass
POSTGRES_DB=maintenance_db
DATABASE_URL=postgresql://maintenance_user:maintenance_pass@db:5432/maintenance_db
```

コンテナを起動:

```bash
docker compose up --build -d
```

マイグレーションを適用:

```bash
docker compose exec web alembic upgrade head
```

`http://localhost:8000/docs` でAPIドキュメント(Swagger UI)にアクセスできます。

## APIエンドポイント

### rental_items(貸出用品)

| メソッド | パス | 説明 |
|---|---|---|
| POST | /rental_items | 新規登録 |
| GET | /rental_items | 一覧取得(status・item_typeで絞り込み可) |
| GET | /rental_items/{item_id} | 詳細取得 |
| PATCH | /rental_items/{item_id} | 更新 |
| DELETE | /rental_items/{item_id} | 論理削除(statusを「廃棄」に変更) |

### maintenance_log(整備記録)

| メソッド | パス | 説明 |
|---|---|---|
| POST | /maintenance_log | 整備記録の登録 |
| GET | /maintenance_log | 一覧取得(target_type・statusで絞り込み可) |
| GET | /maintenance_log/{log_id} | 詳細取得 |
| PATCH | /maintenance_log/{log_id} | 修正(全項目) |
| DELETE | /maintenance_log/{log_id} | 物理削除(誤登録の取り消し用) |

## MVPの設計方針

複数のAI(ChatGPT・Claude・Groq・Gemini)による合議を経て、以下の方針でスコープを絞り込みました。

**今回入れたもの**
- 対象の状態(利用可否)と整備履歴の役割分離
- 修理の進行ステータス(店舗対応/業者対応の区別を含む)
- 次回整備予定・周期管理(軽量版、専用テーブルなし)
- 実施者の記録

**MVPでは見送ったもの**
- 消耗品在庫(オイル・洗剤等)の本格的な在庫管理
- 法定点検の本格実装(整備区分として持つのみ)
- 第四弾(会員のマイギア管理)との接続実装
- 費用集計・承認フロー・使用頻度データ・モバイル連携

## デプロイ

AWS EC2(t3.micro, Ubuntu 24.04 LTS)上でDocker Composeを使って稼働しています。本番起動時は開発用の `--reload` オプションを外し、`.env` でDB認証情報をコードから分離しています。

## 今後の展望

- 第三弾(店舗管理システム)とのAPI連携
- 第四弾(会員のマイギア管理)との接続実装
- 消耗品在庫管理の本格実装
- 法定点検の詳細管理
