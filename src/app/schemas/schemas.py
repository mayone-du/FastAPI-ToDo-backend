import graphene
from graphene_sqlalchemy.fields import SQLAlchemyConnectionField

from .task import CreateTask, DeleteTask, TaskNode, UpdateTask
from .user import CreateUser, UserNode


class Query(graphene.ObjectType):
    current_user = graphene.Field(UserNode)
    all_users = SQLAlchemyConnectionField(UserNode)
    all_tasks = SQLAlchemyConnectionField(TaskNode)

    def resolve_current_user(self, info):
        return UserNode.get_query(info).first()
        #   .filter(username="VXNlck5vZGU6MQ==")

    def resolve_all_users(self, info):
        query = UserNode.get_query(info)
        return query.all()

    def resolve_all_tasks(self, info):
        query = TaskNode.get_query(info)
        return query.all()


class Mutation(graphene.ObjectType):
    create_user = CreateUser.Field()
    create_task = CreateTask.Field()
    update_task = UpdateTask.Field()
    delete_task = DeleteTask.Field()

    # auth
    # get_access_token = 
