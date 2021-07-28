from datetime import datetime

from fastapi_mail import FastMail, MessageSchema
from settings.envs import MAIL_CONFIGS

from libs.auth import (create_access_token, create_access_token_exp,
                       get_current_custom_user)


def send_magic_link_email(
    info,
    email,
):
    try:
        user = get_current_custom_user(info)
        # アクセストークンを作成
        payload = {
            'ulid': user.ulid,
            'iat': datetime.utcnow(),
            'exp': create_access_token_exp
        }
        access_token = create_access_token(payload)
        background = info.context["background"]
        email_body = f'''
                <h1>本登録のご案内</h1>
                <p><br><a href="https://sample.vercel.app/auth?token={access_token}">こちらのリンク</a>
                をクリックすると本登録が完了します。有効期限は30分です。</p>
                <p><a href="https://mayoblog.vercel.app/search/results?keyword={access_token}">Link</a></p>
            '''
        message = MessageSchema(
            subject='Webアプリ 本登録のご案内',
            recipients=[email],
            body=email_body,
            subtype='html',
        )
        fm = FastMail(MAIL_CONFIGS)
        # バックグラウンドタスクで非優先的に、同期的にメールを送信
        background.add_task(fm.send_message, message)
        return True
    except:
        raise
