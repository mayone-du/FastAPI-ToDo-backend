from database.database import Base, engine
from sqlalchemy import Boolean, Column, String
from sqlalchemy.orm import relationship

# relationshipのためにimport
from .task import TaskModel
from .token import RefreshTokenModel


# PostgreSQLがデフォルトでuserテーブルを作成してしまうため、名前を見やすくCustomとつける
class CustomUserModel(Base):
    __tablename__ = "custom_users"
    __table_args__ = {'extend_existing': True}
    ulid = Column(String, primary_key=True, unique=True)
    username = Column(String(255))
    email = Column(String(255), unique=True)
    password = Column(String)
    full_name = Column(String(255))
    # 本人確認確認フラグ マジックリンクをクリックしたらTrueに更新する
    is_proof = Column(Boolean, nullable=False, default=False)
    tasks = relationship('TaskModel')
    refresh_token = relationship('RefreshTokenModel')
