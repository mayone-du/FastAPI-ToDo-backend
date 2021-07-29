from database.database import Base
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func


class TaskModel(Base):
    __tablename__ = "tasks"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, autoincrement=True)
    # タスクを作成したユーザー
    task_creator_ulid = Column(String, ForeignKey('custom_users.ulid'), nullable=False)
    # task_creator = relationship('CustomUserModel', primaryjoin='CustomUserModel.ulid == foreign(TaskModel.id)',)
    # task_creator = relationship('CustomUserModel', back_populates='tasks')
    # task_creator = relationship('CustomUserModel')

    title = Column(String(255), nullable=False)
    content = Column(String(255), nullable=False, default='')
    is_done = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
