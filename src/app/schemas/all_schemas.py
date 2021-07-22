import graphene
from app.libs.auth import get_current_custom_user  # , send_email_background
from fastapi import HTTPException, status
from fastapi_mail import FastMail, MessageSchema
from graphene_sqlalchemy.fields import SQLAlchemyConnectionField
from graphql_relay import from_global_id
from jose import JWTError, jwt
from models.custom_user import CustomUserModel
from settings.envs import MAIL_CONFIGS

from .custom_user import CreateCustomUser, CustomUserNode
from .task import CreateTask, DeleteTask, TaskNode, UpdateTask
from .token import CreateAccessToken, CreateRefreshToken


class Query(graphene.ObjectType):
    current_user = graphene.Field(CustomUserNode)
    user = graphene.Field(CustomUserNode, id=graphene.NonNull(graphene.ID))
    all_users = SQLAlchemyConnectionField(CustomUserNode)
    all_tasks = SQLAlchemyConnectionField(TaskNode, email=graphene.String(required=True))

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

    # すべてのタスクを取得
    def resolve_all_tasks(self, info, **kwargs):
        query = TaskNode.get_query(info)
        # send_email_background(BackgroundTasks(), subject='subject', email_to='cocomayo1201@gmail.com')
        background = info.context["background"]
        message = MessageSchema(
            subject='subject',
            recipients=[kwargs.get('email')],
            body='''<h1>hogehge body</h1>''',
            subtype='html',
        )
        fm = FastMail(MAIL_CONFIGS)
        background.add_task(fm.send_message, message
                               #   template_name='email.html'
        )
        return query.all()


class Mutation(graphene.ObjectType):
    create_user = CreateCustomUser.Field()
    create_task = CreateTask.Field()
    update_task = UpdateTask.Field()
    delete_task = DeleteTask.Field()

    # auth
    create_access_token = CreateAccessToken.Field()
    create_refresh_token = CreateRefreshToken.Field()
