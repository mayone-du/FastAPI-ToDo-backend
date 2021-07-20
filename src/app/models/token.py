from database.database import Base
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func


# リフレッシュトークンのみDBに保存する
class RefreshTokenModel(Base):
    __tablename__ = "refresh_tokens"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    # TODO: one-to-oneの関係にできるようにする
    token_holder = Column(String, ForeignKey('custom_users.ulid'))
    # ランダムに生成した文字列をトークンの内容とする
    body = Column(String(255))
    # expiration_date = Column(String())
