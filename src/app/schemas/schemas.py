import graphene
from auth.auth import get_current_user
from graphene_sqlalchemy.fields import SQLAlchemyConnectionField
from graphql_relay import from_global_id
from models.user import UserModel

from .task import CreateTask, DeleteTask, TaskNode, UpdateTask
from .token import CreateToken
from .user import CreateUser, UserNode


class Query(graphene.ObjectType):
    current_user = graphene.Field(UserNode)
    user = graphene.Field(UserNode, id=graphene.NonNull(graphene.ID))
    all_users = SQLAlchemyConnectionField(UserNode)
    all_tasks = SQLAlchemyConnectionField(TaskNode)


    def resolve_current_user(self, info):
        # TODO
        headers = dict(info.context['request']['headers'])
        jwt = headers[b'authorization'].decode()
        user = get_current_user(jwt)
        return user

    # idからユーザーを取得
    def resolve_user(self, info, id):
        print(info.context['request']['headers'])
        query = UserNode.get_query(info)
        # 受け取ったidと一致するUserオブジェクトを返却
        return query.filter(UserModel.id==from_global_id(id)[1]).first() 

    # すべてのユーザーを取得
    def resolve_all_users(self, info):
        query = UserNode.get_query(info)
        return query.all()

    # すべてのタスクを取得
    def resolve_all_tasks(self, info):
        query = TaskNode.get_query(info)
        return query.all()


class Mutation(graphene.ObjectType):
    create_user = CreateUser.Field()
    create_task = CreateTask.Field()
    update_task = UpdateTask.Field()
    delete_task = DeleteTask.Field()

    # auth
    create_token = CreateToken.Field()
    # get_access_token = 
