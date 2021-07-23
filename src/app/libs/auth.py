from datetime import datetime, timedelta

import bcrypt
from database.database import db
from fastapi import BackgroundTasks, HTTPException
from fastapi_mail import FastMail, MessageSchema
from jose import jwt
from models.custom_user import CustomUserModel
from passlib.context import CryptContext
from schemas.custom_user import CustomUserNode
from settings.envs import (ACCESS_TOKEN_EXPIRE_MINUTES, ALGORITHM,
                           MAIL_CONFIGS, SECRET_KEY)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# 引数で受け取った文字列をハッシュ化する
def hash_data(data: str):
    hashed_data = bcrypt.hashpw(data.encode('utf-8'), bcrypt.gensalt())
    # DBかドライバー側が自動でutf-8にエンコードし、二重エンコードになり無効な文字列に変換してしまうのでdocodeする
    hashed_data = hashed_data.decode('utf-8')
    return hashed_data


# プレーンテキストのパスワードとハッシュ化されたパスワードを検証
def verify_hash_data(plain_data: str, hashed_data: str):
    return bcrypt.checkpw(plain_data.encode('utf-8'),
                          hashed_data.encode('utf-8'))


# Cookieのheadersのauthorizationからjwtを取得し、decodeしてpayloadのulidを取得し、そのulidと紐づくユーザーを返す
def get_current_custom_user(info) -> CustomUserModel:
    try:
        # headersのauthorizationからjwtを取得
        headers = dict(info.context['request']['headers'])
        # Bearer の文字列を半角空白含めて削除（計7文字）
        token = headers[b'authorization'].decode()[7:]
        # トークンの内容を取得
        payload: dict = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        ulid = payload.get('ulid')
        # ulidに紐づくユーザーを返却
        # TODO: token自体の検証（有効期限など）
        validate_access_token(token)
        return CustomUserNode.get_query(info).filter(
            CustomUserModel.ulid == ulid).first()
    except:
        # TODO: エラーハンドリングの実装
        raise


# アクセストークンの作成
# TODO: リファクタ もっとやることを絞って専門性をもたせる
def create_access_token(info, email: str, password: str) -> dict:
    try:
        # emailからそのユーザーのインスタンスを取得
        user = CustomUserNode.get_query(info).filter(
            CustomUserModel.email == email).first()
        # 登録済みのハッシュ化されたパスワード
        registered_password = user.password
        ulid = user.ulid
        # パスワードが一致しなかったらエラーレスポンスを返す
        if not verify_hash_data(password, registered_password):
            # TODO: エラーレスポンスの実装
            raise HTTPException(status_code=401)
        expiration_date = datetime.utcnow() + timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        # ulid、トークンタイプ、有効期限をもとにJWTを発行
        token_payload = {
            'ulid': ulid,
            # access_token or refresh_token
            'type': 'access_token',
            # 有効期限をUTCタイムスタンプ形式で設定
            'exp': expiration_date
        }
        access_token = jwt.encode(token_payload,
                                  SECRET_KEY,
                                  algorithm=ALGORITHM)
        access_token_object = {
            'access_token': access_token,
            'expiration_date': str(expiration_date)
        }
        return access_token_object
    except:
        # TODO: エラーレスポンスの実装
        raise


# TODO: tokenのpayloadについて考えたりエラーハンドリングなど
# アクセストークンを検証する。デコレーターにした方がよいかも
def validate_access_token(access_token: str):
    try:
        now = datetime.utcnow().timestamp()
        payload: dict = jwt.decode(access_token,
                                   SECRET_KEY,
                                   algorithms=[ALGORITHM])
        ulid = payload.get('ulid')
        token_type = payload.get('type')
        expiration_date = payload.get('exp')

        # ulidに紐づくユーザーがいなかったらエラー
        if db.query(CustomUserModel).filter(
                CustomUserModel.ulid == ulid).first() is None:
            raise
        # トークンタイプがaccess_tokenじゃなかったらエラー（トークンに持たせるpayloadについては要検討）
        if token_type != 'access_token':
            raise
        # 有効期限が過ぎていたらエラー処理
        if now > expiration_date:
            raise
    except:
        raise
