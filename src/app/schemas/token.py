import graphene
from auth.auth import create_access_token, hash_password


class CreateToken(graphene.Mutation):
    class Arguments:
        email = graphene.String(required=True)
        password = graphene.String(required=True)

    access_token = graphene.String()

    @staticmethod
    def mutate(root, info, **kwargs):
        # emailとusernameをもとにJWTを発行
        user_data = {'email': kwargs.get('email'), 'password': hash_password(kwargs.get('password')).decode()}
        access_token = create_access_token(data=user_data)
      
        return CreateToken(access_token=access_token)
