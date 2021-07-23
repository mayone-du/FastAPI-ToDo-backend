from datetime import datetime, timedelta
from uuid import uuid4

import graphene
from database.database import db
from fastapi import HTTPException
from fastapi_mail import FastMail, MessageSchema
from graphene_sqlalchemy import SQLAlchemyObjectType
from jose import JWTError, jwt
from libs.auth import create_access_token, verify_hash_data
from models.custom_user import CustomUserModel
from models.token import RefreshTokenModel
from pydantic import BaseModel
from settings.envs import (ACCESS_TOKEN_EXPIRE_MINUTES, ALGORITHM,
                           MAIL_CONFIGS, REFRESH_TOKEN_EXPIRE_DAYS, SECRET_KEY)

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
            access_token_object: dict = create_access_token(info, email=kwargs.get('email'), password=kwargs.get('password'))
            return CreateAccessToken(access_token_object=access_token_object)
        except:
            raise


# マジックリンクを送信
class SendMagicLinkEmail(graphene.Mutation):
    class Arguments:
        email = graphene.String(required=True)
        password = graphene.String(required=True)

    ok = graphene.Boolean()

    @staticmethod
    def mutate(root, info, **kwargs):
        try:
            # アクセストークンを作成
            access_token_object: dict = create_access_token(info, email=kwargs.get('email'), password=kwargs.get('password'))
            # バックグラウンドタスクで非優先的に、同期的にメールを送信
            background = info.context["background"]
            email_body = f'''
                <h1>hogehge body</h1>
                <p><br><a href="https://google.com">こちらのリンク</a>
                をクリックすると本登録が完了します。有効期限は30分です。</p>
                <p><a href="https://mayoblog.vercel.app/search/results?keyword={access_token_object.get('access_token')}">Link</a></p>
            '''
            message = MessageSchema(
                subject='Webアプリ 本登録のご案内',
                recipients=[kwargs.get('email')],
                body=email_body,
                subtype='html',
            )
            fm = FastMail(MAIL_CONFIGS)
            background.add_task(fm.send_message, message)
            ok=True
            return SendMagicLinkEmail(ok=ok)
        except:
            raise

# リフレッシュトークンの発行
class CreateRefreshToken(graphene.Mutation):
    class Arguments:
        ulid = graphene.String(required=True)
    refresh_token_object = graphene.JSONString(
        refresh_token = graphene.String(),
        expiration_date = graphene.String()
    ) 
    @staticmethod
    def mutate(root, info, **kwargs):
        try:
            # UUIDを生成してリフレッシュトークンとする
            uuid = uuid4().hex
            expiration_date = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
            db_refresh_token = RefreshTokenModel(uuid=uuid, token_holder=kwargs.get('ulid'), expiration_date=expiration_date)
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
        old_refresh_token = graphene.String(required=True)
    
    tokens_object = graphene.JSONString(
        access_token = graphene.String(),
        access_token_exp = graphene.DateTime(),
        refresh_token = graphene.String(),
        refresh_token_exp = graphene.DateTime()
    )

    @staticmethod
    def mutate(root, info, **kwargs):
        try:
            # 2種類のトークンを再発行し、もともとDBに保存しているリフレッシュトークンの値を更新する
            # 新しいリフレッシュトークンの作成
            new_refresh_token = uuid4().hex
            old_refresh_token = db.query(RefreshTokenModel).filter(RefreshTokenModel.uuid==kwargs.get('old_refresh_token')).first()
            old_refresh_token.uuid = new_refresh_token
            refresh_token_expiration_date =  datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
            old_refresh_token.expiration_date = refresh_token_expiration_date
            # 新しいアクセストークンの作成
            # TODO: 逆参照できるようにする（やっぱいらないかも） -> ex) old_refresh_token.token_holder.ulid
            ulid = old_refresh_token.token_holder
            # アクセストークンの作成
            access_token_expiration_date = datetime.utcnow() + timedelta(
                        minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
            # ulid、トークンタイプ、有効期限をもとにJWTを発行
            token_payload = {
                'ulid': ulid,
                'type': 'access_token',
                'exp': access_token_expiration_date
            }
            access_token = jwt.encode(token_payload,
                            SECRET_KEY,
                            algorithm=ALGORITHM)
            db.commit()
            tokens_object = {
                'access_token': access_token,
                'access_token_exp': str(access_token_expiration_date),
                'refresh_token': new_refresh_token,
                'refresh_token_exp': str(refresh_token_expiration_date),
            }
            return UpdateTokens(tokens_object=tokens_object)
        except:
            db.rollback()
            raise
        finally:
            db.close()



# # リフレッシュトークンの削除？
# class DeleteRefreshToken(graphene.Mutation):
#     pass
