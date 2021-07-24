# TODO: ログインチェックのデコレーターを作成する
def validate_access_token(function):
    def validate(*args, **kwargs):
        # アクセストークン（JWT）が存在するか、デコードして有効期限内かチェック
        print('デコレーター')
        result = function(*args, **kwargs)
        return result

    return validate


# ↓サンプル
def args_logger(f):
    def wrapper(*args, **kwargs):
        f(*args, **kwargs)
        print('args: {}, kwargs: {}'.format(args, kwargs))

    return wrapper


@args_logger
def print_message(msg):
    print(msg)


# 以下と等価
'''
def print_message(msg):
    print(msg)
print_message = args_logger(print_message)
'''

# print_message('hello')
# ↓結果
# hello
# args: ('hello',), kwargs: {}
