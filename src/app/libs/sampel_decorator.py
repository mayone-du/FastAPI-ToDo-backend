# TODO: ログインチェックのデコレーターを作成する
def validate_access_token(function):
    def validate(*args, **kwargs):
        # アクセストークン（JWT）が存在するか、デコードして有効期限内かチェック
        print('デコレーター')
        result = function(*args, **kwargs)
        return result

    return validate
