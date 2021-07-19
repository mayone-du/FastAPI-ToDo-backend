from typing import Optional

import database
import graphene
from graphene_sqlalchemy.types import SQLAlchemyObjectType
from models import user
from pydantic import BaseModel
from ulid import ULID


class UserSchema(BaseModel):
    username: str
    email: str
    password: str
    # email: Optional[str] = None
    # disabled: Optional[bool] = None


class UserNode(SQLAlchemyObjectType):
    class Meta:
        model = user.UserModel
        interfaces = (graphene.relay.Node, )


# class UserInDBSchema(UserSchema):
#     hashed_password: str


# class UserInDBNode(SQLAlchemyObjectType):
#     class Meta:
#         model = user.UserModel
#         interfaces = (graphene.relay.Node, )


class CreateUser(graphene.Mutation):
    class Arguments:
        username = graphene.String(required=True)
        email = graphene.String(required=True)
        password = graphene.String(required=True)

    ok = graphene.Boolean()

    @staticmethod
    def mutate(root, info, **kwargs):
        try:
            from auth.auth import hash_password
            new_user = user.UserModel(ulid=str(ULID()), username=kwargs.get('username'),
                                    email=kwargs.get('email'),
                                    # ユーザーが登録したパスワードをハッシュ化して保存
                                    password=hash_password(kwargs.get('password')))
            database.db.add(new_user)
            database.db.commit()
            database.db.refresh(new_user)
            ok = True
            return CreateUser(ok=ok)
        except:
            database.db.rollback()
            raise
