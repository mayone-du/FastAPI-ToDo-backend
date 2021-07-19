from datetime import datetime, timedelta

import graphene
from app.models.user import UserModel
from app.schemas.user import UserNode
from auth.auth import verify_password
from fastapi import HTTPException
from jose import JWTError, jwt
from settings.envs import ACCESS_TOKEN_EXPIRE_MINUTES, ALGORITHM, SECRET_KEY


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
        # emailからそのユーザーのインスタンスを取得
        user =  UserNode.get_query(info).filter(UserModel.email==input_email).first()
        # 登録済みのハッシュ化されたパスワード
        registered_password = user.password
        ulid = user.ulid
        print(ulid)
        #TODO: パスワードが一致するか検証
        if verify_password(input_password, registered_password):
            print('ok')
        else:
            print('out! password is no-match')
            raise HTTPException(status_code=401)

        # ulid、トークンタイプ、有効期限をもとにJWTを発行
        token_data = {
                        'ulid': ulid,
                        # access_token or refresh_token
                        'type': 'access_token', 
                        # 有効期限をUTCタイムスタンプ形式で設定
                        'exp': datetime.utcnow() + timedelta(minutes=int(ACCESS_TOKEN_EXPIRE_MINUTES))
                    }
        access_token = jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)
        return CreateAccessToken(access_token=access_token)


class CreateRefreshToken(graphene.Mutation):
    refresh_token = graphene.String()

    @staticmethod
    def mutate(root, info):
        ulid = ''
        data = {
                    'ulid': ulid ,
                    'token_type': 'refresh_token',
                    'exp': datetime.utcnow() + timedelta(days=7)
                }
        refresh_token = jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)
        return CreateRefreshToken(refresh_token=refresh_token)
