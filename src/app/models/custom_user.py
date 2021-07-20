from database.database import Base, engine
from sqlalchemy import Column, String
from sqlalchemy.orm import relationship


# PostgreSQLがデフォルトでuserテーブルを作成してしまうため、名前を見やすくCustomとつける
class CustomUserModel(Base):
    __tablename__ = "custom_users"
    __table_args__ = {'extend_existing': True}
    ulid = Column(String, primary_key=True, unique=True)
    username = Column(String(255))
    email = Column(String(255), unique=True)
    password = Column(String)
    full_name = Column(String(255))
    tasks = relationship('TaskModel')
    refresh_token = relationship('RefreshTokenModel')
