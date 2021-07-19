import graphene
from app.models.user import UserModel
from app.schemas.user import UserNode
from auth.auth import (create_access_token, get_password_hash, hash_password,
                       verify_password)
from fastapi import HTTPException
from ulid import ULID


class CreateAccessToken(graphene.Mutation):
    class Arguments:
        email = graphene.String(required=True)
        password = graphene.String(required=True)

    access_token = graphene.String()

    # アクセストークン作成時にemailとpasswordを受け取り、そのユーザーのULIDをもとにJWTを発行
    @staticmethod
    def mutate(root, info, **kwargs):
        input_email = kwargs.get('email')
        input_password = kwargs.get('password')
        # emailからそのユーザーのパスワードを取得
        registered_password = UserNode.get_query(info).filter(UserModel.email==input_email).first().password
        ulid = UserNode.get_query(info).filter(UserModel.email==input_email).first().ulid
        print(ulid)
        # パスワードが一致するか検証
        if verify_password(input_password, registered_password):
            print('ok')
        else:
            print('out! password is no-match')
            raise HTTPException(status_code=401)
        # ulid = UserNode.get_query(info).filter(UserModel.password==hash_password(input_password)).first().id
        
        # ulid = UserNode.get_query(info).filter(UserModel.email==email, UserModel.password==registered_password).first().id
        # print(ulid)
        # ulid、トークンタイプ、有効期限をもとにJWTを発行
        # user_data = {'ulid': kwargs.get('ulid'), 'password': hash_password(kwargs.get('password')).decode()}
        user_data = {'ulid': 1, 'type': 'access_token'}
        access_token = create_access_token(data=user_data)
      
        return CreateAccessToken(access_token=access_token)


class CreateRefreshToken(graphene.Mutation):
    refresh_token = graphene.String()

    @staticmethod
    def mutate(root, info):
        data = {'token_type': 'refresh_token'}
