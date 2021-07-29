from database.database import Base
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
    username = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password = Column(String, nullable=False)
    full_name = Column(String(255))
    # 本人確認確認フラグ マジックリンクをクリックしたらTrueに更新する
    is_verified = Column(Boolean, nullable=False)
    # tasks = relationship('TaskModel', primaryjoin='CustomUserModel.ulid == foreign(TaskModel.id)') 
    # tasks = relationship('TaskModel', backref=backref('tasks', uselist=True, cascade='delete,all'))
    # tasks = relationship('TaskModel', back_populates='custom_users')
    # tasks = relationship('TaskModel', backref='custom_users')
    tasks = relationship('TaskModel')
    # refresh_token = relationship('RefreshTokenModel')
