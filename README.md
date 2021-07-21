# 概要

Qin ToDo のサンプル

## 使用技術

- FastAPI
- GraphQL
- Docker

### インストールしているパッケージ一覧

<!-- linter,formatterのインストール -->

- flake8
- yapf

<!-- ライブラリのインストール -->

- fastapi
- uvicorn
- SQLAlchemy
- graphene
- graphene-sqlalchemy

<!-- 周辺ツール -->

- passlib[bcrypt]
- python-jose
- python-multipart
- alembic
- python-decouple
- psycopg2-binary

<!-- ダッシュボードの導入 -->

- fastapi-admin

## セットアップ

```shell
pipenv --python 3.9
```

<!-- Pipfile に書いてあるパッケージをインストールする -->

```shell
pipenv install --dev
```

<!-- Pillow, graphene-file-upload -->

```shell
pipenv install yapf flake8 --dev
```

```shell
pipenv shell
```

```shell
docker-compose up
```

```shell
docker-compose exec app bash
```

```shell
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

```shell
openssl rand -hex 32
# SECRET_KEYを取得
```

```/.env
POSTGRES_USER=xxx
POSTGRES_PASSWORD=xxx
POSTGRES_SERVER=yy
POSTGRES_PORT=0000
POSTGRES_DB=zzzz

SECRET_KEY=xxxx
ALGORITHM=xxxx
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

## DB の初期化について

初期化用の python ファイルなどを用意する必要がある。

## 各処理について

非同期処理にできるものは対応する。
try-except のエラーハンドリングをする。

### マジックリンクでの本人確認について

JWT によるアクセストークンを発行し、https://frontend-name.domain/auth/token=?<token>などとしてメールを送り、フロントエンド側で Cookie に JWT をセットし自分のユーザーモデルの本人確認フラグを True に更新する？

もしメールを送信したけど、トークンの時間切れや本人確認がされなかったときは、本人確認フラグを更新せずに保存はしておく。
