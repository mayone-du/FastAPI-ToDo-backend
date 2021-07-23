from database.database import Base
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func


# リフレッシュトークンのみDBに保存する
class RefreshTokenModel(Base):
    __tablename__ = "refresh_tokens"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, autoincrement=True, unique=True, nullable=False, primary_key=True)
    # UUIDをアプリケーション側で作成し保存する
    uuid = Column(UUID(as_uuid=True), unique=True, nullable=False)
    # TODO: one-to-oneの関係にできるようにする
    # TODO: 逆参照できるようにする
    token_holder = Column(String, ForeignKey('custom_users.ulid'), nullable=False, unique=True)
    expiration_date = Column(DateTime(timezone=True), nullable=False)
