import graphene
from database.database import db
from graphene_sqlalchemy.types import SQLAlchemyObjectType
from models.custom_user import CustomUserModel
from ulid import ULID

# circular import回避のため下部で2箇所importしている


class CustomUserNode(SQLAlchemyObjectType):
    class Meta:
        model = CustomUserModel
        interfaces = (graphene.relay.Node, )


# ユーザーの作成
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
            from libs.auth import hash_data
            new_user = CustomUserModel(ulid=str(ULID()), username=kwargs.get('username'),
                                    email=kwargs.get('email'),
                                    # ユーザーが登録したパスワードをハッシュ化して保存
                                    password=hash_data(kwargs.get('password')))
            db.add(new_user)
            db.commit()
            ok = True
            return CreateCustomUser(ok=ok)
        except:
            db.rollback()
            raise
        finally:
            db.close()


# 基本的なユーザー情報の更新 別でProfileモデルなどを作成し、Optional的な内容はそちらに持たせると良いかも。
class UpdateCustomUser(graphene.Mutation):
    class Arguments:
        username = graphene.String(required=True)

    ok = graphene.Boolean()

    @staticmethod
    def mutate(root, info, **kwargs):
        try:
            # TODO: ユーザー情報更新機能の実装
            pass
            db.add()
            db.commit()
            ok=True
            return UpdateCustomUser(ok=ok)
        except:
            db.rollback()
            raise
        finally:
            db.close()



# 初回認証時に呼ばれる関数。CookieからJWTを受け取って検証し、本人確認のフラグをTrueにする
class UpdateProofCustomUser(graphene.Mutation):
    ok = graphene.Boolean()

    @staticmethod
    def mutate(root, info, **kwargs):
        try:
            # cookieヘッダーのauthorizatoinからJWTを取得
            # TODO: tokenをvalidation
            # ユーザーの本人確認フラグを更新
            from libs.auth import get_current_custom_user
            current_user: CustomUserModel = get_current_custom_user(info)           
            current_user.is_proof = True
            db.commit()
            ok=True
            return UpdateProofCustomUser(ok=ok)
        except:
            db.rollback()
            raise
        finally:
            db.close()


# ユーザーの削除
class DeleteCustomUser(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)

    ok = graphene.Boolean()

    @staticmethod
    def mutate(root, info, **kwargs):
        try:
            ok=True
        except:
            raise
        finally:
            return DeleteCustomUser(ok=ok)
