from typing import List, Optional

import graphene
from graphene_sqlalchemy import SQLAlchemyObjectType
from graphene_sqlalchemy.fields import SQLAlchemyConnectionField
from pydantic import BaseModel

import database
import models

db = database.db_session.session_factory()


class PostSchema(BaseModel):
    title: str
    content: str


class PostModel(SQLAlchemyObjectType):
    class Meta:
        model = models.Post
        interfaces = (graphene.relay.Node, )


class CreateNewPost(graphene.Mutation):
    class Arguments:
        title = graphene.String(required=True)
        content = graphene.String(required=True)

    ok = graphene.Boolean()

    @staticmethod
    def mutate(root, info, title, content):
        post = PostSchema(title=title, content=content)
        db_post = models.Post(title=post.title, content=post.content)
        db.add(db_post)
        db.commit()
        db.refresh(db_post)
        ok = True
        return CreateNewPost(ok=ok)


class Query(graphene.ObjectType):
    # node = graphene.relay.Node.Field()
    hello = graphene.String(name=graphene.String(default_value="stranger"))
    # all_posts = graphene.Field(PostModel, id=graphene.NonNull())
    all_posts = SQLAlchemyConnectionField(PostModel)

    def resolve_hello(self, info, name):
        # return User.parse_obj(User)
        return "Hello! : " + name

    def resolve_all_posts(self, info):
        query = PostModel.get_query(info)
        return query.all()


class Mutation(graphene.ObjectType):
    create_new_post = CreateNewPost.Field()
