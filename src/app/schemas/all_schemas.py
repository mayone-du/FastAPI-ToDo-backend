import graphene
from graphene_sqlalchemy.fields import SQLAlchemyConnectionField
from graphql_relay import from_global_id
from libs.auth import get_current_custom_user  # , send_email_background
from models.custom_user import CustomUserModel
from models.task import TaskModel

from .custom_user import (CreateCustomUser, CustomUserNode,
                          UpdateVerifyCustomUser)
from .email import SendMagicLinkEmail
from .task import CreateTask, DeleteTask, TaskNode, UpdateTask
from .token import ReAuthentication, UpdateTokens


class Query(graphene.ObjectType):
    node = graphene.relay.Node.Field()

    current_user = graphene.Field(CustomUserNode)
    user = graphene.Field(CustomUserNode, id=graphene.NonNull(graphene.ID))
    all_users = SQLAlchemyConnectionField(CustomUserNode)
    task = graphene.Field(TaskNode, id=graphene.NonNull(graphene.ID))
    all_tasks = SQLAlchemyConnectionField(TaskNode)

    # 現在ログインしているユーザーを取得
    def resolve_current_user(self, info):
        return get_current_custom_user(info)

    # idからユーザーを取得
    def resolve_user(self, info, id):
        query = CustomUserNode.get_query(info)
        # 受け取ったidと一致するUserオブジェクトを返却
        return query.filter(CustomUserModel.id == from_global_id(id)[1]).first()

    # すべてのユーザーを取得
    def resolve_all_users(self, info):
        query = CustomUserNode.get_query(info)
        return query.all()

    # idからタスクを取得
    def resolve_task(self, info, id):
        query = TaskNode.get_query(info).filter(TaskModel.id==from_global_id(id)[1]).first()
        return query

    # すべてのタスクを取得
    def resolve_all_tasks(self, info):
        query = TaskNode.get_query(info)
        return query.all()


class Mutation(graphene.ObjectType):
    # user
    create_custom_user = CreateCustomUser.Field()
    update_verify_custom_user = UpdateVerifyCustomUser.Field()

    # task
    create_task = CreateTask.Field()
    update_task = UpdateTask.Field()
    delete_task = DeleteTask.Field()

    # auth
    update_tokens = UpdateTokens.Field()
    send_magic_link_email = SendMagicLinkEmail.Field()
    re_authentication = ReAuthentication.Field()
