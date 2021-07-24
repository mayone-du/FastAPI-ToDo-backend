from datetime import datetime

from jose import jwt

from app.models.custom_user import CustomUserModel
from app.schemas.custom_user import CustomUserNode
from settings.envs import ALGORITHM, SECRET_KEY


# TODO: ログインチェックのデコレーターを作成する
def login_required(function):
    def validate(root, info, **kwargs):
        # アクセストークン（JWT）が存在するか、デコードして有効期限内かチェック
        headers = dict(info.context['request']['headers'])
        # Bearer の文字列を半角空白含めて削除（計7文字）
        token = headers[b'authorization'].decode()[7:]
        # トークンの内容を取得
        payload: dict = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        # ulidに紐づくユーザーがいなかったらエラー
        user = CustomUserNode.get_query(info).filter(
            CustomUserModel.ulid == payload.get('ulid')).first()
        if user is None:
            raise
        # トークンタイプがaccess_tokenじゃなかったらエラー（トークンに持たせるpayloadについては要検討）
        if payload.get('token_tyep') != 'access_token':
            raise
        # 有効期限が過ぎていたらエラー処理
        if datetime.utcnow() > payload.get('exp'):
            raise
        result = function(root, info, **kwargs)
        return result

    return validate
