from app.database import Base


def init():
    print('initialization...')
    Base.create_all()


init()
