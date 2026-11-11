# チームの連絡板（team-board）

チームへの連絡を書き込むと、一覧に表示される Web アプリです。
「コンテナ入門 〜Docker で作る・動かす・配る〜」のハンズオンで、**配属先のチームのプロジェクトの役**として使います。

## 構成

| サービス | 中身 |
|---|---|
| `web` | アプリ本体（Python の FastAPI）。この Dockerfile から作る |
| `db` | データベース（PostgreSQL 18） |
| `cache` | 表示した回数を数える置き場（Redis 8） |

## 起動のしかた

1. 設定の見本 `.env.example` を写して `.env` を作ります。

   ```
   cp .env.example .env
   ```

2. `.env` を開き、`DB_PASSWORD` と `ADMIN_TOKEN` に値を書き入れます（練習用の値でかまいません）。
3. まとめて起動します。

   ```
   docker compose up -d
   ```

4. ブラウザで `http://localhost:8000` を開きます（Codespaces では、ポートのタブから開きます）。
   ポート番号を変えたときは、`.env` の `WEB_PORT` の番号で開きます。

管理画面は `/admin?token=〈ADMIN_TOKEN の値〉` です。

## 止め方

```
docker compose down
```

データ（連絡の書き込み）まで消すときは `docker compose down -v` です。
