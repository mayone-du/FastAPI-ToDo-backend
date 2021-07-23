from datetime import datetime, timedelta
from time import time
from uuid import uuid4

import bcrypt
import graphene
from app.libs.auth import hash_data
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
            # TODO: リファクタ（関数名がややこしい）
            access_token_object: dict = create_access_token(info, email=kwargs.get('email'), password=kwargs.get('password'))
            # バックグラウンドタスクで非優先的に、同期的にメールを送信
            background = info.context["background"]
            email_body = f'''
                <h1>本登録のご案内</h1>
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

# ? リフレッシュトークンの発行（初回のみ？）
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
            old_refresh_token = db.query(RefreshTokenModel).filter(RefreshTokenModel.uuid==kwargs.get('old_refresh_token')).first()
            new_refresh_token = uuid4().hex
            # 受け取ったトークンの有効期限が切れてないか検証
            if old_refresh_token.expiration_date.timestamp() < datetime.utcnow().timestamp():
                raise
            old_refresh_token.uuid = new_refresh_token
            refresh_token_expiration_date = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
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


# リフレッシュトークンの有効期限がきれて再度emailとpasswordでログインする場合
class ReAuthentication(graphene.Mutation):
    class Arguments:
        email = graphene.String(required=True)
        password = graphene.String(required=True)

    tokens_object = graphene.JSONString(
        access_token = graphene.String(),
        access_token_exp = graphene.DateTime(),
        refresh_token = graphene.String(),
        refresh_token_exp = graphene.DateTime()
    )

    @staticmethod
    def mutate(root, info, **kwargs):
        try:
            input_email = kwargs.get('email')
            input_password = kwargs.get('password')
            # ユーザーの検証 & 取得
            # user = db.query(CustomUserModel).filter(CustomUserModel.email==input_email, CustomUserModel.password==hash_data(input_password)).first()
            # if user is None:
            #     raise
            access_token_object: dict = create_access_token(info, email=input_email, password=input_password)
            # emailとpasswordからユーザーのulidを取得
            user = db.query(CustomUserModel).filter(CustomUserModel.email==input_email).first()
            if verify_hash_data(input_password, user.password) == False:
                raise
            # TODO: ↓リファクタ 関数にして共通化
            new_refresh_token = uuid4().hex
            refresh_token_expiration_date = datetime.utcnow().timestamp()
            # リフレッシュトークンを更新
            old_refresh_token = db.query(RefreshTokenModel).filter(RefreshTokenModel.token_holder==user.ulid).first()
            old_refresh_token.uuid=new_refresh_token
            db.commit()
            db.close()
            tokens_object = {
                'access_token': access_token_object.get('access_token'),
                'access_token_exp': access_token_object.get('expiration_date'),
                'refresh_token': new_refresh_token,
                'refresh_token_exp': str(refresh_token_expiration_date),
            }
            return ReAuthentication(tokens_object=tokens_object)
        except:
            raise


# リフレッシュトークンの削除
class DeleteRefreshToken(graphene.Mutation):
    class Arguments:
        ulid = graphene.String()
    
    ok = graphene.Boolean()

    @staticmethod
    def mutate(root, info, **kwargs):
        try:
            # TODO: ユーザーのulidをもとに削除
            db.delete()
            ok=True
        except:
            db.rollback()
            raise
        finally:
            db.close()
        return DeleteRefreshToken(ok=ok)


