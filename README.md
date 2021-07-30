# 概要

FastAPI と GraphQL の練習用
※2021/07/30 GraphQL のサポートが少なくてきついから一回クローズ。ファイルのアップロード周りとかが充実してくれればありかも。

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

## 認証フローメモ

1. email, password で新規登録
2. 登録したメールアドレスに フロントの URL のクエリパラメーターに token をのせた形式で JWT の有効期限付きでメールを送信
3. 1. 有効期限内にクリック
   2. トークン更新用のフロントのエンドポイントを用意し、JWT をフロント側で保存し、JWT を使って本人確認の更新をする
   3. 更新が出来たらリフレッシュトークンも作成し、フロントの Cookie と DB へ保存する
4. 1. 有効期限内にクリックしなかった場合
   2. ログイン画面へ
   3. ユーザー情報自体は登録されているため、email と password のセットが一致したら再度メールを送る
5. 1. リフレッシュトークンの有効期限が切れた場合
   2. email と password で再ログイン（2 種類のトークンを発行）

## 具体的な認証時の流れ

<!-- TODO: ↓の流れをまとめたほうが良いかも？ 関数自体はわけても、GraphQLのMutation自体は分ける必要ない。 -->

1. CreateCustomUser でユーザーの作成
2. 1.のメールアドレスに、SendMagicLink でマジックリンク付きメールを送信
3. マジックリンクが届いてクリックすると、フロント側でトークンを設定後に UpdateVerifyCustomUser でフラグを True にする
4.

### 改善案

1. ユーザー作成とマジックリンクの送信を一つの Mutation で実行
2. マジックリンクをクリックしたらフロント側でトークンをヘッダーに付与し、UpdateVerifyCustomUser でフラグを更新し、同時にリフレッシュトークンも作成してフロントに返す。
3. フロントはかえってきたリフレッシュトークンも保存し、準備完了。
4. アクセストークンが切れたら UpdateTokens へリフレッシュトークンを投げ、どちらも更新する。
5. ログイン自体無効になったら、ReAuthentication でトークンを 2 種類発行する。

### 新規アイデア

初回登録時のメールアドレスとパスワード入力では DB に登録せず、メアドとパスワードを JWT にのせ、リンクをクリックしたら登録？
フロント側でアクセスしたときに登録し、二回目以降はリダイレクトやエラーにする？

## TODO:

- DB に保存する DateTime 型のタイムゾーンなどの確認
- 各エラーハンドリング
- 認証フローの確認・テスト
- パスワードを忘れた場合にメールを送り、再設定できるようにする？
- XSS 等の対策のため、なるべくフロント側からのリクエストは少なくし、バックエンド側でエラーハンドリングやバリデーションを厳格にする
