import database
import graphene
from graphene import relay
from graphene_sqlalchemy import SQLAlchemyObjectType
from graphql_relay import from_global_id
from models import task
from pydantic import BaseModel

db = database.db_session.session_factory()


class TaskSchema(BaseModel):
    title: str
    content: str
    is_done: bool


class TaskNode(SQLAlchemyObjectType):
    class Meta:
        model = task.TaskModel
        interfaces = (graphene.relay.Node, )


class CreateTask(graphene.Mutation):
    class Arguments:
        title = graphene.String(required=True)
        content = graphene.String(required=False)

    ok = graphene.Boolean()

    @staticmethod
    def mutate(root, info, **kwargs):
        new_task = TaskSchema(title=kwargs.get('title'),
                              content=kwargs.get('content'),
                              is_done=False)
        db_post = task.TaskModel(title=new_task.title,
                                 content=new_task.content)
        db.add(db_post)
        db.commit()
        db.refresh(db_post)
        ok = True
        return CreateTask(ok=ok)


class UpdateTask(graphene.ClientIDMutation):
    class Arguments:
        id = graphene.ID(required=True)
        title = graphene.String(required=True)
        content = graphene.String(required=True)
        is_done = graphene.Boolean(required=True)

    @staticmethod
    def mutate(root, info, **kwargs):
        pass


class DeleteTask(graphene.ClientIDMutation):
    class Arguments:
        id = graphene.ID(required=True)

    @staticmethod
    def mutate(root, info):
        pass
