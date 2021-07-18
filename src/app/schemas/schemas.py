import graphene
from graphene_sqlalchemy.fields import SQLAlchemyConnectionField

from .task import CreateTask, DeleteTask, TaskNode, UpdateTask
from .user import UserNode


class Query(graphene.ObjectType):
    all_users = SQLAlchemyConnectionField(UserNode)
    all_tasks = SQLAlchemyConnectionField(TaskNode)

    def resolve_all_users(self, info):
        query = UserNode.get_query(info)
        return query.all()



    def resolve_all_tasks(self, info):
        query = TaskNode.get_query(info)
        return query.all()


class Mutation(graphene.ObjectType):
    create_task = CreateTask.Field()
    update_task = UpdateTask.Field()
    delete_task = DeleteTask.Field()
