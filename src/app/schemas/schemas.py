import graphene
from auth.token_schemas import CreateAccessToken
from fastapi import HTTPException, status
from graphene_sqlalchemy.fields import SQLAlchemyConnectionField
from graphql_relay import from_global_id
from jose import JWTError, jwt
from models.user import UserModel
from settings.envs import ALGORITHM, SECRET_KEY

from .task import CreateTask, DeleteTask, TaskNode, UpdateTask
from .user import CreateUser, UserNode


class Query(graphene.ObjectType):
    current_user = graphene.Field(UserNode)
    user = graphene.Field(UserNode, id=graphene.NonNull(graphene.ID))
    all_users = SQLAlchemyConnectionField(UserNode)
    all_tasks = SQLAlchemyConnectionField(TaskNode)

    def resolve_current_user(self, info):
        try:
            # headersのauthorizationからjwtを取得
            headers = dict(info.context['request']['headers'])
            token = headers[b'authorization'].decode()[
                7:]  # Bearer の文字列を半角空白含めて削除
            # トークンの内容を取得
            payload: dict = jwt.decode(token,
                                       SECRET_KEY,
                                       algorithms=[ALGORITHM])
            ulid = payload.get('ulid')
            # ulidに紐づくユーザーを返却
            return UserNode.get_query(info).filter(
                UserModel.ulid == ulid).first()
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

    # idからユーザーを取得
    def resolve_user(self, info, id):
        query = UserNode.get_query(info)
        # 受け取ったidと一致するUserオブジェクトを返却
        return query.filter(UserModel.id == from_global_id(id)[1]).first()

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
    create_token = CreateAccessToken.Field()
    # get_access_token =
