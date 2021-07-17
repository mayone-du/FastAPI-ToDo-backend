import graphene
from graphene_sqlalchemy.fields import SQLAlchemyConnectionField

from task import CreateTask, TaskNode


class Query(graphene.ObjectType):
    hello = graphene.String(name=graphene.String(default_value="stranger"))
    all_tasks = SQLAlchemyConnectionField(TaskNode)

    def resolve_hello(self, info, name):
        # return User.parse_obj(User)
        return "Hello! : " + name

    def resolve_all_tasks(self, info):
        query = TaskNode.get_query(info)
        return query.all()


class Mutation(graphene.ObjectType):
    create_new_post = CreateTask.Field()
