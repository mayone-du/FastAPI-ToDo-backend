def validate_access_token(function):
    def validate(*args, **kwargs):
        print('デコレーター')
        result = function(*args, **kwargs)
        return result

    return validate
