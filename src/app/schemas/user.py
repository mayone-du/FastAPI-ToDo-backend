from typing import Optional

import database
import graphene
from graphene_sqlalchemy.types import SQLAlchemyObjectType
from models import user
from pydantic import BaseModel


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


class UserInDBSchema(UserSchema):
    hashed_password: str


class UserInDBNode(SQLAlchemyObjectType):
    class Meta:
        model = user.UserModel
        interfaces = (graphene.relay.Node, )


class CreateUser(graphene.Mutation):
    class Arguments:
        username = graphene.String(required=True)
        email = graphene.String(required=True)
        password = graphene.String(required=True)

    ok = graphene.Boolean()

    @staticmethod
    def mutate(root, info, **kwargs):
        new_user = UserSchema(username=kwargs.get('username'),
                              email=kwargs.get('email'),
                              password=kwargs.get('password'))
        db_user = user.UserModel(username=new_user.username,
                                 email=new_user.email,
                                 password=new_user.password)
        database.db.add(db_user)
        database.db.commit()
        database.db.refresh(db_user)
        ok = True
        return CreateUser(ok=ok)
