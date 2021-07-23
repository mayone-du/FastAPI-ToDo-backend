import graphene
from app.models.task import TaskModel
from database.database import db
from graphene_sqlalchemy import SQLAlchemyObjectType
from graphql_relay.node.node import from_global_id
# from graphql_relay import from_global_id
from models import task
from pydantic import BaseModel

# class TaskSchema(BaseModel):
#     title: str
#     content: str
#     is_done: bool


class TaskNode(SQLAlchemyObjectType):
    class Meta:
        model = task.TaskModel
        interfaces = (graphene.relay.Node,)


class CreateTask(graphene.Mutation):
    class Arguments:
        title = graphene.String(required=True)
        content = graphene.String(required=False)

    ok = graphene.Boolean()

    @staticmethod
    def mutate(root, info, **kwargs):
        try:
            db_task = task.TaskModel(title=kwargs.get('title'),
                                    content=kwargs.get('content'),
                                    is_done=False)
            db.add(db_task)
            db.commit()
            ok = True
            return CreateTask(ok=ok)
        except:
            db.rollback()
            raise
        finally:
            db.close()


class UpdateTask(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)
        title = graphene.String(required=True)
        content = graphene.String(required=True)
        is_done = graphene.Boolean(required=True)

    ok = graphene.Boolean()

    @staticmethod
    def mutate(root, info, **kwargs):
        try:
            # idから取得したtaskを更新
            current_task: TaskModel = TaskNode.get_query(info).filter(TaskModel.id==from_global_id(kwargs.get('id'))[1]).first()
            # TODO: リファクタリング
            current_task.title=kwargs.get('title')
            current_task.content=kwargs.get('content')
            current_task.is_done=kwargs.get('is_done')
            db.commit()
            ok = True
            return UpdateTask(ok=ok)
        except:
            db.rollback()
            raise
        finally:
            db.close()


class DeleteTask(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)

    ok = graphene.Boolean()

    @staticmethod
    def mutate(root, info):
        try:
            ok = True
            return DeleteTask(ok=ok)
        except:
            raise
        finally:
            pass

