from datetime import datetime, timedelta
from uuid import uuid4

import graphene
from database.database import db
from fastapi import HTTPException
from graphene_sqlalchemy import SQLAlchemyObjectType
from jose import JWTError, jwt
from libs.auth import verify_hash_data
from models.custom_user import CustomUserModel
from models.token import RefreshTokenModel
from pydantic import BaseModel
from settings.envs import ACCESS_TOKEN_EXPIRE_MINUTES, ALGORITHM, SECRET_KEY

from .custom_user import CustomUserNode


# アクセストークンの発行 DBに保存はしない。
class CreateAccessToken(graphene.Mutation):
    class Arguments:
        email = graphene.String(required=True)
        password = graphene.String(required=True)

    access_token_object = graphene.JSONString(
        access_toekn = graphene.String(),
        expiration_date = graphene.DateTime()
    )
    # アクセストークン作成時にemailとpasswordを受け取り、そのユーザーのULIDをもとにJWTを発行
    @staticmethod
    def mutate(root, info, **kwargs):
        try:
            input_email = kwargs.get('email')
            input_password = kwargs.get('password')
            # emailからそのユーザーのインスタンスを取得
            user = CustomUserNode.get_query(info).filter(
                CustomUserModel.email == input_email).first()
            # 登録済みのハッシュ化されたパスワード
            registered_password = user.password
            ulid = user.ulid

            # パスワードが一致しなかったらエラーレスポンスを返す
            if not verify_hash_data(input_password, registered_password):
                # TODO: エラーレスポンスの実装
                raise HTTPException(status_code=401)

            expiration_date = datetime.utcnow() + timedelta(minutes=int(ACCESS_TOKEN_EXPIRE_MINUTES))
            # ulid、トークンタイプ、有効期限をもとにJWTを発行
            token_payload = {
                'ulid': ulid,
                # access_token or refresh_token
                'type': 'access_token',
                # 有効期限をUTCタイムスタンプ形式で設定
                'exp': expiration_date
            }
            access_token = jwt.encode(token_payload, SECRET_KEY, algorithm=ALGORITHM)
            access_token_object = {
                'access_token': access_token,
                'expiration_date': str(expiration_date)
            }
            return CreateAccessToken(access_token_object=access_token_object)
        except:
            raise


# マジックリンクを送信
class SendMagicLink(graphene.Mutation):
    class Arguments:
        email = graphene.String(required=True)
        password = graphene.String(required=True)

    ok = graphene.Boolean()

    @staticmethod
    def mutate(root, info, **kwargs):
        try:
            pass
            ok=True
            SendMagicLink(ok=ok)
        except:
            raise

# リフレッシュトークンの発行
class CreateRefreshToken(graphene.Mutation):
    refresh_token_object = graphene.JSONString(
        refresh_token = graphene.String(),
        expiration_date = graphene.String()
    ) 
    @staticmethod
    def mutate(root, info):
        try:
            # UUIDを生成してリフレッシュトークンとする
            uuid = uuid4().hex
            expiration_date = datetime.utcnow() + timedelta(days=7)
            db_refresh_token = RefreshTokenModel(body=uuid, expiration_date=expiration_date)
            refresh_token_object = {
                    'refresh_token' : uuid,
                    'expiration_date' : str(expiration_date)
                }
            
            db.add(db_refresh_token)
            db.commit()
            return CreateRefreshToken(refresh_token_object=refresh_token_object)
        except:
            db.rollback()
            raise
        finally:
            db.close()


# リフレッシュトークンを受け取り、有効期限の切れたアクセストークンを再発行し、リフレッシュトークンも新しいものに更新する
class UpdateTokens(graphene.Mutation):
    class Arguments:
        refresh_token = graphene.String(required=True)
    
    tokens_object = {
        'access_token': graphene.String(),
        'access_token_exp': graphene.DateTime(),
        'refresh_token': graphene.String(),
        'refresh_token_exp': graphene.DateTime()
    }

    @staticmethod
    def mutate(root, info, **kwargs):
        # 2種類のトークンを再発行し、もともとDBに保存しているリフレッシュトークンを削除する
        refresh_token = kwargs.get('refresh_token')
        tokens_object = {
            'access_token': '',
            'access_token_exp': '',
            'refresh_token': '',
            'refresh_token_exp': '',
        }
        return UpdateTokens(tokens_object=tokens_object)



# # リフレッシュトークンの削除？
# class DeleteRefreshToken(graphene.Mutation):
#     pass
