import graphene
from auth.auth import create_access_token


class CreateToken(graphene.Mutation):
    class Arguments:
        email = graphene.String(required=True)
        username = graphene.String(required=True)

    access_token = graphene.String()

    @staticmethod
    def mutate(root, info, **kwargs):
        # emailとusernameをもとにJWTを発行
        user_data = {'email': kwargs.get('email'), 'username': kwargs.get('username')}
        access_token = create_access_token(data=user_data)
      
        return CreateToken(access_token=access_token)
