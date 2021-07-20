import bcrypt
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# パスワードをハッシュ化
def hash_password(password: str):
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    # DBかドライバー側が自動でutf-8にエンコードし、二重エンコードになり無効な文字列に変換してしまうのでdocodeする
    hashed_password = hashed_password.decode('utf-8')
    return hashed_password


# プレーンテキストのパスワードとハッシュ化されたパスワードを検証
def verify_password(plain_password, hashed_password):
    return bcrypt.checkpw(plain_password.encode('utf-8'),
                          hashed_password.encode('utf-8'))
