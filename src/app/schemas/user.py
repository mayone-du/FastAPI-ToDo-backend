from typing import Optional

import graphene
from graphene_sqlalchemy.types import SQLAlchemyObjectType
from models import user
from pydantic import BaseModel


class UserSchema(BaseModel):
    username: str
    email: Optional[str] = None
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
