from typing import Optional

import graphene
from database.database import db
from graphene_sqlalchemy.types import SQLAlchemyObjectType
from models.user import UserModel
from pydantic import BaseModel
from ulid import ULID


class UserSchema(BaseModel):
    username: str
    email: str
    password: str
    # is_active: bool


class UserNode(SQLAlchemyObjectType):
    class Meta:
        model = UserModel
        interfaces = (graphene.relay.Node, )


class CreateUser(graphene.Mutation):
    class Arguments:
        username = graphene.String(required=True)
        email = graphene.String(required=True)
        password = graphene.String(required=True)

    ok = graphene.Boolean()

    @staticmethod
    def mutate(root, info, **kwargs):
        try:
            from libs.auth import hash_password
            new_user = UserModel(ulid=str(ULID()), username=kwargs.get('username'),
                                    email=kwargs.get('email'),
                                    # ユーザーが登録したパスワードをハッシュ化して保存
                                    password=hash_password(kwargs.get('password')))
            db.add(new_user)
            db.commit()
            db.refresh(new_user)
            ok = True
            return CreateUser(ok=ok)
            # TODO: エラーハンドリング
        except:
            db.rollback()
            raise


class UpdateUser(graphene.Mutation):
    class Arguments:
        username = graphene.String(required=True)

    ok = graphene.Boolean()

    @staticmethod
    def mutate(root, info, **kwargs):
        try:
            # TODO: ユーザー情報更新機能の実装
            pass
            ok=True
            return UpdateUser(ok=ok)
        except:
            pass


class DeleteUser(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)

    ok = graphene.Boolean()

    @staticmethod
    def mutate(root, info, **kwargs):
        pass
        ok=True
        return DeleteUser(ok=ok)
