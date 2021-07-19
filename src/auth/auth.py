from datetime import datetime, timedelta
from typing import Optional

import bcrypt
from app.schemas.user import UserSchema
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from settings.envs import ALGORITHM, SECRET_KEY


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[str] = None


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
    # return pwd_context.verify(plain_password, hashed_password)


# パスワードのハッシュを取得
def get_password_hash(password):
    return pwd_context.hash(password)


def get_user(db, email: str):
    if email in db:
        user_dict = db[email]
        return UserSchema(**user_dict)


def authenticate_user(db, email: str, password: str):
    user = get_user(db, email)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


# アクセストークンの作成
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    # トークンの有効期限があればそちらで設定（消して良いかも）
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=30)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# トークンからユーザーを取得
def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        # トークンからユーザーネームを取得し、存在しなかったらHTTPエラーを返す
        # payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        # print(payload)
        print('hogeeeeeeeeeeeeeeeeeeeeee')
        # TODO JWTの取得とかはOK get_userの引数とかをチェック
        #     email: str = payload.get("email")
        #     print(email)
        #     if email is None:
        #         raise credentials_exception
        #     token_data = TokenData(email=email)
        return False
    except JWTError:
        raise credentials_exception
    # user = get_user(db_session, email=token_data.email)
    # # user = db_session.query(UserModel).filter(email=email).first()
    # if user is None:
    #     raise credentials_exception
    # return user


async def get_current_active_user(
        current_user: UserSchema = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
