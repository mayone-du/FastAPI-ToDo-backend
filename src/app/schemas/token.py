import graphene
from app.models.user import UserModel
from app.schemas.user import UserNode
from auth.auth import (create_access_token, get_password_hash, hash_password,
                       verify_password)


class CreateToken(graphene.Mutation):
    class Arguments:
        email = graphene.String(required=True)
        password = graphene.String(required=True)

    access_token = graphene.String()

    # アクセストークン作成時にemailとpasswordを受け取り、そのユーザーのULIDをもとにJWTを発行
    @staticmethod
    def mutate(root, info, **kwargs):
        email = kwargs.get('email')
        hashed_password = UserNode.get_query(info).filter(UserModel.email==email).first().password
        print(hashed_password)

        # パスワードが一致するか検証
        boolean = verify_password(kwargs.get('password'), hashed_password)
        print(boolean)
        # ulid = UserNode.get_query(info).filter(UserModel.email==email).filter(UserModel.password==hashed_password).first().id
        # ulid = UserNode.get_query(info).filter(UserModel.email==email, UserModel.password==hashed_password).first().id
        # print(ulid)
        # ulidとusernameをもとにJWTを発行
        # user_data = {'ulid': kwargs.get('ulid'), 'password': hash_password(kwargs.get('password')).decode()}
        user_data = {'ulid': kwargs.get('ulid'), 'type': 'access_token'}
        access_token = create_access_token(data=user_data)
      
        return CreateToken(access_token=access_token)


class CreateRefreshToken(graphene.Mutation):
    refresh_token = graphene.String()

    @staticmethod
    def mutate(root, info):
        data = {'token_type': 'refresh_token'}
