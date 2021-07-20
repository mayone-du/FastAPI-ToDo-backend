# from typing import Optional

import graphene
from database.database import db
from graphene_sqlalchemy.types import SQLAlchemyObjectType
from models.custom_user import CustomUserModel
from pydantic import BaseModel
from ulid import ULID


class CustomUserSchema(BaseModel):
    username: str
    email: str
    password: str
    # is_active: bool


class CustomUserNode(SQLAlchemyObjectType):
    class Meta:
        model = CustomUserModel
        interfaces = (graphene.relay.Node, )


class CreateCustomUser(graphene.Mutation):
    class Arguments:
        username = graphene.String(required=True)
        email = graphene.String(required=True)
        password = graphene.String(required=True)

    ok = graphene.Boolean()

    @staticmethod
    def mutate(root, info, **kwargs):
        try:
            from libs.auth import hash_password
            new_user = CustomUserModel(ulid=str(ULID()), username=kwargs.get('username'),
                                    email=kwargs.get('email'),
                                    # ユーザーが登録したパスワードをハッシュ化して保存
                                    password=hash_password(kwargs.get('password')))
            db.add(new_user)
            db.commit()
            ok = True
            return CreateCustomUser(ok=ok)
        except:
            db.rollback()
            # TODO: エラーハンドリング
            raise
        finally:
            db.close()


# ユーザー情報の更新
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


class DeleteCustomUser(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)

    ok = graphene.Boolean()

    @staticmethod
    def mutate(root, info, **kwargs):
        try:
            ok=True
        except:
            # ok=False
            raise
        finally:
            return DeleteCustomUser(ok=ok)
