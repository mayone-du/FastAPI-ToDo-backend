
from database.database import Base
from sqlalchemy import Boolean, Column, DateTime, Integer, String
from sqlalchemy.sql import func


# リフレッシュトークンのみDBに保存する
class RefreshTokenModel(Base):
    __tablename__ = "refresh_token"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    #TODO: 所持者のユーザーIDと紐付ける

    # ランダムに生成した文字列をトークンの内容とする
    body = Column(String(255))
    # expiration_date = Column(String())
