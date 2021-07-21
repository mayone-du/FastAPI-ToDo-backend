import bcrypt
from jose import jwt
from models.custom_user import CustomUserModel
from passlib.context import CryptContext
from schemas.custom_user import CustomUserNode
from settings.envs import ALGORITHM, SECRET_KEY

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
def get_current_custom_user(info):
    try:
        # headersのauthorizationからjwtを取得
        headers = dict(info.context['request']['headers'])
        # Bearer の文字列を半角空白含めて削除（計7文字）
        token = headers[b'authorization'].decode()[7:]
        # トークンの内容を取得
        payload: dict = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        ulid = payload.get('ulid')
        # ulidに紐づくユーザーを返却
        return CustomUserNode.get_query(info).filter(
            CustomUserModel.ulid == ulid).first()
    except:
        # TODO: エラーハンドリングの実装
        raise
