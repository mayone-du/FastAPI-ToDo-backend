from datetime import datetime

import graphene
from app.schemas.custom_user import CustomUserNode
from database.database import db
from fastapi import HTTPException
from libs.auth import (create_access_token, create_access_token_exp,
                       create_refresh_token, create_refresh_token_exp,
                       verify_hash_data)
from models.custom_user import CustomUserModel
from models.token import RefreshTokenModel
from pytz import UTC


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
            old_refresh_token = db.query(RefreshTokenModel).filter(RefreshTokenModel.uuid==kwargs.get('old_refresh_token')).first()
            # 受け取ったトークンの有効期限が切れてないか検証
            if old_refresh_token.expiration_date.replace(tzinfo=UTC) < datetime.utcnow().replace(tzinfo=UTC):
                raise
            # リフレッシュトークンを作成して更新
            new_refresh_token = create_refresh_token()
            old_refresh_token.uuid = new_refresh_token
            refresh_token_expiration_date = create_refresh_token_exp()
            old_refresh_token.expiration_date = refresh_token_expiration_date
            # 新しいアクセストークンの作成
            ulid = old_refresh_token.token_holder
            # アクセストークンの作成
            access_token_expiration_date = create_access_token_exp()
            # ulid、トークンタイプ、有効期限をもとにJWTを発行
            token_payload = {
                'ulid': ulid,
                'iat': datetime.utcnow(),
                'exp': access_token_expiration_date
            }
            access_token = create_access_token(token_payload)
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
            user = db.query(CustomUserModel).filter(CustomUserModel.email==input_email).first()
            # emailとpasswordからユーザーのulidを取得、検証
            if verify_hash_data(input_password, user.password) == False:
                raise

            access_token_exp = create_access_token_exp()
            payload = {
                'ulid': user.ulid,
                'iat': datetime.utcnow(),
                'exp': access_token_exp
            }
            access_token = create_access_token(payload)
            new_refresh_token = create_refresh_token()
            refresh_token_expiration_date = create_refresh_token_exp()
            # リフレッシュトークンを取得
            old_refresh_token = db.query(RefreshTokenModel).filter(RefreshTokenModel.token_holder==user.ulid).first()
            # 更新
            old_refresh_token.uuid=new_refresh_token
            db.commit()
            tokens_object = {
                'access_token': access_token,
                'access_token_exp': str(access_token_exp),
                'refresh_token': new_refresh_token,
                'refresh_token_exp': str(refresh_token_expiration_date),
            }
            return ReAuthentication(tokens_object=tokens_object)
        except:
            db.rollback()
            raise
        finally:
            db.close()



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


