from datetime import datetime

import graphene
from database.database import db_session
from fastapi.exceptions import HTTPException
from fastapi_mail.fastmail import FastMail
from fastapi_mail.schemas import MessageSchema
from graphene_sqlalchemy.types import SQLAlchemyObjectType
from models.custom_user import CustomUserModel
from models.token import RefreshTokenModel
from settings.envs import MAIL_CONFIGS
from ulid import ULID

# circular import回避のため下部で2箇所importしている


class CustomUserNode(SQLAlchemyObjectType):
    class Meta:
        model = CustomUserModel
        interfaces = (graphene.relay.Node, )

# class CustomUserConnections(graphene.relay.Connection):
#     class Meta:
#         node = CustomUserNode


# ユーザーの作成と、作成されたメールアドレス宛にマジックリンク付きメールを送信
class CreateCustomUser(graphene.Mutation):
    class Arguments:
        username = graphene.String(required=True)
        email = graphene.String(required=True)
        password = graphene.String(required=True)

    ok = graphene.Boolean()

    @staticmethod
    def mutate(root, info, **kwargs):
        try:
            # circular import回避のためここでimport
            from libs.auth import (create_access_token,
                                   create_access_token_exp, hash_data)
            new_user = CustomUserModel(ulid=str(ULID()), username=kwargs.get('username'),
                                    email=kwargs.get('email'),
                                    # ユーザーが登録したパスワードをハッシュ化して保存
                                    password=hash_data(kwargs.get('password')),
                                    is_verified=False)
            db_session.add(new_user)
            db_session.commit()
            # アクセストークンを作成
            payload = {
                "ulid": new_user.ulid,
                "iat": datetime.utcnow(),
                "exp": create_access_token_exp()
            }
            access_token = create_access_token(payload)
            # メール送信
            background = info.context["background"]
            email_body = f'''
                <h1>本登録のご案内</h1>
                <p><br><a href="https://sample.vercel.app/auth?token={access_token}">こちらのリンク</a>
                をクリックすると本登録が完了します。有効期限は30分です。</p>
                <p><a href="https://mayoblog.vercel.app/search/results?keyword={access_token}">Link</a></p>
            '''
            message = MessageSchema(
                subject='Webアプリ 本登録のご案内',
                recipients=[kwargs.get('email')],
                body=email_body,
                subtype='html',
            )
            fm = FastMail(MAIL_CONFIGS)
            # バックグラウンドタスクで非優先的に、同期的にメールを送信
            background.add_task(fm.send_message, message)
            ok = True
            return CreateCustomUser(ok=ok)
        except:
            db_session.rollback()
            raise
        finally:
            db_session.close()


# 基本的なユーザー情報の更新 別でProfileモデルなどを作成し、Optional的な内容はそちらに持たせると良いかも。
class UpdateCustomUser(graphene.Mutation):
    class Arguments:
        username = graphene.String(required=True)

    ok = graphene.Boolean()

    @staticmethod
    def mutate(root, info, **kwargs):
        try:
            # TODO: ユーザー情報更新機能の実装
            # db_session.commit()
            ok=True
            return UpdateCustomUser(ok=ok)
        except:
            db_session.rollback()
            raise
        finally:
            db_session.close()



# 初回認証時に呼ばれる関数。リクエストヘッダーからJWTを受け取って検証し、本人確認のフラグをTrueにする。
# リフレッシュトークンも発行し、フロントへ返す。
class UpdateVerifyCustomUser(graphene.Mutation):

    refresh_token_object = graphene.JSONString(
        refresh_token = graphene.String(),
        expiration_date = graphene.String()
    ) 

    @staticmethod
    def mutate(root, info):
        try:
            # リクエストヘッダーからJWTを取得してユーザーの検証と取得
            from libs.auth import (create_refresh_token,
                                   create_refresh_token_exp,
                                   get_current_custom_user)
            current_user: CustomUserModel = get_current_custom_user(info)           
            # 既に本人確認がすんでいるか確認
            if current_user.is_verified:
                raise HTTPException(status_code=400, detail="既に本人確認済みです。")
            # ユーザーの本人確認フラグを更新
            current_user.is_verified = True
            db_session.commit()
            
            refresh_token = create_refresh_token()
            refresh_token_exp = create_refresh_token_exp()
            db_refresh_token = RefreshTokenModel(uuid=refresh_token, token_holder=current_user.ulid, expiration_date=refresh_token_exp)
            db_session.add(db_refresh_token)
            refresh_token_object = {
                "refresh_token" : refresh_token,
                "expiration_date": str(refresh_token_exp)
            }
            db_session.commit()
            return UpdateVerifyCustomUser(refresh_token_object=refresh_token_object)
        except:
            db_session.rollback()
            raise
        finally:
            db_session.close()


# ユーザーの削除（本人のみしか削除できないようにする）
class DeleteCustomUser(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)

    ok = graphene.Boolean()

    @staticmethod
    # @login_required
    def mutate(root, info, **kwargs):
        try:
            # user = get_current_custom_user(info)
            ok=True
        except:
            db_session.rollback()
            raise
        finally:
            db_session.close()
            return DeleteCustomUser(ok=ok)
