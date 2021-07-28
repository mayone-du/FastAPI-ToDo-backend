from datetime import datetime

from fastapi.exceptions import HTTPException
from jose import jwt
from models.custom_user import CustomUserModel
from schemas.custom_user import CustomUserNode
from settings.envs import ALGORITHM, SECRET_KEY


# アクセストークンを検証してログインが有効かどうかをチェックする
def login_required(function):
    def validate(root, info, **kwargs):
        try:
            # def validate(*args):
            # アクセストークン（JWT）が存在するか、デコードして有効期限内かチェック
            headers = dict(info.context['request']['headers'])
            # Bearer の文字列を半角空白含めて削除（計7文字）
            token = headers[b'authorization'].decode()[7:]
            # トークンの内容を取得
            payload: dict = jwt.decode(token,
                                       SECRET_KEY,
                                       algorithms=[ALGORITHM])
            # ulidに紐づくユーザーがいなかったらエラー
            user: CustomUserModel = CustomUserNode.get_query(info).filter(
                CustomUserModel.ulid == payload.get('ulid')).first()
            if user is None:
                raise HTTPException(status_code=400, detail="ユーザーいませｎ")
            # 本人確認がされているかの確認
            if not user.is_verified:
                raise HTTPException(status_code=400, detail="本人確認がまだです。")
            # 有効期限が過ぎていたらエラー処理
            if datetime.utcnow().timestamp() > payload.get('exp'):
                raise HTTPException(status_code=400, detail="有効期限が切れています。")
            result = function(root, info, **kwargs)
            return result
        except:
            raise HTTPException(status_code=400,
                                detail="トークン検証中に何らかのエラーが発生しました。")

    return validate
