FROM python:3.9.6-slim

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

RUN \
  mkdir src && \
  # pip自体のアップグレード
  pip install --upgrade pip && \
  pip install \
  # linter,formatterのインストール
  flake8 \
  yapf \
  # ライブラリのインストール
  fastapi \
  uvicorn \
  SQLAlchemy \
  graphene \
  graphene-sqlalchemy \
  # 周辺ツール
  passlib[bcrypt] \
  python-jose \
  python-multipart \
  alembic \
  python-decouple \
  psycopg2-binary \
  # ダッシュボードの導入
  fastapi-admin

WORKDIR /src