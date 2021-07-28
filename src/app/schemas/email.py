import graphene
from fastapi_mail import FastMail, MessageSchema
from libs.send_emai import send_magic_link_email
from settings.envs import MAIL_CONFIGS


# マジックリンクを送信（ユーザー作成時に送ったメールの有効期限が切れた場合に再度送信する用）
class SendMagicLinkEmail(graphene.Mutation):
    class Arguments:
        email = graphene.String(required=True)
        password = graphene.String(required=True)

    ok = graphene.Boolean()

    @staticmethod
    def mutate(root, info, **kwargs):
        try:
            # 内部でアクセストークンの作成まで行なっている
            ok=send_magic_link_email(info, kwargs.get('email'))
            return SendMagicLinkEmail(ok=ok)
        except: 
            raise

