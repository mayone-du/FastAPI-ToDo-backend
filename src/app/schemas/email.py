import graphene
from fastapi_mail import FastMail, MessageSchema
from libs.auth import create_access_token, verify_hash_data
from settings.envs import MAIL_CONFIGS


# マジックリンクを送信
class SendMagicLinkEmail(graphene.Mutation):
    class Arguments:
        email = graphene.String(required=True)
        password = graphene.String(required=True)

    ok = graphene.Boolean()

    @staticmethod
    def mutate(root, info, **kwargs):
        try:
            # アクセストークンを作成
            # TODO: リファクタ（関数名がややこしい。内部でユーザーが存在するかの検証まで行っている。）
            access_token_object: dict = create_access_token(info, email=kwargs.get('email'), password=kwargs.get('password'))
            # バックグラウンドタスクで非優先的に、同期的にメールを送信
            background = info.context["background"]
            email_body = f'''
                <h1>本登録のご案内</h1>
                <p><br><a href="https://google.com">こちらのリンク</a>
                をクリックすると本登録が完了します。有効期限は30分です。</p>
                <p><a href="https://mayoblog.vercel.app/search/results?keyword={access_token_object.get('access_token')}">Link</a></p>
            '''
            message = MessageSchema(
                subject='Webアプリ 本登録のご案内',
                recipients=[kwargs.get('email')],
                body=email_body,
                subtype='html',
            )
            fm = FastMail(MAIL_CONFIGS)
            background.add_task(fm.send_message, message)
            ok=True
            return SendMagicLinkEmail(ok=ok)
        except: 
            raise

