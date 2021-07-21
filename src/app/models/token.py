from uuid import UUID

from database.database import Base
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func


# リフレッシュトークンのみDBに保存する
class RefreshTokenModel(Base):
    __tablename__ = "refresh_tokens"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    # TODO: one-to-oneの関係にできるようにする
    token_holder = Column(String, ForeignKey('custom_users.ulid'))
    # UUIDをアプリケーション側で作成し保存する
    # TODO: Stringで保存ではなくUUIDで保存する
    body = Column(String)
    expiration_date = Column(DateTime(timezone=True))
